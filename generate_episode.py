#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Automation - Daily Episode Generator
Pipeline: LLM script -> Chinese-animation-style images -> edge-tts voiceover
          -> 1024x576 video (Ken Burns + subtitles) -> YouTube upload -> Drive backup
Run locally (test):  DRY_RUN=1 python generate_episode.py
Run in CI:           private run first, then set UPLOAD=1
"""
import os, sys, json, csv, time, random, base64, asyncio, subprocess
import urllib.request, urllib.parse
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
WORK = ROOT / "work"
STATE_FILE = ROOT / "state" / "episodes.json"
EPISODES_CSV = ROOT / os.environ.get("EPISODES_CSV", "episodes_100.csv")
TOKEN_PATH = ROOT / "token.json"
PLAYLIST_ID = os.environ.get("PLAYLIST_ID", "").strip()  # optional override: if set, uses this playlist for ALL episodes
PLAYLIST_TITLE_CN = os.environ.get("PLAYLIST_TITLE_CN", "Chinese Animation Recaps").strip()
PLAYLIST_TITLE_JP = os.environ.get("PLAYLIST_TITLE_JP", "Japanese 2D Anime Recaps").strip()
STYLE = os.environ.get("STYLE", "japanese").strip().lower()
WORK.mkdir(exist_ok=True)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()
OPENROUTER_MODEL   = os.environ.get("OPENROUTER_MODEL", "nvidia/nemotron-3-ultra-550b-a55b:free")
CF_ACCOUNT_ID      = os.environ.get("CF_ACCOUNT_ID", "").strip()
CF_API_TOKEN       = os.environ.get("CF_API_TOKEN", "").strip()
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
] ]
VOICE              = os.environ.get("TTS_VOICE", "en-IN-NeerjaExpressiveNeural")
TTS_RATE           = os.environ.get("TTS_RATE", "-12%")  # slower, contemplative dramatic pace
PRIVACY_STATUS     = os.environ.get("PRIVACY_STATUS", "private")  # safe default; set public when confident
UPLOAD             = os.environ.get("UPLOAD", "1") == "1"
DRY_RUN            = os.environ.get("DRY_RUN", "0") == "1"
EPISODE_OVERRIDE   = os.environ.get("EPISODE_INDEX", "").strip()  # force a specific episode id

W, H, FPS = 1024, 576, 25
N_IMAGES = 20  # CF FLUX schnell; spaced ~5s apart to stay inside free-tier burst rate
MIN_WORDS = 5000  # floor for narration; -12% TTS speaks ~112 wpm, so 5000 words ~ 45 min video

# ---------------------------------------------------------------- helpers

def log(*a):
    print(f"[{datetime.now():%H:%M:%S}]", *a, flush=True)

def load_episode():
    rows = list(csv.DictReader(open(EPISODES_CSV, encoding="utf-8")))
    assert rows, "episodes.csv empty"
    if EPISODE_OVERRIDE:
        row = next((r for r in rows if r["id"] == EPISODE_OVERRIDE), None)
        if not row:
            sys.exit(f"EPISODE_INDEX {EPISODE_OVERRIDE} not found in episodes.csv")
        return row
    state = json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {"next_id": rows[0]["id"], "done": []}
    row = next((r for r in rows if r["id"] == state.get("next_id")), rows[0])
    return row

def mark_done(ep_id):
    state = json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {"next_id": None, "done": []}
    done = state.get("done", [])
    if ep_id not in done:
        done.append(ep_id)
    rows = list(csv.DictReader(open(EPISODES_CSV, encoding="utf-8")))
    ids = [r["id"] for r in rows]
    nxt = ids[(ids.index(ep_id) + 1) % len(ids)]  # cycle
    STATE_FILE.write_text(json.dumps({"next_id": nxt, "done": done}, indent=2, ensure_ascii=False))
    log(f"state -> next episode id = {nxt}")

# ---------------------------------------------------------------- 1. script

def _call_llm_once(model, sys_prompt, user_prompt):
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "system", "content": sys_prompt},
                     {"role": "user", "content": user_prompt}],
        "temperature": 0.9,
        "max_tokens": 13500,
        "reasoning": {"enabled": False},
    }).encode()

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload, method="POST",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/NO-NAME7861/youtube-automation",
            "X-Title": "YouTube Automation",
        })
    with urllib.request.urlopen(req, timeout=240) as r:
        resp = json.loads(r.read())

    content = None
    try:
        content = resp["choices"][0]["message"]["content"]
    except Exception:
        raise RuntimeError("unexpected LLM payload: " + json.dumps(resp)[:1500])
    if not content:
        raise RuntimeError("empty content: " + json.dumps(resp)[:1500])

    content = content.strip()
    start = content.find("{")
    if start == -1:
        raise RuntimeError("no JSON in reply: " + content[:1500])
    # robust extraction: raw_decode (eats trailing garbage) + escape lone backslashes
    import re as _re
    decoder = json.JSONDecoder(strict=False)
    payload = content[start:]
    try:
        obj, _ = decoder.raw_decode(payload)
        return obj
    except Exception:
        fixed = _re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', payload)
        try:
            obj, _ = decoder.raw_decode(fixed)
            return obj
        except Exception:
            end = payload.rfind("}")
            if end <= 0:
                raise RuntimeError("no JSON in reply: " + content[:1500])
            return json.loads(fixed[:fixed.rfind("}") + 1], strict=False)

def _generate_once(sys_prompt, user_prompt):
    """Try every model (OpenRouter free tier) up to 3 attempts each; return parsed JSON."""
    models = [OPENROUTER_MODEL] + [m for m in FALLBACK_MODELS if m != OPENROUTER_MODEL]
    failures = []
    for model in models:
        for attempt in range(3):
            try:
                ep = _call_llm_once(model, sys_prompt, user_prompt)
                log(f"LLM OK via {model} (attempt {attempt + 1})")
                return ep
            except Exception as e:
                log(f"model {model} attempt {attempt + 1} failed: {e}")
                failures.append(f"{model}: {e}")
                time.sleep(20)
    sys.exit("All LLM models failed:\n" + "\n\n".join(failures))

def call_llm(row):
    track = (row.get("track") or STYLE or "japanese").strip().lower()
    if track == "chinese" or STYLE == "chinese":
        style_req = "Chinese-animation (xianxia/wuxia) style"
        thumbnail_desc = "Chinese-animation (xianxia/wuxia) style"
        recap_label = "Chinese Animation Recap"
        sys_topic = "Chinese animation recap"
    else:
        style_req = "Japanese 2D anime style (modern shoujo/shonen, studio-quality cel shading)"
        thumbnail_desc = "Japanese 2D anime style (modern shoujo/shonen)"
        recap_label = "Japanese 2D Anime Recap"
        sys_topic = "Japanese 2D anime recap"
    sys_prompt = (
        f"You are a veteran YouTube scriptwriter for the '{sys_topic}' niche. "
        f"You write vivid, original retellings in that style and ALWAYS end with a clear moral. "
        "Reply ONLY with valid JSON, no markdown fences."
    )
    user_prompt = f"""Write one complete episode in this exact JSON shape:
{{
 "title": "concise YouTube title WITH STRONG HOOK at the start, max 70 chars; put the keyword + 'Chinese Animation Recap' or 'Japanese 2D Anime Recap' at the END of the title. Use concrete, vivid, meme-y hooks like: 'Underdog Who X'd To Y' / 'Broke Carpenter Outfoxed The Demon King' / 'Weak Cultivator Refused Heaven's Throne' / 'Merchant Who Fed A Plague City'. NEVER academic-sounding titles like 'The Poisoned Heir Surviving'. Always write as If Netflix show title; MORAL in brackets optional",
 "description": "2-3 sentences hook + 1 line moral + line: This video features AI-generated visuals and AI narration. + subscribe CTA, max 1000 chars",
 "tags": ["max 15 tags"],
 "moral": "one sentence",
 "narration": "5500-6500 words continuous narration, written in a Roman Urdu + English + Hindi mixed style (native-written Roman Urdu sentences with English/Hindi verb phrases - like popular Pakistani YouTube storytelling: 'agar aap ne suno to...', 'wo larki sach mein hero ban gyi'). Suited for one warm female voice. Devanagari script NOT used. ABSOLUTE MINIMUM 5200 words, NEVER fewer. Structure it in 14-18 scenes with slow pacing, dramatic peaks, quiet contemplation, and emotional beats. Every scene should land emotionally. MUST end with the explicit moral.",
 "image_prompts": ["20 SHORT prompts, each: {style_req}, cinematic, dramatic lighting, <scene description>"],
 "thumbnail_prompt": "one dramatic prompt for a 16:9 thumbnail in {thumbnail_desc}"
}}

Episode brief (topic + moral):
Title seed: {row['topic']}
Moral: {row['moral']}"""

    ep = _generate_once(sys_prompt, user_prompt)

    # Enforce the length floor: free models routinely under-deliver. Re-ask to expand.
    words = len((ep.get("narration") or "").split())
    for attempt in range(2):
        if words >= MIN_WORDS:
            break
        log(f"narration only {words} words (< {MIN_WORDS}); asking model to expand (pass {attempt + 1})")
        expand_prompt = user_prompt + (
            f"\n\nIMPORTANT: Your previous draft had only {words} words of narration. "
            f"Rewrite the COMPLETE episode JSON. The narration MUST be AT LEAST {MIN_WORDS + 500} words "
            "(aim 5500-6200). Expand every scene: sensory detail, character interiority, dialogue, "
            "quiet beats, rising tension. Do NOT summarize. Do NOT shorten any scene."
        )
        try:
            ep2 = _generate_once(sys_prompt, expand_prompt)
        except SystemExit as e:
            log(f"expansion pass failed ({e}); keeping previous narration")
            break
        w2 = len((ep2.get("narration") or "").split())
        log(f"expansion pass {attempt + 1}: {w2} words")
        if w2 > words:
            ep, words = ep2, w2
    if words < MIN_WORDS:
        log(f"WARNING: narration still only {words} words after retries - video will be shorter than 40 min")
    return ep

# ---------------------------------------------------------------- 2. images

def make_synthetic_image(dest, idx):
    """Quota-proof fallback: FFmpeg-only moody xianxia gradient + noise, no network, no API.
    Guarantees a full video even when CF Workers AI is 429-ing and Pollinations is down."""
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

def _cf_image(prompt, dest, seed):
    import base64
    payload = json.dumps({"prompt": prompt}).encode()
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/@cf/black-forest-labs/flux-1-schnell",
        data=payload, method="POST",
        headers={"Authorization": f"Bearer {CF_API_TOKEN}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        resp = json.loads(r.read())
    img_b64 = resp.get("result", {}).get("image")
    if not img_b64:
        raise RuntimeError("CF AI failed: " + json.dumps(resp)[:500])
    dest.write_bytes(base64.b64decode(img_b64))
    return True

def _pollinations_image(prompt, dest, seed):
    url = ("https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt)
           + f"?width={W}&height={H}&nologo=true&seed={seed}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=180) as r:
        data = r.read()
    if len(data) <= 20_000:
        raise RuntimeError(f"pollinations too small: {len(data)} bytes")
    dest.write_bytes(data)
    return True

def gen_image(prompt, dest, seed):
    """CF FLUX first (if env has creds), Pollinations second (fast fail), else False.
    Backoff removed: Pollinations is currently 402/503-dead and CF 429s are daily-quota errors -
    neither is fixed by sleeping. The caller fills missing images with synthetic gradients."""
    if CF_ACCOUNT_ID and CF_API_TOKEN:
        try:
            _cf_image(prompt, dest, seed)
            return True
        except Exception as e:
            log(f"cf failed: {str(e)[:80]}")
    try:
        _pollinations_image(prompt, dest, seed)
        return True
    except Exception as e:
        log(f"pollinations failed: {str(e)[:60]}")
    return False

# ---------------------------------------------------------------- 3. voice

def run_tts(text_file, mp3, srt):
    cmd = [sys.executable, "edge_tts_shim.py", "--file", str(text_file),
           "--write-media", str(mp3), "--write-subtitles", str(srt),
           "--voice", VOICE, f"--rate={TTS_RATE}"]
    subprocess.run(cmd, check=True)

def media_duration(path):
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)]).decode().strip()
    return float(out)

# ---------------------------------------------------------------- 4. video

KZ_IN  = "z='min(zoom+0.0011,1.18)'"          # zoom in
KZ_OUT = "z='if(eq(on,1),1.18,max(1.001,zoom-0.0016))'"  # zoom out

def make_segment(img, seg, d, zoom_in):
    frames = max(int(d * FPS), FPS)
    z = KZ_IN if zoom_in else KZ_OUT
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
          f"zoompan={z}:d={frames}:s={W}x{H}:fps={FPS},"
          f"eq=brightness=0.0,format=yuv420p")
    cmd = ["ffmpeg", "-y", "-loop", "1", "-i", str(img), "-t", f"{d:.3f}",
           "-vf", vf, "-r", str(FPS), "-c:v", "libx264", "-preset", "ultrafast",
           "-crf", "27", str(seg)]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def mix_narration_with_bgm(audio):
    """Mix narration with looping epic ambient BGM at low volume."""
    bgm = ROOT / "assets" / "music" / "epic_ambient.mp3"
    if not bgm.exists():
        log("BGM missing - skipping mix")
        return audio
    dur = media_duration(audio)
    mixed = WORK / "narration_mix.mp3"
    fade_end = max(0.1, dur - 6)
    subprocess.run([
        "ffmpeg", "-y", "-stream_loop", "-1", "-i", str(bgm), "-i", str(audio),
        "-filter_complex",
        f"[1:a]volume=1.0[n];[0:a]volume=0.40,"
        f"afade=t=in:st=0:d=6,afade=t=out:st={fade_end:.2f}:d=6[m];"
        f"[n][m]amix=inputs=2:duration=first:dropout_transition=2,"
        f"loudnorm[a]",
        "-map", "[a]", "-c:a", "libmp3lame", "-q:a", "3", str(mixed)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log("BGM mixed with narration (volume 0.40 = 40% + loudnorm)")
    return mixed

def build_video(image_paths, audio, srt, out_mp4, thumb):
    audio = mix_narration_with_bgm(audio)
    total = media_duration(audio)
    per = total / len(image_paths)
    segs = []
    for i, img in enumerate(image_paths):
        seg = WORK / f"seg_{i:02d}.mp4"
        make_segment(img, seg, per, zoom_in=(i % 2 == 0))
        segs.append(seg)
        log(f"segment {i + 1}/{len(image_paths)} done ({per:.1f}s)")

    list_file = WORK / "concat.txt"
    list_file.write_text("\n".join(f"file '{s.as_posix()}'" for s in segs))
    concat = WORK / "concat.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
                    "-c", "copy", str(concat)], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    sub_style = ("FontName=Noto Sans Devanagari,FontSize=16,Bold=-1,PrimaryColour=&H00FFFFFF,"
                 "OutlineColour=&H00000000,BorderStyle=4,Outline=2,Shadow=0,MarginV=22")
    subprocess.run(["ffmpeg", "-y", "-i", str(concat), "-i", str(audio),
                    "-vf", f"subtitles={srt.as_posix()}:force_style='{sub_style}'",
                    "-c:v", "libx264", "-preset", "ultrafast", "-crf", "26",
                    "-c:a", "aac", "-b:a", "128k", "-shortest", str(out_mp4)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log("video ready:", out_mp4)

# ---------------------------------------------------------------- 5. upload

def youtube_upload(ep, mp4, thumbnail):
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
              "https://www.googleapis.com/auth/youtube"]
    if not TOKEN_PATH.exists():
        sys.exit("token.json missing - run get_token.py first")
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)

    default_desc = ep["description"].rstrip()
    footer = (
        "\n\n- Motion Draft Studio\n\n"
        "?? Subscribe for daily recaps\n"
        "?? Chinese animation & Japanese 2D anime stories in English narration\n\n"
        "?? Recommended reads this week (affiliate):\n"
        "  * RE:ZERO - Re:Zero Light Novel Volume 1 on Amazon - https://www.amazon.com/?tag=motiondraft-20\n"
        "  * Frieren: Beyond Journey's End - Vol 1 - https://www.amazon.com/?tag=motiondraft-20\n"
        "  * Mushoku Tensei - Isekai Anthology - https://www.amazon.com/?tag=motiondraft-20\n"
        "  * The Eminence in Shadow - Vol 1 - https://www.amazon.com/?tag=motiondraft-20\n\n"
        "?? This video contains AI-generated visuals and an AI-generated voiceover.\n\n"
        "Playlist: https://www.youtube.com/playlist?list=PLJ8DOidoftZM\n\n"
        "#ChineseAnimationRecap #Japanese2DAnimeRecap #MotionDraftStudio #AnimationRecap #NovelRecap"
    )
    full_desc = (default_desc + footer)[:5000]

    body = {
        "snippet": {
            "title": ep["title"][:100],
            "description": full_desc,
            "tags": ep.get("tags", [])[:15],
            "categoryId": "24",  # Entertainment
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": PRIVACY_STATUS,
            "selfDeclaredMadeForKids": False,
        },
    }
    media = MediaFileUpload(str(mp4), chunksize=16 * 1024 * 1024, resumable=True,
                            mimetype="video/mp4")
    log("uploading to YouTube ...")
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            log(f"upload {int(status.progress() * 100)}%")
    vid = resp["id"]
    log(f"uploaded: https://youtu.be/{vid}")

    if thumbnail and Path(thumbnail).exists():
        try:
            yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(thumbnail))).execute()
            log("thumbnail set")
        except Exception as e:
            log("thumbnail set skipped (channel likely lacks custom thumbnail permission):", e)
    return vid

def drive_backup(mp4):
    # Optional: needs token_drive.json (separate token, Drive scope only -
    # Google forbids mixing YouTube and Drive scopes in one consent)
    drive_token = ROOT / "token_drive.json"
    if not drive_token.exists():
        log("drive backup skipped - token_drive.json not present (optional)")
        return
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    SCOPES = ["https://www.googleapis.com/auth/drive.file"]
    creds = Credentials.from_authorized_user_file(str(drive_token), SCOPES)
    drive = build("drive", "v3", credentials=creds, cache_discovery=False)
    q = "name='YouTubeAutomation' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    folders = drive.files().list(q=q, fields="files(id)").execute().get("files", [])
    if folders:
        fid = folders[0]["id"]
    else:
        fid = drive.files().create(body={"name": "YouTubeAutomation",
                                          "mimeType": "application/vnd.google-apps.folder"},
                                    fields="id").execute()["id"]
    drive.files().create(body={"name": Path(mp4).name, "parents": [fid]},
                         media_body=MediaFileUpload(str(mp4)),
                         fields="id").execute()
    log("backed up to Google Drive /YouTubeAutomation")

# ---------------------------------------------------------------- playlist

def playlist_for(track):
    """Return the playlist ID for given track ("chinese" or "japanese"), creating it if missing."""
    if PLAYLIST_ID:
        return PLAYLIST_ID
    title = PLAYLIST_TITLE_CN if track == "chinese" else PLAYLIST_TITLE_JP
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
              "https://www.googleapis.com/auth/youtube"]
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
    try:
        # find existing by listing mine
        resp = yt.playlists().list(part="snippet", mine=True, maxResults=50).execute()
        for item in resp.get("items", []):
            if item["snippet"]["title"] == title:
                return item["id"]
        # create if missing
        desc = ("Chinese animation (xianxia/wuxia) recap series. "
                if track == "chinese"
                else "Japanese 2D anime recap series. ")
        desc += "AI-generated visuals and voiceover. One moral in every episode."
        p = yt.playlists().insert(part="snippet,status",
            body={"snippet": {"title": title, "description": desc, "defaultLanguage": "en"},
                  "status": {"privacyStatus": "public"}}).execute()
        log(f"created playlist: {title} -> {p['id']}")
        return p["id"]
    except Exception as e:
        log("WARNING: playlist lookup failed:", e)
        return None

def add_to_playlist(video_id, track):
    pid = playlist_for(track or "japanese")
    if not pid:
        log("no playlist id - skipping playlist add")
        return
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
              "https://www.googleapis.com/auth/youtube"]
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
    try:
        yt.playlistItems().insert(part="snippet",
            body={"snippet": {"playlistId": pid,
                              "resourceId": {"kind": "youtube#video", "videoId": video_id}}}).execute()
        log(f"added to playlist {pid} ({'chinese' if track == 'chinese' else 'japanese'})")
    except Exception as e:
        log("playlist add failed (non-fatal):", e)

# ---------------------------------------------------------------- main

def main():
    if not OPENROUTER_API_KEY:
        sys.exit("OPENROUTER_API_KEY not set")

    row = load_episode()
    log(f"episode: {row['id']} | {row['topic']}")

    ep = call_llm(row)
    log("LLM wrote:", ep["title"])
    (WORK / "episode.json").write_text(json.dumps(ep, indent=2, ensure_ascii=False))

    narration = ep["narration"]
    (WORK / "narration.txt").write_text(narration, encoding="utf-8")
    log(f"narration words: {len(narration.split())}")

    STYLE_EFFECTIVE = (row.get("track") or STYLE or "japanese").strip().lower()
    image_suffix = (", chinese animation style, xianxia, cinematic lighting, highly detailed"
                    if STYLE_EFFECTIVE == "chinese"
                    else ", Japanese 2D anime style, cinematic lighting, highly detailed")

    prompts = ep["image_prompts"][:N_IMAGES]
    image_paths = []
    seed0 = random.randint(1000, 999999)
    for i, p in enumerate(prompts):
        dest = WORK / f"img_{i:02d}.png"
        if gen_image(p + image_suffix, dest, seed0 + i):
            image_paths.append(dest)
        time.sleep(2)
    # Quoteoma apocalypse safety net: fill the remainder with synthetic gradients
    if len(image_paths) < N_IMAGES:
        log(f"only {len(image_paths)} real images - filling the rest with synthetic gradients")
        for j in range(N_IMAGES - len(image_paths)):
            synth = WORK / f"img_syn_{j:02d}.png"
            if make_synthetic_image(synth, len(image_paths) + j):
                image_paths.append(synth)
    if not image_paths:
        sys.exit("no images at all - aborting")

    mp3, srt = WORK / "narration.mp3", WORK / "narration.srt"
    run_tts(WORK / "narration.txt", mp3, srt)

    thumb = WORK / "thumb.png"
    gen_image(ep.get("thumbnail_prompt", prompts[0]) + (", chinese animation style, dramatic, cinematic" if STYLE_EFFECTIVE == "chinese" else ", Japanese 2D anime style, dramatic, cinematic"), thumb, seed0 + 999)

    out_mp4 = WORK / f"episode_{row['id']}.mp4"
    build_video(image_paths, mp3, srt, out_mp4, thumb)

    if DRY_RUN or not UPLOAD:
        log("DRY_RUN/UPLOAD=0 - skipping upload. Video at:", out_mp4)
        return

    vid = youtube_upload(ep, out_mp4, thumb)
    track = (row.get("track") or STYLE or "japanese").strip().lower()
    add_to_playlist(vid, track)
    try:
        drive_backup(out_mp4)
    except Exception as e:
        log("drive backup failed (non-fatal):", e)
    mark_done(row["id"])
    log("done -> https://youtu.be/" + vid)

if __name__ == "__main__":
    main()

