"""
mega_queue.py - daily self-healing watchdog for the MEGA 2h Devanagari series.

Logic:
  1. Reads state/mega_queue.json  -> {"done": ["M001", ...]}
  2. For every pending variant (in declared order), tries to build + upload it
     via make_mega_video.py (same pipeline: 7-part LLM -> SRT -> TTS -> render -> public upload).
  3. On success, marks it done. On failure, it simply retries on the NEXT run (no manual command needed).
  4. Fully no-op when everything is done. Never fails loudly - exits 0 so a single bad variant
     can't block the others or the workflow itself.

Runs inside .github/workflows/mega_scheduled.yml (daily at 00:30 UTC / 05:30 PKT).
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
STATE = ROOT / "state" / "mega_queue.json"

# Declared order of the series. Already-Done variants (M001 saga + done list) are skipped forever.
PENDING = ["M002", "M003"]

def log(*a):
    from datetime import datetime
    print(f"[{datetime.now():%H:%M:%S}]", *a, flush=True)

def load_state():
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding="utf-8-sig"))
        except Exception:
            log("mega_queue.json unreadable - treating as empty (won't re-upload M001 duplicate;")
            return {"done": ["M001"]}
    return {"done": ["M001"]}  # M001 already uploaded (https://youtu.be/_a5T4ltsz_8)

def save_state(done):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps({"done": sorted(set(done))}, indent=2))
    tmp.replace(STATE)
    log(f"mega_queue state -> done={sorted(set(done))}")

def attempt_variant(variant):
    env = dict(os.environ, MEGA_VARIANT=variant, UPLOAD="1", MEGA_SKIP_LLM="0")
    log(f"=== attempting MEGA variant {variant} ===")
    r = subprocess.run([sys.executable, str(ROOT / "make_mega_video.py")], env=env, cwd=str(ROOT))
    return r.returncode == 0

def main():
    state = load_state()
    done = set(state.get("done", []))
    log(f"mega_queue - done={sorted(done)}")
    pending = [v for v in PENDING if v not in done]
    if not pending:
        log("nothing pending - all mega variants uploaded. Healthy.")
        return 0
    for variant in pending:
        try:
            ok = attempt_variant(variant)
        except Exception as e:
            log(f"{variant}: watchdog exception (will retry tomorrow): {e}")
            continue
        if ok:
            done.add(variant)
            save_state(done)
            log(f"{variant} uploaded successfully and marked done")
        else:
            log(f"{variant} failed - will retry on next daily run")
    return 0

if __name__ == "__main__":
    sys.exit(main())
