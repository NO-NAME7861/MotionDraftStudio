"""
upload_shorts.py - upload shorts/work/*.mp4 to the channel, with series-specific playlist tags
Writes to "Chinese Animation Shorts" or "Japanese 2D Anime Shorts" playlist.
"""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import json, sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent
TOKEN_PATH = ROOT / "token.json"
OUT = ROOT / "shorts-out"

META = [
    {
        "file": "W1.mp4",
        "series": "chinese",
        "title": "Which is stronger: Mercy or Revenge? 🤔 #Shorts #MotionDraftShorts",
        "description": (
            "A poisoned prince holds the power to destroy his demon king father. "
            "Which option would you take?\n\n"
            "Like 🤍 if you choose mercy · Comment your answer below.\n\n"
            "⚠️ AI-generated visuals and narration.\n\n"
            "#MotionDraftShorts #MotionDraftStudio #ChineseAnimationRecap"
        ),
        "tags": ["Shorts", "MotionDraftShorts", "ChineseAnimationRecap", "MercyVsRevenge", "CultivationRecap", "MotionDraftStudio"],
    },
    {
        "file": "W2.mp4",
        "series": "japanese",
        "title": "Break the chain of silence or keep the silence? 🤫 #Shorts",
        "description": (
            "In a school where silence is the law, one student refuses to blink.\n\n"
            "Like 🤍 if you break the chain · Comment your answer below.\n\n"
            "⚠️ AI-generated visuals and narration.\n\n"
            "#MotionDraftShorts #MotionDraftStudio #Japanese2DAnimeRecap"
        ),
        "tags": ["Shorts", "MotionDraftShorts", "Japanese2DAnimeRecap", "AnimeRecap", "StoicHero", "MotionDraftStudio"],
    },
    {
        "file": "W3.mp4",
        "series": "chinese",
        "title": "Wealth or Honour? What would YOU choose? 🍚 #Shorts",
        "description": (
            "A rice merchant feeds a plague-stricken city when no one else would — "
            "losing all his wealth but gaining a nation's gratitude.\n\n"
            "Like 🤍 for honour · Comment for wealth.\n\n"
            "⚠️ AI-generated visuals and narration.\n\n"
            "#MotionDraftShorts #MotionDraftStudio #ChineseAnimationRecap"
        ),
        "tags": ["Shorts", "MotionDraftShorts", "ChineseAnimationRecap", "HonourOverWealth", "RiceMerchant", "MotionDraftStudio"],
    },
]

CN_TITLE = "Chinese Animation Shorts"
JP_TITLE = "Japanese 2D Anime Shorts"

def upload_one(yt, token, meta):
    f = OUT / meta["file"]
    if not f.exists():
        print(f"SKIP {meta['file']} - missing")
        return None
    body = {
        "snippet": {
            "title": meta["title"][:100],
            "description": meta["description"],
            "tags": meta["tags"],
            "categoryId": "24",
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }
    req = yt.videos().insert(part="snippet,status", body=body, media_body=MediaFileUpload(str(f), chunksize=16*1024*1024, resumable=True))
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"  upload {int(status.progress()*100)}%", flush=True)
    vid = resp["id"]
    print(f"uploaded {vid} - {meta['title'][:60]}")
    return vid

def playlist_for(yt, creds, series):
    title = CN_TITLE if series == "chinese" else JP_TITLE
    resp = yt.playlists().list(part="snippet", mine=True, maxResults=50).execute()
    for item in resp.get("items", []):
        if item["snippet"]["title"] == title:
            return item["id"]
    desc = (f"Shorts from the Chinese animation recap series. Each short is a poll — your answer shapes the story."
            if series == "chinese" else
            f"Shorts from the Japanese 2D anime recap series. Each short is a poll — your answer shapes the story.")
    p = yt.playlists().insert(part="snippet,status",
        body={"snippet": {"title": title, "description": desc, "defaultLanguage": "en"},
              "status": {"privacyStatus": "public"}}).execute()
    print(f"created playlist: {title} ({p['id']})")
    return p["id"]

def main():
    if not TOKEN_PATH.exists():
        sys.exit("token.json missing")
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH),
        ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"])
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)

    for meta in META:
        vid = upload_one(yt, creds, meta)
        if not vid:
            continue
        pid = playlist_for(yt, creds, meta["series"])
        try:
            yt.playlistItems().insert(part="snippet",
                body={"snippet": {"playlistId": pid,
                                  "resourceId": {"kind": "youtube#video", "videoId": vid}}}).execute()
            print(f"  added to {pid}")
        except Exception as e:
            print(f"  playlist add failed: {e}")

if __name__ == "__main__":
    main()
