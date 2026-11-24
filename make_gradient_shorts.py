"""make_gradient_shorts.py - build + upload vertical Shorts with algorithmic gradients.

No image APIs, no LLM, no external generation: only ffmpeg gradients, edge-tts and
the YouTube Data API. This cannot hit 429/402 image-generation errors.

Usage:
    python make_gradient_shorts.py            # build+upload up to SHORTS_PER_RUN (default 2)
    python make_gradient_shorts.py --dry-run  # build only, no upload, no state change

State: state/shorts_state.json -> {"done": [...], "next": N}
"""
import json
import os
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).parent
WORK = ROOT / "shorts-work"
OUT = ROOT / "shorts-out"
STATE_PATH = ROOT / "state" / "shorts_state.json"
WORK.mkdir(exist_ok=True)
OUT.mkdir(exist_ok=True)

W, H, FPS = 576, 1024, 25
VOICE = os.environ.get("TTS_VOICE", "en-IN-NeerjaExpressiveNeural")
RATE = os.environ.get("TTS_RATE", "-2%")
PER_RUN = int(os.environ.get("SHORTS_PER_RUN", "2"))
AFFILIATE = "?tag=motiondraft-20"
DISCLOSURE = "⚠️ AI-generated visuals and AI narration. Story is original commentary/explainer content."

SHORTS = [
    {
        "id": "GS01",
        "title": "जिसे अपनों ने मारने की साज़िश की — वही उनका राजा बना #Shorts",
        "text": "गाँव वालों ने सोचा कि वह लड़का हमेशा कमज़ोर रहेगा। उसकी ज़मीन छीन ली, उसका नाम मिटा दिया, और एक रात उसे ज़हर देकर मरने के लिए छोड़ दिया। लेकिन उस रात उसके शरीर में कुछ जागा। एक ऐसी ताकत जो सिर्फ़ दर्द से बनती है। सात साल बाद जब वह लौटा, तो उसके पीछे पूरी सल्तनत की सेना थी। और उसने किसी से बदला नहीं लिया — उसने सिर्फ़ अपनी जगह माँगी। जिसे अपनों ने मारा था, वही अब उनका राजा था। क्या आप माफ़ कर पाते?"
    },
    {
        "id": "GS02",
        "title": "ब्रह्मांड का सबसे कमज़ोर इंसान — जिसने देवताओं को घुटनों पर ला दिया #Shorts",
        "text": "देवताओं ने उसे सबसे नीचा दर्जा दिया था — शून्य। न कोई ताकत, न कोई विरासत, न कोई नाम। सबने कहा कि यह जीवन भर कमज़ोर ही रहेगा। लेकिन उन्हें नहीं पता था कि शून्य का मतलब खाली नहीं होता। शून्य वह जगह है जहाँ से हर चीज़ शुरू होती है। जिस दिन उसने अपनी ताकत पहचानी, उस दिन आसमान फट गया। और जो देवता उसे कमज़ोर समझते थे, वही उसके सामने घुटनों पर आ गए।"
    },
    {
        "id": "GS03",
        "title": "जिस लड़की ने अपना चेहरा बेच दिया — ताकि उसकी बहन ज़िंदा रहे #Shorts",
        "text": "रात भर बारिश हुई, और उसकी बहन की साँसें धीरे-धीरे कम हो रही थीं। दवा इतनी महँगी थी कि पूरा गाँव मिलकर भी नहीं खरीद सकता था। तब उस लड़की ने वह किया जो कोई नहीं करता — उसने अपना चेहरा बेच दिया। सुबह जब बहन की आँखें खुलीं, तो सामने कोई अपना खड़ा था, पर उसे पहचाना नहीं। क्योंकि जिसने अपना चेहरा दे दिया, वह खुद को भी भूल चुका था। क्या आप यह कुर्बानी दे पाते?"
    },
    {
        "id": "GS04",
        "title": "सात रातों का वचन — आठवें दिन सब मर गए, एक को छोड़कर #Shorts",
        "text": "सात रातों तक उसने मोमबत्ती जलाई और एक-एक नाम पुकारा। गाँव वाले हँसे — भूतों से बदला कौन लेता है? लेकिन आठवीं रात हवा रुक गई। दरवाज़े अपने आप खुले। और सुबह तक जिन-जिन लोगों ने उसके परिवार को जलाया था, वे सब ठंडे पड़े थे। सिर्फ़ एक बचा था — वह जिसने सच बोल दिया था। पुराने क़ानून कभी नहीं मरते। वे बस इंतज़ार करते हैं।"
    },
    {
        "id": "GS05",
        "title": "रातों-रात अमीर बनने वाला आदमी — जिसने आख़िर में सब कुछ लौटा दिया #Shorts",
        "text": "एक रात उसके खाते में ऐसी रकम आई जो किसी सपने से भी बड़ी थी। उसने महल खरीदे, नाम कमाया, और लोग उसके पैर छूने लगे। लेकिन हर दिन एक घर से बच्चों के रोने की आवाज़ आती थी — वह घर उसने किसी और का छीनकर बनवाया था। जिस दिन उसने वह घर लौटाया, उस दिन उसे सुकून मिला। दौलत सब कुछ खरीद सकती है, सिवाय उस नींद के जो ईमान से आती है।"
    },
    {
        "id": "GS06",
        "title": "जिस तलवार ने अपने ही मालिक को काट दिया #Shorts",
        "text": "वह तलवार तीन सौ साल से एक ही परिवार की सेवा कर रही थी। कहते थे कि जो इसे उठाएगा, वह कभी हारेगा नहीं। लेकिन एक दिन मालिक ने इसे उस इंसान के ख़िलाफ़ उठाया जिसने उसे बचाया था। तलवार ने आदेश मानने से इंकार कर दिया। और जब मालिक ने ज़ोर लगाया, तो तलवार पलट गई। ताकत वफ़ादारी से बड़ी नहीं होती। जो हथियार आपकी नफ़रत से चलता है, वह एक दिन आपकी तरफ़ मुड़ जाता है।"
    },
    {
        "id": "GS07",
        "title": "जिसे पूरे स्कूल ने 'कमज़ोर' कहा — उसने फाइनल में सबको हरा दिया #Shorts",
        "text": "हर मुक़ाबले में वह हारता रहा। कोई उसे टीम में नहीं लेता था। शिक्षक कहते थे कि इसमें कोई प्रतिभा नहीं। लेकिन उस लड़के ने हारना बंद नहीं किया — उसने हर हार से एक चीज़ सीखी। साल के फाइनल में जब सबसे ताक़वर खिलाड़ी मैदान में उतरा, तो सामने वही लड़का खड़ा था जिसे सब भूल चुके थे। उसने एक ऐसी चाल चली जो किसी किताब में नहीं थी। प्रतिभा नहीं, ज़िद जीतती है।"
    },
    {
        "id": "GS08",
        "title": "जिस बेटी ने अपने ही पिता का राज पलट दिया #Shorts",
        "text": "राजा ने अपने सिंहासन के लिए पूरा शहर जला दिया था। सिर्फ़ एक बच्ची बची थी — उसकी अपनी बेटी। उसने कसम खाई कि वह कभी उसका नाम नहीं लेगी। बीस साल बाद एक नई रानी ने दरबार संभाला। उसने एक-एक करके उन सबको इंसाफ़ दिया जिन्हें राजा ने मिटाया था। और जब पिता ने उससे माफ़ी माँगी, तो उसने कहा — मैं तुम्हारी बेटी नहीं, तुम्हारे गुनाहों की गवाह हूँ।"
    },
    {
        "id": "GS09",
        "title": "जिसने मौत को धोखा दिया — तीन बार #Shorts",
        "text": "पहली बार वह नदी में डूबा — किसी ने बाहर खींच लिया। दूसरी बार जंगल में ज़हर मिला — शरीर ने मना कर दिया। तीसरी बार तलवार सीने के ठीक ऊपर आई — और रुक गई। मौत ने कहा, तुम्हारा समय नहीं आया। लेकिन सच यह था कि उस आदमी के पास अब भी एक काम बाक़ी था, जो सिर्फ़ वही कर सकता था। कुछ लोग मरते नहीं, क्योंकि दुनिया को अभी उनकी ज़रूरत है।"
    },
    {
        "id": "GS10",
        "title": "आख़िरी दिन जब गाँव ने अपने हीरो को पहचाना #Shorts",
        "text": "पूरे गाँव ने उसे पागल कहा। वह हर रोज़ पहाड़ पर जाता और अकेले पत्थर तोड़ता रहता। लोग हँसते, बच्चे पीछे भागते। लेकिन जिस दिन पहाड़ से बाढ़ आई, वही पत्थरों का ढेर गाँव को बचाने वाली दीवार बन गया। तब किसी ने उसका नाम पूछा। वह मुस्कुराया और चला गया। असली हीरो वह नहीं जो पहचान चाहता है, बल्कि वह है जो बिना पहचान के भी काम करता है।"
    },
]


def log(*a):
    print(*a, flush=True)


def load_state():
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {"done": [], "next": 0}


def save_state(state):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def media_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True).stdout.strip()
    return float(out)


def make_gradient_image(dest, idx):
    palettes = [
        ("0x0d1b2a", "0x1a3a5c", "0x7f004f"), ("0x1b140c", "0x3b4a0b", "0xd4a500"),
        ("0x2c001e", "0x5a0a3d", "0xbc005a"), ("0x0f2027", "0x1e3a5f", "0x4d9656"),
        ("0x0d1117", "0x2d1b4e", "0x8ca6a0"), ("0x141e30", "0x273b4e", "0x4d9656"),
        ("0x001f3a", "0x0095d5", "0xf4cece"), ("0x14153c", "0x263e66", "0x8fbc9f"),
        ("0x3a404d", "0x5a5a6e", "0xc5c5c5"), ("0x2d3436", "0x4f4f56", "0xdddddd"),
        ("0x264653", "0x2a9d8f", "0xe9c46a"), ("0xf4a261", "0xe76f51", "0xffad4a"),
    ]
    c0, c1, c2 = palettes[idx % len(palettes)]
    vf = (f"gradients=s={W}x{H}:nb_colors=3:c0={c0}:c1={c1}:c2={c2}:speed=0.05,"
          f"noise=alls=10:allf=t,vignette=PI/3.5")
    r = subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", vf, "-frames:v", "1", "-q:v", "1", str(dest)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return r.returncode == 0 and Path(dest).exists() and Path(dest).stat().st_size > 5000


def tts(text, mp3):
    txt = mp3.with_suffix(".txt")
    txt.write_text(text, encoding="utf-8")
    subprocess.run(
        [sys.executable, "edge_tts_shim.py", "--file", str(txt),
         "--write-media", str(mp3), "--voice", VOICE, f"--rate={RATE}"],
        check=True)


def make_segment(img, seg, dur, zoom_in):
    frames = max(int(dur * FPS), FPS)
    z = "z='min(zoom+0.0011,1.18)'" if zoom_in else "z='if(eq(on,1),1.18,max(1.001,zoom-0.0016))'"
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
          f"zoompan={z}:d={frames}:s={W}x{H}:fps={FPS},format=yuv420p")
    subprocess.run(
        ["ffmpeg", "-y", "-loop", "1", "-i", str(img), "-t", f"{dur:.3f}",
         "-vf", vf, "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "21", str(seg)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def build_short(short):
    sid = short["id"]
    work = WORK / sid
    work.mkdir(exist_ok=True)
    mp3 = work / "narration.mp3"
    tts(short["text"], mp3)
    dur = media_duration(mp3)
    n = 5
    per = dur / n
    segs = []
    for i in range(n):
        img = work / f"img_{i:02d}.png"
        if not make_gradient_image(img, i + int(sid[-2:])):
            raise SystemExit(f"{sid}: gradient image failed")
        seg = work / f"seg_{i:02d}.mp4"
        make_segment(img, seg, per, zoom_in=(i % 2 == 0))
        segs.append(seg)
    concat_list = work / "concat.txt"
    concat_list.write_text("\n".join(f"file '{s.as_posix()}'" for s in segs), encoding="utf-8")
    concat = work / "concat.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(concat)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    out = OUT / f"{sid}.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(concat), "-i", str(mp3), "-c:v", "copy",
         "-c:a", "aac", "-b:a", "128k", "-shortest", str(out)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log(f"[built] {out.name} ({out.stat().st_size/1e6:.1f} MB, {dur:.1f}s)")
    return out


def upload_short(path, short):
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    creds = Credentials.from_authorized_user_file(
        str(ROOT / "token.json"),
        ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"])
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
    desc = (
        f"{short['title'].replace(' #Shorts', '')}\n\n"
        f"Anime-style story short in Hindi.\n\n{DISCLOSURE}\n\n"
        f"Watch the full series: https://www.youtube.com/@MotionDraftStudio\n"
        f"Affiliate: https://www.amazon.in{AFFILIATE}\n\n"
        "#Shorts #MotionDraftShorts #AnimeRecap #HindiStories"
    )
    body = {
        "snippet": {
            "title": short["title"][:100],
            "description": desc[:4900],
            "tags": ["Shorts", "MotionDraftShorts", "anime recap hindi", "hindi kahani",
                     "story shorts", "MotionDraftStudio"],
            "categoryId": "24",
            "defaultLanguage": "hi",
        },
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
    }
    media = MediaFileUpload(str(path), chunksize=8 * 1024 * 1024, resumable=True)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            log(f"  upload {int(status.progress() * 100)}%")
    log(f"[uploaded] {resp['id']} - https://youtu.be/{resp['id']}")
    return resp["id"]


def main():
    dry = "--dry-run" in sys.argv
    state = load_state()
    done = set(state.get("done", []))
    todo = [s for s in SHORTS if s["id"] not in done][:PER_RUN]
    if not todo:
        log("no pending shorts - add new scripts to SHORTS")
        return
    for short in todo:
        log(f"=== {short['id']} ===")
        path = build_short(short)
        if not dry:
            upload_short(path, short)
            done.add(short["id"])
            state["done"] = sorted(done)
            state["next"] = len(done)
            save_state(state)


if __name__ == "__main__":
    main()
