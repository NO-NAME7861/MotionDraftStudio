"""advance_state.py - advance a series state file after a successful upload.

Reads the series CSV for the canonical episode order, appends the uploaded
episode to "done" and sets "next_id" to the following episode in the CSV.

Env:
  EPISODE_ID    episode that was just uploaded
  EPISODES_CSV  series csv (default: episodes_godsystem.csv)
  STATE_FILE    state json (default: state/episodes_godsystem.json)
"""
import csv
import json
import os
import pathlib

ep = os.environ.get("EPISODE_ID", "").strip()
csv_path = os.environ.get("EPISODES_CSV", "episodes_godsystem.csv")
state_path = pathlib.Path(os.environ.get("STATE_FILE", "state/episodes_godsystem.json"))

with open(csv_path, encoding="utf-8") as f:
    ids = [r["id"] for r in csv.DictReader(f)]

if not ids:
    raise SystemExit(f"no episode ids in {csv_path}")
if ep not in ids:
    raise SystemExit(f"EPISODE_ID {ep} not in {csv_path}")

state = {"next_id": ids[0], "done": []}
if state_path.exists():
    state = json.loads(state_path.read_text(encoding="utf-8"))

done = state.setdefault("done", [])
if ep not in done:
    done.append(ep)

idx = ids.index(ep)
state["next_id"] = ids[idx + 1] if idx + 1 < len(ids) else ep

state_path.parent.mkdir(parents=True, exist_ok=True)
state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
print("state ->", state)
