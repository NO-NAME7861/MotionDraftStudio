"""
make_teasers.py - 5 teaser Shorts for the mega video. NO TEXT ANYWHERE.
Motion graphics: sweeping light streaks, drifting ring sigils, rising chevrons,
letterbox bars, film grain, vignette. Narration in pure Devanagari Hindi (hi-IN-SwaraNeural).
9:16 vertical. Burned-subtitle free on purpose.

Run:  python make_teasers.py [T1 T2 ...]    (build only some)
Upload: python upload_teasers.py
"""
import os, sys, json, subprocess, random, time, urllib.request, urllib.parse, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import create_shorts as cs  # reuse cf_image (CF FLUX -> Pollinations fallback)

ROOT = Path(__file__).parent
WORK = ROOT / "teasers-work"
WORK.mkdir(exist_ok=True)
OUT = ROOT / "shorts-out"
OUT.mkdir(exist_ok=True)

W_, H_, FPS = 1024, 576, 25
VOICE = "hi-IN-SwaraNeural"

TEASERS = [
    {
        "id": "T1",
        "hook_prompts": [
            "chinese animation, xianxia key visual, a 19 year old genius disciple on a mountain trial rope under lightning, red banners, cel art, dramatic, no text",
            "chinese animation, azure heaven pavilion tower above clouds at dusk, dragon banners, xianxia cel art, no text",
            "chinese animation, an elder brother cutting a betrayal rope above a storm ravine, lightning, dramatic cel art, no text",
        ],
        "narration": (
            "हर कोई कहता था कि चेन यिरांग जानता है आगे क्या होगा। "
            "उन्नीस साल की उम्र, सात साल की मेहनत, और एक ऐसा खेल जिसे सिर्फ देखने से नहीं, "
            "जिरफ़ दरकिनार करना ही होता है — मास्टर, भाई, दोस्त, हबीबा। "
            "एक तूफ़ान की रात, सब सामने खड़े थे। और पर्वत पर रस्सी कट गई। "
            "इतना ही नहीं गिरता है कोई... इतना ही नाही — अब पूरी कहानी भयानक मोड़ लेगी।"
        ),
        "seed": 8101,
    },
    {
        "id": "T2",
        "hook_prompts": [
            "chinese animation, a storm on Thunder Crag, a disciple hanging from a single rope above a ravine, lightning strikes, cel art, no text",
            "chinese animation, a body falling against a stormy dark sky, one hand reaching upward, cinematic cel art, no text",
            "chinese animation, broken red prayer bead on wet grass, rain, macro perspective, no text",
        ],
        "narration": (
            "रस्सी कटने की आवाज़ सिर्फ हवा की नहीं थी। "
            "उस पल चेन यिरांग ने एक-एक चेहरे देखे — भाई जिसने काट दिया, "
            "मास्टर जिसने देखा और नहीं बोला, दोस्त जिसने दरवाज़ा पकड़ रखा था। "
            "कुछ चीजें इंसान भूल नहीं सकता। और कुछ चीज़ें उसे बदल देती हैं। "
            "गिरता हुआ लड़का... मार्ता नहीं, जागता है।"
        ),
        "seed": 8102,
    },
    {
        "id": "T3",
        "hook_prompts": [
            "chinese animation, a young man wet in river grass under red lanterns opening his eyes, rain, cel art, no text",
            "chinese animation, an underworld auction hall with shaded booths and screens of files, candle glow, no people, no text",
            "chinese animation, a dying crime kingpin in an obsidian armor chair with a ledger, smoke, cel art, no text",
        ],
        "narration": (
            "मरा हुआ था वो। कम से कम सब यही सोचते थे। "
            "पर रेड लैंटर्न की नमी में आँखें खुल गईं। ओब्सीडियन फेंग, "
            "गलत आदमी ने उठाया, गलत कामों की दुनिया थी — पर वही उगने की जगह थी। "
            "दामून ने ledger निकाली — एसेट नंबर शून्य चार एक। "
            "अब वो जीएगा ताकि बाकी सब को बुलाया जा सके।"
        ),
        "seed": 8103,
    },
    {
        "id": "T4",
        "hook_prompts": [
            "chinese animation, a brother in shackles in a cell lit blood red, one visitor standing outside, cel art, no text",
            "chinese animation, a silver plate with an old black leather ledger on it in a courtroom, candles, no text",
            "chinese animation, an old mentor's face crumbling as students turn around in a great hall, cel art, no text",
        ],
        "narration": (
            "पहला वार हमेशा सबसे चुपचाप होता है। "
            "भाई को पकड़ अपने ही टूर पर बेचा — जज, सबूत, सब पहले से तैयार। "
            "मास्टर को उनकी अपनी लीडेगर चांदी की थाली में सजा दी गई। "
            "दोस्त को बस एक ऑप्शन मिला — सच बोलो, या खेत में दफनाओ। "
            "कौन जीता? जानने के लिए पूरी कहानी देखो।"
        ),
        "seed": 8104,
    },
    {
        "id": "T5",
        "hook_prompts": [
            "chinese animation, a hidden throne room under a sect with chains and masks, fog, dark gold, no text",
            "chinese animation, hundreds of glowing papers flying out of a palace city, every screen goes red at once, cel art, no text",
            "chinese animation, a silhouette on a rooftop above a glowing burning throne, lightning behind, cel art, no text",
        ],
        "narration": (
            "और फिर वो फाइनल रात आई। "
            "पूरा सेक्ट, पूरी अदालतें, पूरी लीडेगर — एक ही पल, एक ही बटन — सब ओपन। "
            "छिपी हुई सिंहासन क्रूर मासूमियत का नकली मुखौटा था। "
            "बचपन वाला चेन यिरांग खत्म हो चुका था — परछाईं अब पूरा खेल चला रहा है। "
            "दो घंटे की पूरी कहानी, अभी देखना।"
        ),
        "seed": 8105,
    },
]


# ------------------------------------------------------------------ motion graphics assets (PIL)
def make_streak(path, w=900, h=170):
    """Diagonal light beam - translucent white gradient on transparent bg."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon([(0, h // 2 + 10), (w // 2, h // 2 - 45), (w - 100, h // 2 - 15), (w, h // 2)],
              fill=(255, 235, 180, 110))
    img.save(path)

def make_ring(path, size=460):
    """Gold/red concentric sigil ring - translucent."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = size // 2
    for r, col, wd in [(c - 8, (255, 80, 60, 150), 6), (c - 60, (255, 190, 90, 120), 10), (c - 120, (200, 60, 40, 160), 4), (c // 3, (255, 220, 150, 90), 3)]:
        d.ellipse([c - r, c - r, c + r, c + r], outline=col, width=wd)
    for a in range(0, 360, 45):
        x = c + (c - 8) * math.cos(math.radians(a))
        y = c + (c - 8) * math.sin(math.radians(a))
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=(255, 120, 80, 170))
    img = img.filter(ImageFilter.GaussianBlur(0.6))
    img.save(path)

def make_chevrons(path, size=360):
    """Six rising chevrons - deep amber on transparent."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, y in enumerate(range(30, size - 60, 48)):
        alpha = int(70 + 26 * i)
        d.polygon([(40, y), (size // 2, y - 26), (size - 40, y)],
                  fill=(255, 170 + i * 8, 60, alpha))
    img.save(path)


def build_teaser(t):
    sid = t["id"]
    d = WORK / sid
    d.mkdir(exist_ok=True)

    # 1) images
    imgs = []
    for i, p in enumerate(t["hook_prompts"]):
        dest = d / f"img_{i}.png"
        if cs.cf_image(p, dest, t["seed"] + i):
            imgs.append(dest)
        time.sleep(1)
    if len(imgs) < 2:
        raise RuntimeError(f"{sid}: only {len(imgs)} images")

    # 2) motion-graphic overlay assets (generated once)
    assets = WORK / "assets"
    assets.mkdir(exist_ok=True)
    streak = assets / "streak.png"; make_streak(streak)
    ring   = assets / "ring.png";   make_ring(ring)
    chev   = assets / "chevrons.png"; make_chevrons(chev)

    # 3) narration
    txt = d / "narration.txt"
    txt.write_text(t["narration"], encoding="utf-8")
    mp3 = d / "narration.mp3"
    subprocess.run([sys.executable, "-m", "edge_tts", "--file", str(txt),
                    "--write-media", str(mp3), "--voice", VOICE], check=True)
    dur = float(subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp3)],
        capture_output=True, text=True).stdout.strip())
    per = dur / len(imgs)

    # 4) concat segments (Ken Burns)
    segs = []
    for i, img in enumerate(imgs):
        seg = d / f"seg_{i}.mp4"
        frames = max(int(per * FPS), FPS)
        z = "z='min(zoom+0.0015,1.16)'" if i % 2 == 0 else "z='if(eq(on,1),1.16,max(1.001,zoom-0.0018))'"
        vf = (f"scale={W_}:{H_}:force_original_aspect_ratio=increase,crop={W_}:{H_},"
              f"zoompan={z}:d={frames}:s={W_}x{H_}:fps={FPS},format=yuv420p")
        subprocess.run(["ffmpeg", "-y", "-loop", "1", "-i", str(img), "-t", f"{per:.3f}",
                        "-vf", vf, "-r", str(FPS), "-c:v", "libx264", "-preset", "ultrafast",
                        "-crf", "26", str(seg)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        segs.append(seg)
    list_file = d / "concat.txt"
    list_file.write_text("\n".join(f"file '{s.as_posix()}'" for s in segs))
    concat = d / "concat.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
                    "-c", "copy", str(concat)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 5) final 9:16 render with motion graphics (NO TEXT)
    bgm = ROOT / "assets" / "music" / "epic_ambient.mp3"
    impact_len = 1.4
    out_mp4 = OUT / f"{sid}.mp4"
    filter_complex = (
        # vertical crop + scale from horizontal concat
        f"[0:v]crop=324:576:(in_w-324)/2:0,scale=576:1024,format=yuv420p[base];"
        # cinematic letterbox bars (pure black, not text)
        f"[base]drawbox=x=0:y=0:w=576:h=84:color=black:t=fill,"
        f"drawbox=x=0:y=944:w=576:h=80:color=black:t=fill[lb];"
        # light-streak sweep (repeats)
        f"[1:v]scale=760:-1[streak];"
        f"[lb][streak]overlay=x='mod(t*170,1000)-250':y='120+40*sin(t*0.9)':format=auto[s1];"
        # ring sigil drifting around center
        f"[2:v]scale=230:230[ring];"
        f"[s1][ring]overlay=x='288-115+70*sin(t*1.15)':y='520-115+55*cos(t*0.95)':format=auto[s2];"
        # split chevron stream once, then reuse for both sides (multi-input overlay requires it)
        f"[3:v]split=2[ch1][ch2];"
        f"[ch1]scale=150:150[chevA];"
        f"[ch2]scale=150:150[chevB];"
        f"[s2][chevA]overlay=x='42+30*sin(t*0.8)':y='1024-mod(t*150,640)':format=auto[s3];"
        f"[s3][chevB]overlay=x='434-30*sin(t*0.8)':y='1024-mod(t*150+320,640)':format=auto[s4];"
        # film grain + vignette, then force YouTube-friendly yuv420p
        f"[s4]noise=alls=4:allf=t,vignette=PI/4.6,format=yuv420p[vout];"
        # audio: narration + BGM + sub-impact
        f"[4:a]volume=1.0[n];"
        f"[5:a]volume=0.28,afade=t=in:st=0:d=2,afade=t=out:st={max(0.0, dur-4):.2f}:d=4[b];"
        f"[6:a]volume=0.55[i];"
        f"[n][b]amix=inputs=2:duration=first:dropout_transition=2[m];"
        f"[m][i]amix=inputs=2:duration=first:dropout_transition=1,loudnorm[aout]"
    )
    cmd = [
        "ffmpeg", "-y",
        "-i", str(concat),
        "-stream_loop", "-1", "-i", str(streak),
        "-stream_loop", "-1", "-i", str(ring),
        "-stream_loop", "-1", "-i", str(chev),
        "-i", str(mp3),
        "-stream_loop", "-1", "-i", str(bgm),
        "-f", "lavfi", "-i", f"aevalsrc=sin(2*PI*52*t)*exp(-5*t)|sin(2*PI*26*t)*exp(-7*t):d={impact_len}",
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "26", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-shortest", str(out_mp4),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    sz = out_mp4.stat().st_size
    print(f"[built] {out_mp4.name} ({sz/1e6:.1f} MB, {dur:.1f}s)", flush=True)
    return out_mp4

def main():
    only = sys.argv[1:]
    targets = [t for t in TEASERS if t["id"] in only] if only else TEASERS
    for t in targets:
        print(f"\n=== {t['id']} ===", flush=True)
        try:
            build_teaser(t)
        except Exception as e:
            print("FAIL", t["id"], e, flush=True)

if __name__ == "__main__":
    main()
