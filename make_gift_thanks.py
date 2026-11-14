"""
make_gift_thanks.py - rebuild/re-upload the first-subscriber special.
Kept for reproducibility; the engine now lives in thanks_video.py.

Run:  python make_gift_thanks.py        (builds + uploads the first-subscriber tribute)
      python make_gift_thanks.py --dry  (renders only, no upload)
"""
import sys
from thanks_video import build_and_upload

if __name__ == "__main__":
    build_and_upload(None, dry_run="--dry" in sys.argv)
