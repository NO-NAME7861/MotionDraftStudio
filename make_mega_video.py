"""
make_mega_video.py - the 2+ HOUR Devanagari-Hindi "Betrayal -> Silent Thriller King" mega recap.
Improved Long Dialogue Mode: 7 part-LLM calls (continuity via beats + previous-part tail),
Hindi (Devanagari) + English mixed narration, hi-IN-SwaraNeural voice, 32 images, BGM.

Runs inside GitHub Actions (mega.yml). Also runnable locally:  python make_mega_video.py
"""
import os, sys, json, subprocess, random, time, urllib.request, urllib.parse, re
from pathlib import Path

ROOT = Path(__file__).parent
WORK = ROOT / "mega-work"
WORK.mkdir(parents=True, exist_ok=True)
OUT  = ROOT / "mega-out"
OUT.mkdir(parents=True, exist_ok=True)

W, H, FPS = 1024, 576, 25
VOICE = "hi-IN-SwaraNeural"
RATE  = "-2%"
N_IMAGES = 32
MEGA_VARIANT = os.environ.get("MEGA_VARIANT", "M001")
EPISODE_ID = MEGA_VARIANT

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()
OPENROUTER_MODEL   = os.environ.get("OPENROUTER_MODEL", "nvidia/nemotron-3-ultra-550b-a55b:free")
# nemotron-ultra is the reliable free model right now - Gemma free models are persistently 429 at peak quota hours
FALLBACK_MODELS    = [m for m in [
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "nvidia/nemotron-3.5-lightning:free",
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
]]
CF_ID    = os.environ.get("CF_ACCOUNT_ID", "")
CF_TOKEN = os.environ.get("CF_API_TOKEN", "")
TOKEN_PATH = ROOT / "token.json"

# ------------------------------------------------------------------ story
from mega_variants import VARIANTS
C = VARIANTS.get(MEGA_VARIANT, VARIANTS["M001"])
TITLE = C["TITLE"]
MORAL = C["MORAL"]
CONTEXT = C["CONTEXT"]
PARTS = C["PARTS"]
DESCRIPTION = C["DESCRIPTION"]
TAGS = C["TAGS"]
IMAGE_PROMPTS = C["IMAGE_PROMPTS"]
THUMB_PROMPT = C["THUMB_PROMPT"]

PART_PROMPT_TMPL = """Write भाग {part} of 7 of the Devanagari-Hindi mega recap script.

CONTEXT OF THE FULL STORY (do not repeat previous parts; continue exactly):
{context}

THIS PART ({part} of 7) - {slug}:
{beat}

Requirements:
- DEEP narration in Devanagari Hindi mixed with ENGLISH technical words (like 'betrayal', 'strategy', 'hidden ledger', 'auction', 'system') - exactly the Hindi-English mix Indians love.
- NEVER use double quotes or backslashes inside the narration text. Use Hindi quotes 「 」 or single quotes ' for dialogue instead - keep valid JSON.
- Target 2100-2400 words. DO NOT write less than 2000 words. Slow pace, heavy suspense.
- Natural spoken style for one voice. Long, flowing sentences mixed with punchy short ones.
- Include dialogue (use Hindi quote style), inner monologue, sensory detail (rain, lantern light, heartbeat, paper, metal).
- Keep tension of a thriller: silence, glances, recorded evidence, courtroom verdicts, rain, crowd pulse.
- End part {part} on a cliffhanger hook (unless part 7 - then end with the explicit moral).
- No headings, no notes, no markdown. Just narration text.

Return ONLY JSON: {{"part": {part}, "narration": "..."}}"""


# ------------------------------------------------------------------ helpers
def log(*a):
    print(f"[{__import__('datetime').datetime.now():%H:%M:%S}]", *a, flush=True)

def extract_json(text):
    """Robustly pull the first JSON object out of an LLM reply (Devanagari-safe)."""
    decoder = json.JSONDecoder(strict=False)
    m = re.search(r"\{", text)
    if not m:
        raise RuntimeError("no JSON in reply: " + text[:1500])
    start = m.start()
    payload = text[start:]
    # 1) plain raw_decode (handles trailing garbage)
    try:
        obj, _ = decoder.raw_decode(payload)
        return obj
    except Exception:
        pass
    # 2) escape lone backslashes (LLMs love illegal \ sequences in Hindi prose)
    fixed = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', payload)
    try:
        obj, _ = decoder.raw_decode(fixed)
        return obj
    except Exception:
        pass
    # 3) first { ... last } sliced, strict=False, escape-fixed
    end = payload.rfind("}")
    if end > 0:
        return json.loads(fixed[: fixed.rfind("}") + 1], strict=False)
    raise RuntimeError("no JSON parse possible: " + text[:1500])

def _call_llm(model, label, user_prompt):
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "system", "content":
                       "You are a veteran Hindi YouTube scriptwriter for animation recaps (Hindi-English mix). Reply ONLY with valid JSON, no markdown."},
                      {"role": "user", "content": user_prompt}],
        "temperature": 0.85,
        "max_tokens": 11000,
        "reasoning": {"enabled": False},
    }).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload, method="POST",
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}",
                 "Content-Type": "application/json",
                 "HTTP-Referer": "https://github.com/NO-NAME7861/youtube-automation",
                 "X-Title": "YouTube Automation"})
    with urllib.request.urlopen(req, timeout=300) as r:
        resp = json.loads(r.read())
    content = resp["choices"][0]["message"]["content"].strip()
    return extract_json(content)

def call_part(part_idx):
    meta = PARTS[part_idx - 1]
    prompt = PART_PROMPT_TMPL.format(part=part_idx, slug=meta["slug"], beat=meta["beat"], context=CONTEXT)
    return _generate(prompt, label=f"part {part_idx}", min_words=1600, floor_accept=400)

def _generate(prompt, label, min_words=1600, floor_accept=700):
    """Try models; keep the BEST partial response. Only hard-fail if literally nothing came back."""
    best, best_len = "", 0
    for model in [OPENROUTER_MODEL] + [m for m in FALLBACK_MODELS if m != OPENROUTER_MODEL]:
        for attempt in range(3):
            try:
                ep = _call_llm(model, label, prompt)
                nar = ep.get("narration", "")
                wc = len(nar.split())
                log(f"{label} via {model} (attempt {attempt+1}): {wc} words")
                if wc > best_len:
                    best, best_len = nar, wc
                if wc >= min_words:
                    return nar
                log(f"{label} too short vs target {min_words}, trying again ...")
            except Exception as ex:
                log(f"{label} {model} attempt {attempt+1} failed: {ex}")
                time.sleep(25)
    if best_len >= floor_accept:
        log(f"{label}: accepting best effort {best_len} words (models under-deliver today)")
        return best
    sys.exit(f"{label} failed on all models - nothing usable returned")

def make_synthetic_image(dest, idx):
    """Quota-proof fallback: FFmpeg-only moody gradient + noise."""
    palettes = [
        ("0x1a0f2e", "0x4a2c5a", "0xc94f32"),
        ("0x0f1d3d", "0x274060", "0x4a8f8f"),
        ("0x241424", "0x45224a", "0xe0a526"),
        ("0x081c2b", "0x1c3d4a", "0x3fa7a0"),
        ("0x1b1122", "0x3d1f3f", "0xc95e5e"),
    ]
    c0, c1, c2 = palettes[idx % len(palettes)]
    vf = (f"gradients=s={W}x{H}:nb_colors=3:c0={c0}:c1={c1}:c2={c2}:speed=0.0,"
          f"noise=alls=8:allf=t,vignette=PI/4.8")
    r = subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", vf,
                        "-frames:v", "1", "-q:v", "2", str(dest)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if r.returncode == 0 and Path(dest).exists() and Path(dest).stat().st_size > 2000:
        log("synthetic gradient image:", Path(dest).name)
        return True
    return False

def cf_image(prompt, dest, seed):
    """CF FLUX schnell -> Pollinations fallback (same as create_shorts)."""
    payload = json.dumps({"prompt": prompt}).encode()
    if CF_ID and CF_TOKEN:
        try:
            req = urllib.request.Request(
                f"https://api.cloudflare.com/client/v4/accounts/{CF_ID}/ai/run/@cf/black-forest-labs/flux-1-schnell",
                data=payload, method="POST",
                headers={"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=120) as r:
                resp = json.loads(r.read())
            img_b64 = resp.get("result", {}).get("image")
            if img_b64:
                import base64
                Path(dest).write_bytes(base64.b64decode(img_b64))
                log(f"[ok] cf image {Path(dest).name}")
                return True
        except Exception as e:
            log(f"cf fail: {e}")
    try:
        url = ("https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt)
               + f"?width={W}&height={H}&nologo=true&seed={seed}")
        req2 = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req2, timeout=120) as r:
            data = r.read()
        if len(data) > 15000:
            Path(dest).write_bytes(data)
            log(f"[ok-p] pollinations {Path(dest).name}")
            return True
    except Exception as e:
        log(f"pollinations fail: {e}")
    return False

def media_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout.strip()
    return float(out)

KZ_IN  = "z='min(zoom+0.0011,1.18)'"
KZ_OUT = "z='if(eq(on,1),1.18,max(1.001,zoom-0.0016))'"

def make_segment(img, seg, d, zoom_in):
    frames = max(int(d * FPS), FPS)
    z = KZ_IN if zoom_in else KZ_OUT
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
          f"zoompan={z}:d={frames}:s={W}x{H}:fps={FPS},format=yuv420p")
    subprocess.run(["ffmpeg", "-y", "-loop", "1", "-i", str(img), "-t", f"{d:.3f}",
                    "-vf", vf, "-r", str(FPS), "-c:v", "libx264", "-preset", "ultrafast",
                    "-crf", "27", str(seg)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def mix_bgm(audio):
    bgm = ROOT / "assets" / "music" / "epic_ambient.mp3"
    if not bgm.exists():
        log("BGM missing - skipping mix")
        return audio
    dur = media_duration(audio)
    mixed = WORK / "narration_mix.mp3"
    fade_end = max(0.1, dur - 8)
    subprocess.run([
        "ffmpeg", "-y", "-stream_loop", "-1", "-i", str(bgm), "-i", str(audio),
        "-filter_complex",
        f"[1:a]volume=1.0[n];[0:a]volume=0.42,"
        f"afade=t=in:st=0:d=8,afade=t=out:st={fade_end:.2f}:d=8[m];"
        f"[n][m]amix=inputs=2:duration=first:dropout_transition=2,loudnorm[a]",
        "-map", "[a]", "-c:a", "libmp3lame", "-q:a", "3", str(mixed)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log("BGM mixed (0.42) + loudnorm")
    return mixed


# ------------------------------------------------------------------ main
def main():
    if not OPENROUTER_API_KEY:
        sys.exit("OPENROUTER_API_KEY not set")

    log(f"=== MEGA: {EPISODE_ID} | 7 parts Devanagari ===")
    if os.environ.get("MEGA_SKIP_LLM") == "1":
        log("MEGA_SKIP_LLM=1 - loading salvaged narration, zero LLM calls")
        narration = Path("mega-salvage/narration.txt").read_text(encoding="utf-8")
        total_words = len(narration.split())
        log(f"salvaged narration: {total_words} words")
    else:
        parts = []
        for i in range(1, 8):
            parts.append(call_part(i))
        narration = "\n\n".join(p.strip() for p in parts)
        total_words = len(narration.split())
        log(f"TOTAL narration: {total_words} words (~{total_words / 100:.0f} min @100wpm Hindi)")

    # -------- Extension loop: guarantee the final video is >= 2 hours --------
    for ext in range(4):
        Path(WORK / "narration.txt").write_text(narration, encoding="utf-8")
        mp3_probe, srt_probe = WORK / "narration.mp3", WORK / "narration.srt"
        subprocess.run([sys.executable, "-m", "edge_tts",
                        "--file", str(WORK / "narration.txt"), "--write-media", str(mp3_probe),
                        "--write-subtitles", str(srt_probe),
                        "--voice", VOICE, f"--rate={RATE}"], check=True)
        dur = media_duration(mp3_probe)
        total_words = len(narration.split())
        log(f"TTS pass {ext}: {dur:.1f}s ({dur/60:.1f} min), {total_words} words")
        if dur >= 7200:
            break
        tail = " ".join(narration.split()[-700:])
        ext_prompt = f"""You previously wrote a 7-part mega recap titled '{TITLE}' (Devanagari Hindi + English mix).
Story context: {CONTEXT}
The story currently ENDS with this final paragraph:
...{tail}

Now you MUST extend the same story WITHOUT repeating previous scenes: write a deep-dive epilogue interlude of 2300-2800 words:
- The night before the storm trial (flashback, sensory suspense)
- What happened to the city between parts (compressed progression scenes with suspense)
- The day AFTER the Hidden Throne falls (the silence, the empty throne, one last lantern)
- Then restate the moral EXPLICITLY and powerfully (last line is the moral)
- Same style: Devanagari Hindi mixed with English technical words. NO double quotes, NO backslashes inside dialogue. Hindi quotes 「 」 or single quotes only.
- Never summarize. Keep pace slow, tension high, absolutely no scenes from before the current ending.

Return ONLY JSON: {{"part": 8, "narration": "..."}}"""
        extra = _generate(ext_prompt, f"extension {ext + 1}", min_words=2000, floor_accept=800)
        narration = narration.rstrip() + "\n\n" + extra.strip()
        total_words = len(narration.split())
        log(f"after extension: {total_words} words")
    else:
        log("WARNING: after 4 extensions video is still under 2h")

    log("=== IMAGES (32) ===")
    image_paths, seed0 = [], random.randint(1000, 999999)
    for i, p in enumerate(IMAGE_PROMPTS):
        dest = WORK / f"img_{i:02d}.png"
        if cf_image(p, dest, seed0 + i):
            image_paths.append(dest)
        time.sleep(1)
    if len(image_paths) < N_IMAGES:
        log(f"only {len(image_paths)} real images - filling with synthetic gradients")
        for j in range(N_IMAGES - len(image_paths)):
            synth = WORK / f"img_syn_{j:02d}.png"
            if make_synthetic_image(synth, len(image_paths) + j):
                image_paths.append(synth)
    if not image_paths:
        sys.exit("no images at all - aborting")

    log("=== THUMB ===")
    thumb_dest = WORK / "thumb.png"
    thumb = thumb_dest if cf_image(THUMB_PROMPT, thumb_dest, seed0 + 999) else None

    # TTS already produced/validated by the extension loop above (narration.txt tracked it)
    txt = WORK / "narration.txt"
    mp3, srt = WORK / "narration.mp3", WORK / "narration.srt"
    log(f"=== continuing with validated TTS: {media_duration(mp3):.1f}s ===")

    log("=== RENDER ===")
    mixed = mix_bgm(mp3)
    total = media_duration(mixed)
    per = total / len(image_paths)
    segs = []
    for i, img in enumerate(image_paths):
        seg = WORK / f"seg_{i:02d}.mp4"
        make_segment(img, seg, per, zoom_in=(i % 2 == 0))
        segs.append(seg)
        log(f"segment {i + 1}/{len(image_paths)} ({per:.1f}s)")

    list_file = WORK / "concat.txt"
    list_file.write_text("\n".join(f"file '{s.as_posix()}'" for s in segs))
    concat = WORK / "concat.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
                    "-c", "copy", str(concat)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    sub_style = ("FontName=Noto Sans Devanagari,FontSize=17,Bold=-1,"
                 "PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=4,Outline=2,Shadow=0,MarginV=24")
    out_mp4 = OUT / f"mega_{EPISODE_ID}.mp4"
    subprocess.run(["ffmpeg", "-y", "-i", str(concat), "-i", str(mixed),
                    "-vf", f"subtitles={srt.as_posix()}:force_style='{sub_style}'",
                    "-c:v", "libx264", "-preset", "ultrafast", "-crf", "27",
                    "-c:a", "aac", "-b:a", "128k", "-shortest", str(out_mp4)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log("video ready:", out_mp4)

    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    creds = Credentials.from_authorized_user_file(
        str(TOKEN_PATH), ["https://www.googleapis.com/auth/youtube.upload",
                          "https://www.googleapis.com/auth/youtube"])
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
    body = {
        "snippet": {"title": TITLE, "description": DESCRIPTION, "tags": TAGS,
                    "categoryId": "24", "defaultLanguage": "hi"},
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
    }
    media = MediaFileUpload(str(out_mp4), chunksize=16 * 1024 * 1024,
                            resumable=True, mimetype="video/mp4")
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            log(f"upload {int(status.progress() * 100)}%")
    vid = resp["id"]
    log(f"uploaded: https://youtu.be/{vid}")

    if thumb:
        try:
            yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(thumb))).execute()
            log("thumbnail set")
        except Exception as e:
            log("thumbnail skipped:", e)

    # add to Chinese Animation Recaps playlist
    try:
        yt.playlistItems().insert(part="snippet",
            body={"snippet": {"playlistId": "PLJ8DOidoftZM",
                               "resourceId": {"kind": "youtube#video", "videoId": vid}}}).execute()
        log("added to CN playlist")
    except Exception as e:
        log("playlist add failed:", e)
    print("MEGA_URL=https://youtu.be/" + vid)

if __name__ == "__main__":
    main()
