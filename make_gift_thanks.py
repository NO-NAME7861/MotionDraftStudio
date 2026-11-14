"""
make_gift_thanks.py - one-off special upload: a THANK YOU video for the channel's FIRST subscriber.
Motion-Draft Studio, Public upload, 16:9 recap-style, ~75s, AI visuals + AI voice.

Run:  python make_gift_thanks.py          (generates + uploads)
      python make_gift_thanks.py --dry    (renders only, no upload)
"""
import os, sys, json, subprocess, random, time
from pathlib import Path

ROOT = Path(__file__).parent
WORK = ROOT / "gift-work"
WORK.mkdir(parents=True, exist_ok=True)
OUT  = ROOT / "gift-out"
OUT.mkdir(parents=True, exist_ok=True)

W, H, FPS = 1024, 576, 25
VOICE = "en-IN-NeerjaExpressiveNeural"
RATE  = "-2%"
DRY_RUN = "--dry" in sys.argv

# ------------------------------------------------------------------ content
NARRATION = """
To my very first subscriber, thank you.

You found us before the applause did. Before the views, before the milestones, you hit one little red button,
because you believed in these stories before anyone else.

Chinese cultivators. Japanese samurai. Quiet heroes, tragic masters, legends reborn.
Every recap we tell, we tell because of you.

So this one is for you. Not for the algorithm. Not for the milestone.
For that one click, from that one human being, sitting somewhere right now, watching this.

Every single day, Motion-Draft Studio uploads a brand-new recap, Chinese animation, Japanese 2D anime,
and every story ends with a moral. That rhythm is for you. It started with your click.

If you're the one watching this, drop your name in the comments.
I'd love to thank you by name, from the bottom of this channel's heart.

Thank you. Truly. Welcome aboard, legend.
""".strip()

TITLE = "A Very Special THANK YOU for My First Subscriber ❤️ | Motion-Draft Studio"

DESCRIPTION = (
    "This one's for YOU — my very first subscriber.\n\n"
    "You believed in Motion-Draft Studio before anyone did, and for that I am genuinely grateful.\n\n"
    "Here's the deal: Motion-Draft Studio uploads a brand-new recap EVERY SINGLE DAY — "
    "Chinese animation recaps and Japanese 2D anime recaps, each ending with a moral worth taking.\n\n"
    "If you're the one, drop your name in the comments — I'd love to thank you by name.\n\n"
    "Subscribe for daily recaps: https://www.youtube.com/@MotionDraftStudio\n\n"
    "⚠️ This video features AI-generated visuals and AI narration.\n\n"
    "#MotionDraftStudio #FirstSubscriber #ThankYou #ChineseAnimationRecap #Japanese2DAnimeRecap"
)

TAGS = [
    "first subscriber", "thank you", "MotionDraftStudio", "milestone",
    "ChineseAnimationRecap", "Japanese2DAnimeRecap", "AnimationRecap",
    "daily recap", "milestone celebration", "MotionDraftShorts",
]

IMAGE_PROMPTS = [
    "chinese animation key visual, a lone figure on a mountain summit greeting a golden sunrise, sea of paper cranes rising toward the light, xianxia cel art, cinematic, dramatic lighting, no text",
    "japanese 2D anime key visual, a smiling student standing on a school rooftop under a rising sun, wind in the hair, city skyline behind, dramatic cel shaded art, no text",
    "fantasy animation, a glowing paper lantern drifting upward through a quiet night market into a starry sky, warm lights from stalls below, cinematic, no text",
    "chinese animation, a grand empty banquet hall where candle flames ignite one by one beneath hanging dragon banners, moonlight through tall windows, dramatic cel art, cinematic, no text",
    "japanese 2D anime style, a single window glowing with warm light on a quiet city street at night, a heart-shaped constellation forming above the rooftops, hopeful, dramatic cel shading, no text",
]

THUMB_PROMPT = (
    "youtube thumbnail, cinematic chinese animation style, close-up of a glowing red paper heart "
    "cupped in two hands above a mountain peak at sunrise, warm golden light rays, sea of paper cranes "
    "below, tear-jerking hopeful mood, dramatic lighting, no text"
)

# ------------------------------------------------------------------ helpers
def log(*a):
    print(f"[{__import__('datetime').datetime.now():%H:%M:%S}]", *a, flush=True)

# reuse the battle-tested CF FLUX -> Pollinations fallback from create_shorts
from create_shorts import cf_image  # noqa: E402

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
                    "-crf", "26", str(seg)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def mix_bgm(audio, bgm_gain=0.32):
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
        f"[1:a]volume=1.0[n];[0:a]volume={bgm_gain},"
        f"afade=t=in:st=0:d=5,afade=t=out:st={fade_end:.2f}:d=5[m];"
        f"[n][m]amix=inputs=2:duration=first:dropout_transition=2,loudnorm[a]",
        "-map", "[a]", "-c:a", "libmp3lame", "-q:a", "3", str(mixed)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log(f"BGM mixed (gain {bgm_gain}) + loudnorm")
    return mixed

# ------------------------------------------------------------------ build
def build():
    log("=== STEP 1: images (CF FLUX -> Pollinations fallback) ===")
    image_paths, seed0 = [], random.randint(1000, 999999)
    for i, p in enumerate(IMAGE_PROMPTS):
        dest = WORK / f"img_{i:02d}.png"
        if cf_image(p, dest, seed0 + i):
            image_paths.append(dest)
        else:
            log(f"image {i} failed - skipping")
        time.sleep(1)
    if len(image_paths) < 3:
        sys.exit(f"only {len(image_paths)} images generated - aborting")

    log("=== STEP 2: thumbnail ===")
    thumb_dest = WORK / "thumb.png"
    thumb = None
    if cf_image(THUMB_PROMPT, thumb_dest, seed0 + 999):
        thumb = thumb_dest
    else:
        log("thumbnail failed - video will upload without custom thumbnail")

    log("=== STEP 3: TTS ===")
    txt = WORK / "narration.txt"
    txt.write_text(NARRATION, encoding="utf-8")
    mp3, srt = WORK / "narration.mp3", WORK / "narration.srt"
    subprocess.run([sys.executable, "-m", "edge_tts",
                    "--file", str(txt), "--write-media", str(mp3),
                    "--write-subtitles", str(srt),
                    "--voice", VOICE, f"--rate={RATE}"], check=True)
    dur = media_duration(mp3)
    log(f"narration: {dur:.1f}s, ~{len(NARRATION.split())} words")

    log("=== STEP 4: render (Ken Burns + subtitles + BGM) ===")
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

    sub_style = ("FontName=Arial,FontSize=17,Bold=-1,PrimaryColour=&H00FFFFFF,"
                 "OutlineColour=&H00000000,BorderStyle=4,Outline=2,Shadow=0,MarginV=24")
    # relative path: spaces/drive-letter colons in absolute Windows paths break the libass filter
    srt_rel = Path("gift-work") / "narration.srt"
    out_mp4 = OUT / "gift_thanks_first_subscriber.mp4"
    subprocess.run(["ffmpeg", "-y", "-i", str(concat), "-i", str(mixed),
                    "-vf", f"subtitles='{srt_rel.as_posix()}':force_style='{sub_style}'",
                    "-c:v", "libx264", "-preset", "ultrafast", "-crf", "26",
                    "-c:a", "aac", "-b:a", "128k", "-shortest", str(out_mp4)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log("video ready:", out_mp4)
    return out_mp4, thumb

def upload(mp4, thumb):
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    token = ROOT / "token.json"
    if not token.exists():
        sys.exit("token.json missing - run get_token.py first")
    creds = Credentials.from_authorized_user_file(
        str(token), ["https://www.googleapis.com/auth/youtube.upload",
                     "https://www.googleapis.com/auth/youtube"])
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)

    body = {
        "snippet": {
            "title": TITLE,
            "description": DESCRIPTION,
            "tags": TAGS,
            "categoryId": "24",  # Entertainment
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }
    media = MediaFileUpload(str(mp4), chunksize=16 * 1024 * 1024, resumable=True,
                            mimetype="video/mp4")
    log("uploading to YouTube (public) ...")
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
            log("thumbnail set skipped:", e)
    return vid

def main():
    out_mp4, thumb = build()
    if DRY_RUN:
        log("--dry: skipping upload. Video at", out_mp4)
        return
    vid = upload(out_mp4, thumb)
    print("GIFT_VIDEO_URL=https://youtu.be/" + vid)

if __name__ == "__main__":
    main()
