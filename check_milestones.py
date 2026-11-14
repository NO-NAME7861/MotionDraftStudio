"""
check_milestones.py - uploads a tribute video when the channel crosses a subscriber milestone.

Milestones: 50, 100, 500, 1000, then every 5000 subscribers (5000, 10000, 15000, ...).
State:   state/milestones.json  -> {"rewarded": [50, ...]}
Runs inside the GitHub Actions cron; also runnable locally.

Notes:
  - YouTube rounds subscriberCount to 3 significant figures at 1000+ subs.
    All thresholds (50/100/500/1000/5000/...) round cleanly, so crossings still detect.
  - Never fails loudly: any error is logged and the script exits 0, so a tribute
    problem can never break the daily episode pipeline.
"""
import json
import sys
from pathlib import Path

ROOT  = Path(__file__).parent
STATE = ROOT / "state" / "milestones.json"

MILESTONES = [50, 100, 500, 1000] + list(range(5000, 500_001, 5000))


def log(*a):
    from datetime import datetime
    print(f"[{datetime.now():%H:%M:%S}]", *a, flush=True)

def load_state():
    if STATE.exists():
        # utf-8-sig tolerates a BOM if the file was ever edited with PowerShell/Notepad
        return json.loads(STATE.read_text(encoding="utf-8-sig"))
    return {"rewarded": []}

def save_state(rewarded):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps({"rewarded": sorted(set(rewarded))}, indent=2, ensure_ascii=False)
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(data)
    tmp.replace(STATE)  # atomic, avoids corrupting state on kill
    log(f"milestones state -> rewarded={sorted(set(rewarded))}")

def get_subscribers(yt):
    r = yt.channels().list(part="statistics", mine=True).execute()
    subs = r.get("items", [])
    if not subs:
        return None
    stats = subs[0].get("statistics", {})
    if stats.get("hiddenSubscriberCount"):
        log("hiddenSubscriberCount=true on channel - cannot track milestones")
        return None
    n = stats.get("subscriberCount")
    return int(n) if n is not None else None

def main():
    token = ROOT / "token.json"
    if not token.exists():
        log("token.json missing - milestone check skipped (CI should decode it first)")
        return 0

    state = load_state()
    rewarded = set(state.get("rewarded", []))

    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        creds = Credentials.from_authorized_user_file(
            str(token), ["https://www.googleapis.com/auth/youtube.upload",
                         "https://www.googleapis.com/auth/youtube"])
        yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
        subs = get_subscribers(yt)
    except Exception as e:
        log(f"milestone check: YouTube lookup failed (non-fatal): {e}")
        return 0

    if subs is None:
        log("milestone check: subscriber count unavailable (non-fatal)")
        return 0
    log(f"subscribers: {subs} (already rewarded: {sorted(rewarded)})")

    pending = [m for m in MILESTONES if subs >= m and m not in rewarded]
    if not pending:
        log("milestone check: no new milestones - nothing to upload")
        return 0

    for m in pending:
        log(f"*** MILESTONE CROSSED: {m:,} subscribers - generating tribute video ***")
        try:
            from thanks_video import build_and_upload
            vid = build_and_upload(m)
        except Exception as e:
            log(f"milestone {m}: tribute video failed (will retry next run): {e}")
            continue
        rewarded.add(m)
        save_state(rewarded)
        log(f"milestone {m}: tribute live at https://youtu.be/{vid}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
