"""next_id.py — print the next episode id for a state file.

Usage: python next_id.py state/episodes_rezero.json R001

Used by .github/workflows/*.yml to avoid inlining Python in YAML
(the inline version broke with IndentationError because of YAML block
indentation stripping).
"""
import json
import pathlib
import sys

state_path = pathlib.Path(sys.argv[1])
fallback = sys.argv[2] if len(sys.argv) > 2 else "S001"

if state_path.exists():
    s = json.loads(state_path.read_text(encoding="utf-8"))
else:
    s = {"next_id": fallback}

print(s.get("next_id", fallback))
