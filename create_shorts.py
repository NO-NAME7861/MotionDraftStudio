"""
create_shorts.py - generate 3 poll/question Shorts (mixed Chinese + Japanese series)
Uses pollinations + CF FLUX; generates vertical MP4.
"""
import os, sys, json, subprocess, urllib.request, urllib.parse, time
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent
WORK = ROOT / "shorts-work"
WORK.mkdir(parents=True, exist_ok=True)
OUT = ROOT / "shorts-out"
OUT.mkdir(parents=True, exist_ok=True)

PROMPTS = [
    {
        "id": "W1",
        "series": "chinese",
        "hook": "Which is stronger? Mercy or Revenge?",
        "question": "Which do YOU choose: mercy or revenge?",
        "narration": (
            "In the shadow of the Heavenly Demon Sect, a poisoned prince holds the power to destroy his father. "
            "One choice: honour the victims, or spill blood in the name of justice. "
            "Mercy is quiet strength; revenge is a beautiful fire that consumes its wielder. "
            "But true heroes know the difference. "
            "So tell me: which would you pick? Mercy or revenge? "
            "Like for mercy, comment for revenge. Subscribe — and let the story answer."
        ),
        "image_prompts": [
            "chinese animation, xianxia fantasy poster, a young poisoned prince holding a broken sword over a crimson sky, dramatic cel art, cinematic lighting, no text",
            "chinese animation, xianxia fantasy poster, a young poisoned prince on a mountain where a demon king sits on a throne, cinematic, dramatic, no text",
            "chinese animation, xianxia fantasy poster, a young poisoned prince facing his demon king father across a battlefield of dragons, epic dramatic lighting, no text",
        ],
        "tags": ["poll", "ChineseAnimation", "CultivationRecap", "MercyVsRevenge", "AnimationRecap", "MotionDraftStudio"],
    },
    {
        "id": "W2",
        "series": "japanese",
        "hook": "Old rule or new truth?",
        "question": "Break tradition, or keep the chain?",
        "narration": (
            "In a school where silence is the law, one boy refuses to blink. "
            "The chain of bullying runs for generations — until the one nobody expected stands up. "
            "Breaking the chain isn't violence, it's courage. "
            "So here's the question: would you break the chain, or keep the silence? "
            "Like for breaking; comment for keeping. Subscribe — the story is just beginning."
        ),
        "image_prompts": [
            "japanese 2D anime poster, a single student standing tall against a crowd, modern shoujo shonen style, dramatic cel shaded art, no text",
            "japanese 2D anime poster, a quiet school hallway with cherry blossoms blooming through a window, melancholy dramatic cel shaded art, no text",
            "japanese 2D anime poster, a student's hand reaching out to another over a crowd, hope rising, dramatic dramatic cel shaded art, no text",
        ],
        "tags": ["poll", "Japanese2DAnime", "AnimeRecap", "StoicHero", "NoMoreSilence", "AnimationRecap", "MotionDraftStudio"],
    },
    {
        "id": "W3",
        "series": "chinese",
        "hook": "Wealth or Honour?",
        "question": "Would you sell your honour for riches?",
        "narration": (
            "A rice merchant feeds a plague-stricken city when no one else would. "
            "He feeds them until he's penniless — and loses everything. "
            "But he gains what can never be bought: the gratitude of a nation he saved. "
            "Would you give up wealth for honour and love? "
            "Like for honour, comment for wealth. Subscribe — our next story is on its way."
        ),
        "image_prompts": [
            "chinese animation, xianxia fantasy poster, a humble merchant carrying bags of rice through a plague-stricken city gate, dramatic cel art, cinematic lighting, no text",
            "chinese animation, xianxia fantasy poster, a city square kneeling before an ordinary merchant with arms full of grain, epic dramatic cel art, no text",
            "chinese animation, xianxia fantasy poster, a merchant standing at dawn on an empty road rich with the honor of the crowd behind him, dramatic cel art, no text",
        ],
        "tags": ["poll", "ChineseAnimation", "RiceMerchant", "HonourOverWealth", "CultivationRecap", "AnimationRecap", "MotionDraftStudio"],
    },
]

CF_ID = os.environ.get("CF_ACCOUNT_ID", "REDACTED_CF_ACCOUNT_ID").strip()
CF_TOKEN = os.environ.get("CF_API_TOKEN", "REDACTED_CF_TOKEN").strip()
W_, H_, FPS = 1024, 576, 25

def cf_image(prompt, out, seed):
    bail_prompt = prompt + " vertical composition"
    data = json.dumps({"prompt": bail_prompt}).encode()
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/accounts/{CF_ID}/ai/run/@cf/black-forest-labs/flux-1-schnell",
        data=data, method="POST",
        headers={"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                resp = json.loads(r.read())
            img_b64 = resp.get("result", {}).get("image")
            import base64
            Path(out).write_bytes(base64.b64decode(img_b64))
            print(f"[ok] cf image {out.name}", flush=True)
            return True
        except Exception as e:
            print(f"[{attempt+1}/3] cf image fail: {e}", flush=True)
            time.sleep(4)
    # fallback Pollinations
    try:
        url = ("https://image.pollinations.ai/prompt/"
               + urllib.parse.quote(bail_prompt)
               + f"?width={W_}&height={H_}&nologo=true&seed={seed}")
        req2 = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req2, timeout=90) as r:
            data = r.read()
        if len(data) > 15_000:
            Path(out).write_bytes(data)
            print(f"[ok-p] pollinations image {out.name}", flush=True)
            return True
    except Exception as e:
        print(f"pollinations fail: {e}", flush=True)
    return False

def run_tts(text_file, mp3, voice="en-US-JennyNeural"):
    subprocess.run([sys.executable, "-m", "edge_tts", "--file", str(text_file),
                    "--write-media", str(mp3), "--voice", voice], check=True)

def build_short(s):
    sid = s["id"]
    f_n = WORK / sid
    f_n.mkdir(parents=True, exist_ok=True)
    img_paths = []
    for i, p in enumerate(s["image_prompts"]):
        out = f_n / f"img_{i:02d}.png"
        if cf_image(p, out, seed=i + 1):
            img_paths.append(out)
        time.sleep(1)
    if len(img_paths) < 3:
        print(f"WARN {sid} only {len(img_paths)} images")

    # TTS narration (writes text file + media)
    txt = f_n / "narration.txt"
    txt.write_text(s["narration"], encoding="utf-8")
    mp3 = f_n / "narration.mp3"
    run_tts(txt, mp3)

    # Simple Ken Burns visualisation of each image for duration/N (cropped long-ish)
    probe = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(mp3)], capture_output=True, text=True).stdout.strip()
    total = float(probe)
    per = total / len(img_paths)
    FPS = 25
    segs = []
    for i, img in enumerate(img_paths):
        z = "z='min(zoom+0.0015,1.18)'" if (i % 2 == 0) else "z='if(eq(on,1),1.18,max(1.001,zoom-0.0018))'"
        d = max(int(per * FPS), FPS)
        seg = f_n / f"seg_{i:02d}.mp4"
        vf = f"scale={W_}:{H_}:force_original_aspect_ratio=increase,crop={W_}:{H_},zoompan={z}:d={d}:s={W_}x{H_}:fps={FPS},format=yuv420p"
        subprocess.run(["ffmpeg", "-y", "-loop", "1", "-i", str(img), "-t", f"{per:.3f}",
                        "-vf", vf, "-r", str(FPS), "-c:v", "libx264", "-preset", "ultrafast", "-crf", "26", str(seg)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        segs.append(seg)
        print(f"  seg {i+1}/{len(img_paths)} ({per:.1f}s)")

    # concat
    list_file = f_n / "concat.txt"
    list_file.write_text("\n".join(f"file '{s.as_posix()}'" for s in segs))
    concat = f_n / "concat.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(concat)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # crop vertical 9:16 + burned subtitles (question) + audio
    sub_srt = f_n / "sub.srt"
    hook = s["hook"]
    srt_text = (
        f"1\n00:00:00,000 --> 00:00:04,000\n{hook}\n\n"
        f"2\n00:00:04,000 --> 00:00:06,000\n{s['question']}\n\n"
    )
    sub_srt.write_text(srt_text, encoding="utf-8")
    dur = total  # seconds
    sub_style = "FontName=Arial,FontSize=42,Bold=-1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=4,Outline=3,Shadow=0,MarginV=160,Alignment=2"
    # 1024x576 -> 9:16 vertical = width 324, height 576; center horizontally
    vf = f"crop=324:576:(in_w-324)/2:0,scale=576:1024,format=yuv420p,subtitles={sub_srt.as_posix()}:force_style='{sub_style}'"
    out_mp4 = OUT / f"{sid}.mp4"
    subprocess.run(["ffmpeg", "-y", "-i", str(concat), "-i", str(mp3),
                    "-vf", vf, "-c:v", "libx264", "-preset", "ultrafast", "-crf", "26",
                    "-c:a", "aac", "-b:a", "128k", "-shortest", str(out_mp4)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    sz = out_mp4.stat().st_size
    print(f"[built] {out_mp4.name} ({sz/1e6:.1f} MB, {dur:.1f}s)")

def main():
    for s in PROMPTS:
        print(f"\n=== {s['id']} ({s['series']}) ===", flush=True)
        try:
            build_short(s)
        except Exception as e:
            print("FAIL", e, flush=True)

if __name__ == "__main__":
    main()
