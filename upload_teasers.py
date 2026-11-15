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
