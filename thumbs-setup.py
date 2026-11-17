from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import json, urllib.request
from pathlib import Path
import os, sys

def _load_dotenv(path=".env"):
    try:
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    except FileNotFoundError:
        pass
_load_dotenv()

CF_ID = os.environ.get("CF_ACCOUNT_ID", "").strip()
CF_TOKEN = os.environ.get("CF_API_TOKEN", "").strip()

if not CF_ID or not CF_TOKEN:
    print("missing CF creds"); sys.exit(1)

JS = Path(__file__).parent

def cf_image(prompt, seed, out):
    data = json.dumps({"prompt": prompt}).encode()
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/accounts/{CF_ID}/ai/run/@cf/black-forest-labs/flux-1-schnell",
        data=data, method="POST",
        headers={"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"})
    req.add_header("User-Agent", "Mozilla/5.0")
    with urllib.request.urlopen(req, timeout=60) as r:
        resp = json.loads(r.read())
    img_b64 = resp.get("result", {}).get("image")
    import base64
    Path(out).write_bytes(base64.b64decode(img_b64))
    print("saved", out)

prompts = {
    "chinese": "Epic Chinese animation poster, blade warrior under dramatic crimson sky, xianxia fantasy, cinematic lighting, bold red and gold, rich painterly cel art, dramatic vertical composition, action-packed hero shot, no text",
    "japanese": "Japanese 2D anime poster, handsome blade dancer in dojo under cherry blossom sky, modern shoujo shonen anime style, cel shaded, dramatic lighting, bold colors, no text",
}
# make thumbnails (square-ish orientation works best)
cf_image(prompts["chinese"], 1234567, r"C:\Users\Park-Edge\Desktop\Thumb-Chinese.jpg")
cf_image(prompts["japanese"], 7654321, r"C:\Users\Park-Edge\Desktop\Thumbs-Japanese.jpg")

# verify
print("done. files:", list(Path.home().joinpath("Desktop").glob("Thumb*")))

creds = Credentials.from_authorized_user_file(
    r'C:\Users\Park-Edge\Documents\Default Project\youtube-automation\token.json',
    ["https://www.googleapis.com/auth/youtube.upload",
     "https://www.googleapis.com/auth/youtube"])
yt = build("youtube", "v3", credentials=creds, cache_discovery=False)

# existing videos: PXsC_50Rp90 (CN), mCbbQ-7YMgU (JP), KQHyB37djs4 (CN), 5SREj-1bRhw (CN), IsugqKzKU_0 (JP), SNZS9eBqLj4 (CN)
mapping = {
    "PXsC_50Rp90": "chinese",
    "mCbbQ-7YMgU": "japanese",
    "KQHyB37djs4": "chinese",
    "5SREj-1bRhw": "chinese",
    "IsugqKzKU_0": "japanese",
    "SNZS9eBqLj4": "chinese",
}

for vid, folder in mapping.items():
    f = JS.parent / "Thumbs-Japanese.jpg" if folder == "japanese" else JS.parent / "Thumb-Chinese.jpg"
    # use Desktop
    f = Path.home() / "Desktop" / ("Thumbs-Japanese.jpg" if folder == "japanese" else "Thumb-Chinese.jpg")
    try:
        yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(f), mimetype="image/jpeg")).execute()
        print("thumb set", vid)
    except Exception as e:
        print("thumb fail", vid, e)
