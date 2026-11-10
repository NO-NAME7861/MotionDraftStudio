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
EPISODES_CSV = ROOT / os.environ.get("EPISODES_CSV", "episodes.csv")
TOKEN_PATH = ROOT / "token.json"
PLAYLIST_ID = os.environ.get("PLAYLIST_ID", "PLfE9RY2EzLWE").strip()
STYLE = os.environ.get("STYLE", "japanese").strip().lower()
WORK.mkdir(exist_ok=True)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()
OPENROUTER_MODEL   = os.environ.get("OPENROUTER_MODEL", "google/gemma-4-31b-it:free")
CF_ACCOUNT_ID      = os.environ.get("CF_ACCOUNT_ID", "").strip()
CF_API_TOKEN       = os.environ.get("CF_API_TOKEN", "").strip()
FALLBACK_MODELS    = [m for m in [
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "nvidia/nemotron-3.5-lightning:free",
] ]
VOICE              = os.environ.get("TTS_VOICE", "en-US-JennyNeural")
TTS_RATE           = os.environ.get("TTS_RATE", "-5%")
PRIVACY_STATUS     = os.environ.get("PRIVACY_STATUS", "private")  # safe default; set public when confident
UPLOAD             = os.environ.get("UPLOAD", "1") == "1"
DRY_RUN            = os.environ.get("DRY_RUN", "0") == "1"
EPISODE_OVERRIDE   = os.environ.get("EPISODE_INDEX", "").strip()  # force a specific episode id

W, H, FPS = 1024, 576, 25
N_IMAGES = 12  # ~1 image per 60-75s for a 10-15 min episode

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

def _call_llm_once(model, row, sys_prompt, user_prompt):
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "system", "content": sys_prompt},
                     {"role": "user", "content": user_prompt}],
        "temperature": 0.9,
        "max_tokens": 7000,
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
    start, end = content.find("{"), content.rfind("}")
    if start == -1 or end == -1:
        raise RuntimeError("no JSON in reply: " + content[:1500])
    return json.loads(content[start:end + 1])

def call_llm(row):
    if STYLE == "chinese":
        style_req = "Chinese-animation (xianxia/wuxia) style"
        thumbnail_desc = "Chinese-animation (xianxia/wuxia) style"
        recap_label = "Chinese Animation Recap"
    else:
        style_req = "Japanese 2D anime style (modern shoujo/shonen, studio-quality cel shading)"
        thumbnail_desc = "Japanese 2D anime style (modern shoujo/shonen)"
        recap_label = "Japanese 2D Anime Recap"
    sys_prompt = (
        f"You are a veteran YouTube scriptwriter for the '{'Chinese' if STYLE == 'chinese' else 'Japanese 2D anime'} animation recap' niche. "
        f"You write vivid, original retellings in that style and ALWAYS end with a clear moral. "
        "Reply ONLY with valid JSON, no markdown fences."
    )
    user_prompt = f"""Write one complete episode in this exact JSON shape:
{{
 "title": "concise YouTube title, max 70 chars, include '{recap_label}' and the episode's moral in brackets",
 "description": "2-3 sentences hook + 1 line moral + line: This video features AI-generated visuals and AI narration. + subscribe CTA, max 1000 chars",
 "tags": ["max 15 tags"],
 "moral": "one sentence",
 "narration": "1200-1600 words continuous narration, natural spoken English, vivid, dramatic, easy for one voice to read. MUST end with the explicit moral.",
 "image_prompts": ["12 SHORT prompts, each: {style_req}, cinematic, dramatic lighting, <scene description>"],
 "thumbnail_prompt": "one dramatic prompt for a 16:9 thumbnail in {thumbnail_desc}"
}}

Episode brief (topic + moral):
Title seed: {row['topic']}
Moral: {row['moral']}"""

    models = [OPENROUTER_MODEL] + [m for m in FALLBACK_MODELS if m != OPENROUTER_MODEL]
    failures = []
    for model in models:
        for attempt in range(3):
            try:
                ep = _call_llm_once(model, row, sys_prompt, user_prompt)
                log(f"LLM OK via {model} (attempt {attempt + 1})")
                return ep
            except Exception as e:
                log(f"model {model} attempt {attempt + 1} failed: {e}")
                failures.append(f"{model}: {e}")
                time.sleep(20)
    sys.exit("All LLM models failed:\n" + "\n\n".join(failures))

# ---------------------------------------------------------------- 2. images

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
    for attempt in range(3):
        try:
            if CF_ACCOUNT_ID and CF_API_TOKEN:
                return _cf_image(prompt, dest, seed)
            return _pollinations_image(prompt, dest, seed)
        except Exception as e:
            log(f"image retry {attempt + 1}/3: {e}")
            time.sleep(4)
    log("WARNING: image failed after retries:", prompt[:60])
    return False

# ---------------------------------------------------------------- 3. voice

def run_tts(text_file, mp3, srt):
    cmd = [sys.executable, "-m", "edge_tts", "--file", str(text_file),
           "--write-media", str(mp3), "--write-subtitles", str(srt),
           "--voice", VOICE, f"--rate={TTS_RATE}"]
    subprocess.run(cmd, check=True)

def media_duration(path):
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)]).decode().strip()
    return float(out)

# ---------------------------------------------------------------- 4. video

KZ_IN  = "z='min(zoom+0.0007,1.18)'"          # zoom in
KZ_OUT = "z='if(eq(on,1),1.18,max(1.001,zoom-0.0009))'"  # zoom out

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

def build_video(image_paths, audio, srt, out_mp4, thumb):
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

    sub_style = ("FontName=Arial,FontSize=16,Bold=-1,PrimaryColour=&H00FFFFFF,"
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

    body = {
        "snippet": {
            "title": ep["title"][:100],
            "description": ep["description"],
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

def add_to_playlist(video_id):
    if not PLAYLIST_ID:
        log("PLAYLIST_ID not set - skipping playlist add")
        return
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
              "https://www.googleapis.com/auth/youtube"]
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
    try:
        yt.playlistItems().insert(part="snippet",
            body={"snippet": {"playlistId": PLAYLIST_ID,
                              "resourceId": {"kind": "youtube#video", "videoId": video_id}}}).execute()
        log(f"added to playlist {PLAYLIST_ID}")
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

    prompts = ep["image_prompts"][:N_IMAGES]
    image_paths = []
    seed0 = random.randint(1000, 999999)
    for i, p in enumerate(prompts):
        dest = WORK / f"img_{i:02d}.png"
        if gen_image(p + ", Japanese 2D anime style, cinematic lighting, highly detailed" if STYLE != "chinese" else p + ", chinese animation style, xianxia, cinematic lighting, highly detailed", dest, seed0 + i):
            image_paths.append(dest)
        time.sleep(2)
    if len(image_paths) < 8:
        sys.exit(f"only {len(image_paths)} images generated - aborting")

    mp3, srt = WORK / "narration.mp3", WORK / "narration.srt"
    run_tts(WORK / "narration.txt", mp3, srt)

    thumb = WORK / "thumb.png"
    gen_image(ep.get("thumbnail_prompt", prompts[0]) + (", Japanese 2D anime style, dramatic, cinematic" if STYLE != "chinese" else ", chinese animation style, dramatic, cinematic"), thumb, seed0 + 999)

    out_mp4 = WORK / f"episode_{row['id']}.mp4"
    build_video(image_paths, mp3, srt, out_mp4, thumb)

    if DRY_RUN or not UPLOAD:
        log("DRY_RUN/UPLOAD=0 - skipping upload. Video at:", out_mp4)
        return

    vid = youtube_upload(ep, out_mp4, thumb)
    add_to_playlist(vid)
    try:
        drive_backup(out_mp4)
    except Exception as e:
        log("drive backup failed (non-fatal):", e)
    mark_done(row["id"])
    log("done -> https://youtu.be/" + vid)

if __name__ == "__main__":
    main()

