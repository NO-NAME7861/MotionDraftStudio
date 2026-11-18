"""
upload_teasers.py - upload the 5 mega-video teaser shorts (public, Chinese Shorts playlist).

Usage: python upload_teasers.py --mega-url https://youtu.be/XXXX   (direct link in description)
       python upload_teasers.py                                     (description points to channel)
"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import argparse
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

ROOT = Path(__file__).parent
OUT = ROOT / "shorts-out"
TOKEN_PATH = ROOT / "token.json"
CN_SHORTS_PLAYLIST = "PLCUjO71ZvRuo"  # Chinese Animation Shorts

BASE_TAGS = ["Shorts", "MotionDraftShorts", "ChineseAnimationRecapHindi",
             "MotionDraftStudio", "BetrayalRecap", "MysteryRecap"]

META = [
    {
        "file": "T1.mp4",
        "title": "उन्नीस साल की उम्र में सब ने छोड़ा — Betrayal की रात #Shorts",
        "description": (
            "सात साल की मेहनत — और तूफ़ान की उस रात भाई ने रस्सी काट दी।\n\n"
            "सुनो उसकी पूरी कहानी — {mega_link}\n\n"
            "⚠️ AI-generated visuals and AI narration.\n\n"
            "#Shorts #MotionDraftShorts #ChineseAnimationRecapHindi #MotionDraftStudio"
        ),
    },
    {
        "file": "T2.mp4",
        "title": "रस्सी कटने की आवाज़ — पूरी कहानी का असली मोड़ #Shorts",
        "description": (
            "भाई ने काट दिया, मास्टर ने देखा, दोस्त ने दरवाज़ा पकड़ा।\n\n"
            "पूरा सीन देखिए — {mega_link}\n\n"
            "⚠️ AI-generated visuals and AI narration.\n\n"
            "#Shorts #MotionDraftShorts #ChineseAnimationRecapHindi #MotionDraftStudio"
        ),
    },
    {
        "file": "T3.mp4",
        "title": "मरा हुआ था वो — RED LANTERN में वापस जाग गया #Shorts",
        "description": (
            "रेड लैंटर्न की नमी में आँखें खुलीं। एसेट नंबर शून्य चार एक — और एक परछाई का जन्म।\n\n"
            "पूरी कहानी — {mega_link}\n\n"
            "⚠️ AI-generated visuals and AI narration.\n\n"
            "#Shorts #MotionDraftShorts #ChineseAnimationRecapHindi #MotionDraftStudio"
        ),
    },
    {
        "file": "T4.mp4",
        "title": "पहला वार हमेशा चुपचाप होता है — भाई का अंजाम #Shorts",
        "description": (
            "भाई, मास्टर, दोस्त — जिसने भी पीठ दिखाई, उसका नंबर आया।\n\n"
            "पूरा सेट देखिये — {mega_link}\n\n"
            "⚠️ AI-generated visuals and AI narration.\n\n"
            "#Shorts #MotionDraftShorts #ChineseAnimationRecapHindi #MotionDraftStudio"
        ),
    },
    {
        "file": "T5.mp4",
        "title": "पूरा सिस्टम धूल में — Shadow King की एक रात #Shorts",
        "description": (
            "एक ही पल, एक ही बटन — सिंहासन, सेक्ट, सारा खेल एक साथ ओपन।\n\n"
            "पूरी दो घंटे की कहानी — {mega_link}\n\n"
            "⚠️ AI-generated visuals and AI narration.\n\n"
            "#Shorts #MotionDraftShorts #ChineseAnimationRecapHindi #MotionDraftStudio"
        ),
    },
    {
        "file": "T6.mp4",
        "title": "हर माँ ने छोड़ा — पर बच्ची की असली शक्ति #Shorts",
        "description": (
            "नौ साल की बच्ची, एक ऐसी पूजा — जो किसी ने नहीं जानी।\n\n"
            "पूरा सीन देखिए — {mega_link}\n\n"
            "⚠️ AI-generated visuals and AI narration.\n\n"
            "#Shorts #MotionDraftShorts #ChineseAnimationRecapHindi #MotionDraftStudio"
        ),
    },
    {
        "file": "T7.mp4",
        "title": "जो बच्चा सबको बलि माना — वो सबसे बड़ा #Shorts",
        "description": (
            "सब उसको कमजोर समझते थे — पर उसने मास्टर की हत्या पहले से देखी थी।\n\n"
            "पूरा सीन — {mega_link}\n\n"
            "⚠️ AI-generated visuals and AI narration.\n\n"
            "#Shorts #MotionDraftShorts #ChineseAnimationRecapHindi #MotionDraftStudio"
        ),
    },
    {
        "file": "T8.mp4",
        "title": "महाराज ने सबसे पहले अपने शिष्य को चखा #Shorts",
        "description": (
            "यह खून है, यह शराब है — कौन जानता था महाराज ने किसको चखा।\n\n"
            "पूरी कहानी — {mega_link}\n\n"
            "⚠️ AI-generated visuals and AI narration.\n\n"
            "#Shorts #MotionDraftShorts #ChineseAnimationRecapHindi #MotionDraftStudio"
        ),
    },
    {
        "file": "T9.mp4",
        "title": "पर्वत बोला — पर केवल एक आदमी सुन पाया #Shorts",
        "description": (
            "पर्वत बोला — जिन्नवो भी नहीं, महाराज भी नहीं। केवल एक।\n\n"
            "पूरा सीन — {mega_link}\n\n"
            "⚠️ AI-generated visuals and AI narration.\n\n"
            "#Shorts #MotionDraftShorts #ChineseAnimationRecapHindi #MotionDraftStudio"
        ),
    },
    {
        "file": "T10.mp4",
        "title": "मास्टर की आखिरी सांस — असली contract #Shorts",
        "description": (
            "दिल पर भरोसा मत करो — मास्टर ने कहा। यह contract इसी की सच्चाई है।\n\n"
            "पूरा सेट — {mega_link}\n\n"
            "⚠️ AI-generated visuals and AI narration.\n\n"
            "#Shorts #MotionDraftShorts #ChineseAnimationRecapHindi #MotionDraftStudio"
        ),
    },
    {
        "file": "T11.mp4",
        "title": "दो बार अपने ही बेटे को ज़हर दिया — तीसरी बार कौन पिला गया #Shorts",
        "description": (
            "दो बार जहर दिया, तीसरी बार उसने ख़ुद पिया — कमरे में एक सांप छिपा था\n\n"
            "पूरी कहानी → {mega_link}\n\n"
            "⚠️ AI-generated visuals and AI narration.\n\n"
            "#Shorts #MotionDraftShorts #ChineseAnimationRecapHindi #MotionDraftStudio"
        ),
    },
    {
        "file": "T12.mp4",
        "title": "नौ साल की उम्र में सब कुछ जल गया — अब वह उन्नीस साल का है #Shorts",
        "description": (
            "जिसने पूरा वंश जलते देखा, आज वही आग उसका सबसे बड़ा हथियार है\n\n"
            "पूरी कहानी → {mega_link}\n\n"
            "⚠️ AI-generated visuals and AI narration.\n\n"
            "#Shorts #MotionDraftShorts #ChineseAnimationRecapHindi #MotionDraftStudio"
        ),
    },
    {
        "file": "T13.mp4",
        "title": "बहन को बचाने के लिए अपना चेहरा बेच दिया — फिर कोई नहीं पहचाना #Shorts",
        "description": (
            "जिसने अपना चेहरा बेच दिया, उसे पहचानने वाला कोई नहीं बचा\n\n"
            "पूरी कहानी → {mega_link}\n\n"
            "⚠️ AI-generated visuals and AI narration.\n\n"
            "#Shorts #MotionDraftShorts #ChineseAnimationRecapHindi #MotionDraftStudio"
        ),
    },
    {
        "file": "T14.mp4",
        "title": "जिस महाराज ने सबको जलाया — उसी की बेटी ने पाया उसका सिंहासन #Shorts",
        "description": (
            "जलाने वाले पिता की इकलौती बेटी — अब उसके सिंहासन पर बैठी है\n\n"
            "पूरी कहानी → {mega_link}\n\n"
            "⚠️ AI-generated visuals and AI narration.\n\n"
            "#Shorts #MotionDraftShorts #ChineseAnimationRecapHindi #MotionDraftStudio"
        ),
    },
    {
        "file": "T15.mp4",
        "title": "सात रातों का वचन — आठवें दिन सब मरे, एक को छोड़कर #Shorts",
        "description": (
            "सात रातें, सात दरवाजे, एक वचन — आठवें दिन क्या हुआ\n\n"
            "पूरी कहानी → {mega_link}\n\n"
            "⚠️ AI-generated visuals and AI narration.\n\n"
            "#Shorts #MotionDraftShorts #ChineseAnimationRecapHindi #MotionDraftStudio"
        ),
    },
    {
        "file": "T16.mp4",
        "title": "भाई ने आख़िरी रात में कहा — माफ़ कर देना — फिर मर गया... पर वह बदला बनकर लौट आया #Shorts",
        "description": (
            "मरने के बाद भी खून का कर्ज़ अदा करना था — भाई की रूह बदला लेने वापस आई\n\n"
            "पूरी कहानी → {mega_link}\n\n"
            "⚠️ AI-generated visuals and AI narration.\n\n"
            "#Shorts #MotionDraftShorts #ChineseAnimationRecapHindi #MotionDraftStudio"
        ),
    },
    {
        "file": "T17.mp4",
        "title": "जब पूरा clan जला, तब एक बहन ने अपना चेहरा जला दिया — ताकि कोई पहचान न सके #Shorts",
        "description": (
            "चेहरा जलाकर बहन ने अपनी पहचान मिटाई — ताकि बदला बिना पहचाने लिया जाए\n\n"
            "पूरी कहानी → {mega_link}\n\n"
            "⚠️ AI-generated visuals and AI narration.\n\n"
            "#Shorts #MotionDraftShorts #ChineseAnimationRecapHindi #MotionDraftStudio"
        ),
    },
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mega-url", default="youtube.com/@MotionDraftStudio (channel page)")
    ap.add_argument("only", nargs="*", help="upload only these ids (e.g. T3 T4 T5)")
    args = ap.parse_args()
    mega_link = args.mega_url
    only = set(args.only)

    if not TOKEN_PATH.exists():
        raise SystemExit("token.json missing")
    creds = Credentials.from_authorized_user_file(
        str(TOKEN_PATH), ["https://www.googleapis.com/auth/youtube.upload",
                          "https://www.googleapis.com/auth/youtube"])
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)

    for m in META:
        if only and m["file"].replace(".mp4", "") not in only:
            continue
        f = OUT / m["file"]
        if not f.exists():
            print(f"SKIP {m['file']} - missing")
            continue
        body = {
            "snippet": {
                "title": m["title"][:100],
                "description": m["description"].format(mega_link=mega_link),
                "tags": BASE_TAGS,
                "categoryId": "24",
                "defaultLanguage": "hi",
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
            },
        }
        req = yt.videos().insert(part="snippet,status", body=body,
                                 media_body=MediaFileUpload(str(f), chunksize=16 * 1024 * 1024, resumable=True))
        resp = None
        while resp is None:
            status, resp = req.next_chunk()
            if status:
                print(f"  {m['file']} upload {int(status.progress() * 100)}%", flush=True)
        vid = resp["id"]
        print(f"uploaded {vid} - {m['title'][:40]}", flush=True)
        try:
            yt.playlistItems().insert(part="snippet",
                                      body={"snippet": {"playlistId": CN_SHORTS_PLAYLIST,
                                                        "resourceId": {"kind": "youtube#video", "videoId": vid}}}).execute()
            print(f"  added to {CN_SHORTS_PLAYLIST}")
        except Exception as e:
            print(f"  playlist add failed: {e}")


if __name__ == "__main__":
    main()
