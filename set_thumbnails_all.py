"""set_thumbnails_all.py - generate + upload a good CTR thumbnail for every video
in the uploads playlist that does not already have a known-good custom thumbnail.

Usage: python set_thumbnails_all.py
"""
import os
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).parent
OUT = ROOT / "thumbs-out"
OUT.mkdir(parents=True, exist_ok=True)
TOKEN = ROOT / "token.json"

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

W, H = 1280, 720
FONTS = [r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts/arial.ttf", r"C:\Windows/Fonts/DejaVuSans-Bold.ttf"]


def font(size):
    for p in FONTS:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()


PALETTES = {
    "god":   ((52, 30, 84, 255), (18, 8, 40, 255), (255, 90, 60, 255)),
    "rezero": ((20, 8, 40, 255), (10, 10, 30, 255), (90, 130, 255, 255)),
    "sung":  ((40, 10, 20, 255), (12, 6, 12, 255), (255, 150, 60, 255)),
    "chinese": ((20, 40, 60, 255), (6, 12, 18, 255), (60, 190, 160, 255)),
    "japanese": ((30, 10, 30, 255), (10, 8, 12, 255), (230, 120, 230, 255)),
    "pills": ((30, 40, 10, 255), (12, 14, 10, 255), (210, 180, 60, 255)),
}


def hex_to_rgb(h):
    h = (h or "0d1b2a").lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def gen_thumb(title: str, seed_idx: int, dest: Path):
    pal = list(PALETTES.values())[seed_idx % len(PALETTES)]
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        t = y / H
        top, bot = pal[0], pal[1]
        r = int(top[0] * (1 - t) + bot[0] * t)
        g = int(top[1] * (1 - t) + bot[1] * t)
        b = int(top[2] * (1 - t) + bot[2] * t)
        for x in range(W):
            px[x, y] = (r, g, b)
    d = ImageDraw.Draw(img, "RGBA")

    fh = 150
    ty = 110
    d.text((60, ty), title[:70], font=font(fh), fill=(255, 255, 255))
    d.rectangle([60, 300, 360, 312], fill=(255, 90, 60))
    sy = 336
    d.text((60, sy), f"HINDI RECAP  |  {title[:55]}", font=font(42), fill=(235, 235, 235))
    img = img.filter(ImageFilter.GaussianBlur(0.35))
    img.save(str(dest), quality=95)
    return dest


def upload(yt, vid, thumb_path):
    media = MediaFileUpload(str(thumb_path), chunksize=16 * 1024 * 1024, resumable=True)
    yt.thumbnails().set(videoId=vid, media_body=media).execute()
    return True


def main():
    creds = Credentials.from_authorized_user_file(
        str(TOKEN), ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"])
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
    pl = "UUzU1cvWNsJJrbbp6HMkxIOg"
    ids = []
    page = None
    while True:
        r3 = yt.playlistItems().list(part="contentDetails", playlistId=pl, maxResults=50, pageToken=page).execute()
        ids += [i["contentDetails"]["videoId"] for i in r3.get("items", [])]
        page = r3.get("nextPageToken")
        if not page:
            break

    done_ids = []
    for vid in ids:
        r4 = yt.videos().list(part="snippet", id=vid).execute()
        for it in r4.get("items", []):
            title = it["snippet"]["title"]
            skip = "Betrayal Chronicles Arc 1" in title or "The Ronin Betrayed" in title or "M002" in title
            hook = re.sub(r"[^A-Za-z0-9 ]", "", title.replace("https://", "").split(" | ")[-1])[:40] if " | " in title else title[:45]
            hook = re.sub(r"\d+", "", hook)
            tp = OUT / (vid + ".png")
            gen = gen_thumb(hook.strip().replace(" | ", " | ").strip()[:70] or "Anime", seed_idx=len(done_ids), dest=tp)
            ok = upload(yt, vid, tp)
            done_ids.append((vid, ok, title[:45]))
            print(f"{vid} ok={ok} | {title[:60]}")

    print("THUMB_DONE", len(done_ids))


if __name__ == "__main__":
    main()
