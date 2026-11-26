"""
build_explainer.py - Anime novel EXPLAINER episodes.

Targets ~2-hour episodes for the Re:Zero / Solo Leveling series.
Each episode = 4 parts, each part ~4,500 words (Devanagari Hindi + English mix),
all concatenated into one full-length explainer video.

Run: EPISODE_ID=R001 python build_explainer.py
CI:  in mega_explainer.yml (daily 00:30 UTC via GitHub Actions)
"""
import os, sys, json, subprocess, random, time, urllib.request, urllib.parse, re
from pathlib import Path

ROOT = Path(__file__).parent
WORK = ROOT / "explainer-work"
WORK.mkdir(exist_ok=True)
OUT  = ROOT / "explainer-out"
OUT.mkdir(exist_ok=True)

W, H, FPS = 1280, 720, 25
N_IMAGES   = int(os.environ.get("N_IMAGES", "32"))
SERIES        = os.environ.get("EXPLAINER_SERIES", "RE:ZERO")
SKIP_LLM      = os.environ.get("EXPLAINER_SKIP_LLM", "0") == "1"
SALVAGE_FILE  = os.environ.get("EXPLAINER_SALVAGE_FILE", "").strip()
CUSTOM_TITLE  = os.environ.get("EXPLAINER_TITLE", "").strip()
TARGET_PARTS = int(os.environ.get("EXPLAINER_PARTS", "6"))
APPROX_WORDS_PER_PART = int(os.environ.get("WORDS_PER_PART", "5000"))
VOICE = os.environ.get("TTS_VOICE", "en-IN-NeerjaExpressiveNeural")
RATE  = os.environ.get("TTS_RATE", "+22%")  # valid edge-tts rate format (+22% English / +0% Romanized Hindi-Urdu); was '150%' -> INVALID -> gTTS fallback -> robot voice
EPISODE_ID = os.environ.get("EPISODE_ID", "R001")
EPISODES_CSV = os.environ.get("EPISODES_CSV", "episodes_rezero.csv")

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()
OPENROUTER_MODEL   = os.environ.get("OPENROUTER_MODEL", "nvidia/nemotron-3-ultra-550b-a55b:free")
FALLBACK_MODELS    = [m for m in [
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "nvidia/nemotron-3.5-lightning:free",
    "baidu/ernie-5.5-flash-preview:free",
    "inclusionai/ling-3.2-flash:free",
    "recursive/flint-v1.0:free",
    "particle-ai/particle-1:free",
    "dots-studio/dots-3-note-preview:free",
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "nvidia/nemotron-3.5-super-vl:free",
]]
CF_ID    = os.environ.get("CF_ACCOUNT_ID", "").strip()
CF_TOKEN = os.environ.get("CF_API_TOKEN", "").strip()
TOKEN_PATH = ROOT / "token.json"

BGM = ROOT / "assets" / "music" / "epic_ambient.mp3"

from mega_variants import VARIANTS  # reusing the variant prompt helpers not mandatory


def log(*a):
    print(f"[{__import__('datetime').datetime.now():%H:%M:%S}]", *a, flush=True)

def load_episode():
    import csv
    for row in csv.DictReader(open(EPISODES_CSV, encoding="utf-8")):
        if row["id"] == EPISODE_ID:
            return row
    sys.exit(f"EPISODE_ID {EPISODE_ID} not found in {EPISODES_CSV}")

def _call_llm_once(model, system_prompt, user_prompt):
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "system", "content": system_prompt},
                     {"role": "user", "content": user_prompt}],
        "temperature": 0.9,
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
    start, end = content.find("{"), content.rfind("}")
    return json.loads(content[start:end + 1])

def cf_image(prompt, dest, seed):
    """CF FLUX -> Pollinations fallback -> synthetic gradient."""
    if CF_ID and CF_TOKEN:
        try:
            payload = json.dumps({"prompt": prompt}).encode()
            req = urllib.request.Request(
                f"https://api.cloudflare.com/client/v4/accounts/{CF_ID}/ai/run/@cf/black-forest-labs/flux-1-schnell",
                data=payload, method="POST",
                headers={"Authorization": f"Bearer {CF_TOKEN}",
                         "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=120) as r:
                resp = json.loads(r.read())
            img = resp.get("result", {}).get("image")
            if img:
                import base64
                Path(dest).write_bytes(base64.b64decode(img))
                log(f"[ok] image {Path(dest).name}")
                return True
        except Exception as e:
            log(f"cf fail: {str(e)[:60]}")
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
        log(f"pollinations fail: {str(e)[:60]}")
    return False

def make_synthetic_image(dest, idx):
    # High-contrast, vibrant palettes with subtle motion and film grain.
    palettes = [("0x0d1b2a", "0x1a3a5c", "0x7f004f"), ("0x1b140c", "0x3b4a0b", "0xd4a500"),
                ("0x2c001e", "0x5a0a3d", "0xbc005a"), ("0x0f2027", "0x1e3a5f", "0x4d9656"),
                ("0x0d1117", "0x2d1b4e", "0x8ca6a0"), ("0x141e30", "0x273b4e", "0x4d9656"),
                ("0x001f3a", "0x0095d5", "0xf4cece"), ("0x14153c", "0x263e66", "0x8fbc9f"),
                ("0x3a404d", "0x5a5a6e", "0xc5c5c5"), ("0x2d3436", "0x4f4f56", "0xdddddd"),
                ("0x264653", "0x2a9d8f", "0xe9c46a"), ("0xf4a261", "0xe76f51", "0xffad4a")]
    c0, c1, c2 = palettes[idx % len(palettes)]
    vf = f"gradients=s={W}x{H}:nb_colors=3:c0={c0}:c1={c1}:c2={c2}:speed=0.05,noise=alls=10:allf=t,vignette=PI/3.5"
    r = subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", vf,
                        "-frames:v", "1", "-q:v", "1", str(dest)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return r.returncode == 0 and Path(dest).exists() and Path(dest).stat().st_size > 5000

def call_part(part_idx: int, total_parts: int, row: dict) -> str:
    sys_prompt = (
        "You are a veteran YouTube scriptwriter in the style of Deniz / Shey Anime recaps, targeting Indian audiences. "
        f"You write {SERIES} deep-arc explainers in Devanagari Hindi + English mix. Every sentence pulls the viewer forward. "
        "You never copyright-quote scenes verbatim; you explain, dramatize, and analyse. "
        "Write ONLY JSON line with key 'narration'. No markdown, no extra commentary."
    )
    approx_hours = round(APPROX_WORDS_PER_PART * total_parts * 0.427 / 3600, 1)
    user_prompt = f"""Write PART {part_idx} of {total_parts} of a roughly {approx_hours}-hour long explanation of "{row['topic']}".

Structure of remaining video:
  Part 1: Hook ΓÇö the curling facts about the arc. Skip nothing. Add suspense AND stakes.
  Part 2: The cast ΓÇö every named character, their role, their wound.
  Part 3-{{total_parts - 1}}: Beat-by-beat retelling of the arc's chronology with commentary. In-between lines that break the fourth wall.
  Part {total_parts}: The author's message & a grin-worthy conclusion. End with the moral, explicitly and clearly.

Requirements:
- ~{APPROX_WORDS_PER_PART} words. ABSOLUTE MINIMUM {int(APPROX_WORDS_PER_PART * 0.85)} words. Do not write less.
- Devanagari Hindi + English technical words (like 'death loop', 'witch', 'temporal freeze', 'decision-fatigued').
- No double quotes or backslashes inside text ΓÇö use Hindi quotes πÇî πÇì or single quotes.
- Keep building the story; reference Part 1's hook but do NOT repeat content from previous parts.
- Natural spoken pace: long monologues by the narrator, with line-break-separated "commentary".
- End with a specific cliffhanger line unless this is the final part (then end with the moral).
- Reply with ONLY JSON: {{"narration": "..."}}
"""
    models = [OPENROUTER_MODEL] + [m for m in FALLBACK_MODELS if m != OPENROUTER_MODEL]
    for model in models:
        for attempt in range(3):
            try:
                ep = _call_llm_once(model, sys_prompt, user_prompt)
                nar = ep.get("narration", "")
                wc = len(nar.split())
                log(f"  part {part_idx} via {model} (att {attempt + 1}): {wc} words")
                if wc >= int(APPROX_WORDS_PER_PART * 0.5):
                    return nar
                log("  too short, retry")
            except Exception as e:
                log(f"  part {part_idx} {model} att {attempt + 1} fail: {str(e)[:60]}")
                time.sleep(15)
    sys.exit(f"part {part_idx} failed across all models")

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
                    "-crf", "18", str(seg)],  # high quality
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def mix_bgm(audio):
    if not BGM.exists():
        log("BGM missing ΓÇö plain narration")
        return audio
    dur = media_duration(audio)
    mixed = WORK / "narration_mix.mp3"
    fade_end = max(0.1, dur - 8)
    subprocess.run([
        "ffmpeg", "-y", "-stream_loop", "-1", "-i", str(BGM), "-i", str(audio),
        "-filter_complex",
        f"[1:a]volume=1.0[n];[0:a]volume=0.42,"
        f"afade=t=in:st=0:d=8,afade=t=out:st={fade_end:.2f}:d=8[m];"
        f"[n][m]amix=inputs=2:duration=first:dropout_transition=2,loudnorm[a]",
        "-map", "[a]", "-c:a", "libmp3lame", "-q:a", "3", str(mixed)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log("BGM mixed + loudnorm")
    return mixed


def main():
    row = load_episode()
    total = TARGET_PARTS
    if SKIP_LLM and SALVAGE_FILE:
        narration = Path(SALVAGE_FILE).read_text(encoding="utf-8")
        txt = WORK / "narration.txt"
        txt.write_text(narration, encoding="utf-8")
        log(f"SALVAGE mode: {len(narration.split())} words from {SALVAGE_FILE}")
    else:
        if not OPENROUTER_API_KEY:
            sys.exit("OPENROUTER_API_KEY not set")
        parts = []
        for i in range(1, total + 1):
            parts.append(call_part(i, total, row))
        narration = "\n\n".join(p.strip() for p in parts)
        txt = WORK / "narration.txt"
        txt.write_text(narration, encoding="utf-8")
        log(f"TOTAL narration: {len(narration.split())} words (target ~{APPROX_WORDS_PER_PART*total})")

    seed0 = random.randint(1000, 999999)
    image_paths = []
    _sl = SERIES.lower()
    art_style = ("chinese animation, xianxia fantasy, cinematic cel art, ancient throne room, dark dramatic tone"
                 if any(k in _sl for k in ("betrayal", "chinese", "xianxia"))
                 else "japanese 2D anime style, dark dramatic tone, cinematic")
    for i in range(N_IMAGES):
        dest = WORK / f"img_{i:02d}.png"
        prompt = f"{SERIES}: {row['topic'][:120]} scene {i+1}, {art_style}, no text"
        if cf_image(prompt, dest, seed0 + i):
            image_paths.append(dest)
        elif make_synthetic_image(dest, i):
            image_paths.append(dest)
        time.sleep(0.6)
    if len(image_paths) < 10:
        sys.exit(f"only {len(image_paths)} images - aborting")
    seed0 = seed0 + 1000

    mp3, srt = WORK / "narration.mp3", WORK / "narration.srt"
    subprocess.run([sys.executable, "edge_tts_shim.py",
                    "--file", str(txt), "--write-media", str(mp3),
                    "--write-subtitles", str(srt),
                    "--voice", VOICE, f"--rate={RATE}"], check=True)
    log(f"TTS done: {media_duration(mp3):.1f}s")

    mixed = mix_bgm(mp3)
    total_dur = media_duration(mixed)
    per = total_dur / len(image_paths)
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

    # No subtitle burn-in; captions can be added in Studio later.
    # Motion graphics: light-streak sweep, drifting sigil ring, rising chevrons,
    # letterbox bars, film grain ΓÇö same style as the viral T-series teasers.
    out_mp4 = OUT / f"explainer_{EPISODE_ID}.mp4"
    try:
        from make_teasers import make_streak, make_ring, make_chevrons
        mg = WORK / "mg_assets"; mg.mkdir(exist_ok=True)
        streak = mg / "streak.png"; ring = mg / "ring.png"; chev = mg / "chevrons.png"
        if not streak.exists():
            make_streak(streak)
        if not ring.exists():
            make_ring(ring)
        if not chev.exists():
            make_chevrons(chev)
        fc = (f"[0:v]drawbox=x=0:y=0:w={W}:h=44:color=black:t=fill,"
              f"drawbox=x=0:y={H-40}:w={W}:h=40:color=black:t=fill[lb];"
              f"[1:v]scale=760:-1[streak];"
              f"[lb][streak]overlay=x='mod(t*150,1240)-230':y='88+32*sin(t*0.8)':format=auto[s1];"
              f"[2:v]scale=170:170[ring];"
              f"[s1][ring]overlay=x='{W//2-85}+58*sin(t*1.15)':y='288-85+46*cos(t*0.95)':format=auto[s2];"
              f"[3:v]split=2[ch1][ch2];[ch1]scale=140:140[chevA];[ch2]scale=140:140[chevB];"
              f"[s2][chevA]overlay=x='34+26*sin(t*0.75)':y='{H}-mod(t*150,{H+260})':format=auto[s3];"
              f"[s3][chevB]overlay=x='{W-174}-26*sin(t*0.75)':y='{H}-mod(t*150+260,{H+260})':format=auto[s4];"
              f"[s4]noise=alls=4:allf=t,vignette=PI/4.6,format=yuv420p[vout];"
              f"[4:a]loudnorm[aout]")
        subprocess.run(["ffmpeg", "-y", "-i", str(concat),
                        "-stream_loop", "-1", "-i", str(streak),
                        "-stream_loop", "-1", "-i", str(ring),
                        "-stream_loop", "-1", "-i", str(chev),
                        "-i", str(mixed),
                        "-filter_complex", fc,
                        "-map", "[vout]", "-map", "[aout]",
                        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-shortest", str(out_mp4)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log("MG rendered:", out_mp4)
    except Exception as e:
        log("MG failed, falling back to plain concat:", str(e)[:120])
        subprocess.run(["ffmpeg", "-y", "-i", str(concat), "-i", str(mixed),
                        "-map", "0:v:0", "-map", "1:a:0",
                        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
                        "-c:a", "aac", "-b:a", "128k", "-shortest", str(out_mp4)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log("video ready:", out_mp4)

    # Upload
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    creds = Credentials.from_authorized_user_file(
        str(TOKEN_PATH), ["https://www.googleapis.com/auth/youtube.upload",
                          "https://www.googleapis.com/auth/youtube"])
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
    thumb = None
    thumb_dest = WORK / "thumb.png"
    custom_thumb = os.environ.get("THUMB_FILE", "").strip()
    if custom_thumb and Path(custom_thumb).exists():
        thumb = Path(custom_thumb)
        log("using custom thumbnail:", custom_thumb)
    else:
        cf_image(f"{SERIES} thumb {row['topic']}, dramatic, blood red art, no text",
                 thumb_dest, seed0 + 999)
        if thumb_dest.exists():
            thumb = thumb_dest
    if CUSTOM_TITLE:
        title = CUSTOM_TITLE
    else:
        title = f"{SERIES} Explained - {row['arc']} | Complete Arc Hindi Recap by Motion-Draft Studio"
    title = title[:100]
    desc = (f"{SERIES} explained in Hindi ΓÇö Arc: {row['arc']}\n\n"
            "Deep recap: every character, every decision, every twist.\n\n"
            "ΓÜá∩╕Å This video features AI-generated visuals and AI narration.\n\n"
            "Subscribe for weekly anime + novel explainers: https://www.youtube.com/@MotionDraftStudio\n\n"
            f"#{SERIES.replace(' ', '').replace(':', '')} #MotionDraftStudio #HindiAnimeRecap")
    tags = list(dict.fromkeys([SERIES.lower(), SERIES.lower() + " explained",
                               SERIES.lower() + " hindi", "anime recap hindi",
                               "motion draft studio", "explained", "long recap",
                               "sung jinwoo"]))
    body = {
        "snippet": {"title": title, "description": desc, "tags": tags,
                    "categoryId": "24", "defaultLanguage": "hi"},
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
    }
    media = MediaFileUpload(str(out_mp4), chunksize=16 * 1024 * 1024, resumable=True)
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
    print("EXPLAINER_URL=https://youtu.be/" + vid)

if __name__ == "__main__":
    main()
