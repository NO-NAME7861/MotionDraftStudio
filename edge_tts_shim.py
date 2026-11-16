"""
edge_tts_shim.py - drop-in replacement for `python -m edge_tts ...`.

Calls edge_tts as a subprocess first; on failure, falls back to gTTS (Google built-in).
Used when Microsoft rate-limits GitHub Actions IPs.

Args (matches edge_tts API):
  --file FILE          text file to read
  --write-media PATH   mp3 output
  --write-subtitles P  srt output (optional)
  --voice VOICE        edge_tts voice name (ignored by gTTS fallback)
  --rate RATE          like -12% (ignored by gTTS fallback)
"""
import sys
import subprocess
import argparse
import pathlib
import re
import time


def edge_attempt(args):
    cmd = [sys.executable, "-m", "edge_tts",
           "--file", args.file,
           "--write-media", args.write_media]
    if args.write_subtitles:
        cmd += ["--write-subtitles", args.write_subtitles]
    if args.voice:
        cmd += ["--voice", args.voice]
    if args.rate:
        cmd += [f"--rate={args.rate}"]
    return subprocess.run(cmd, capture_output=True, text=True)


def gtts_fallback(args):
    from gtts import gTTS
    text = pathlib.Path(args.file).read_text(encoding="utf-8")
    mp3_path = args.write_media
    words = text.split()
    chunks = []
    cur, cur_len = [], 0
    for w in words:
        if cur_len + len(w) + 1 > 3000:
            chunks.append(" ".join(cur)); cur, cur_len = [], 0
        cur.append(w); cur_len += len(w) + 1
    if cur:
        chunks.append(" ".join(cur))
    if not chunks:
        chunks = [text]
    out = b""
    for i, chunk in enumerate(chunks):
        print(f"gtts chunk {i+1}/{len(chunks)} ({len(chunk)} chars)", flush=True)
        for attempt in range(3):
            try:
                tts = gTTS(text=chunk, lang="hi", slow=False)
                from io import BytesIO
                buf = BytesIO(); tts.write_to_fp(buf); out += buf.getvalue(); break
            except Exception as e:
                print(f"  attempt {attempt+1} fail: {str(e)[:100]}")
                time.sleep(2)
        else:
            raise RuntimeError("gTTS chunk failed")
    pathlib.Path(mp3_path).write_bytes(out)
    print(f"wrote {mp3_path} ({len(out)} bytes)", flush=True)
    if args.write_subtitles:
        # simple word-based SRT
        srt_path = args.write_subtitles
        import math
        words_total = len(words)
        # rough duration estimate 150 wpm
        approx_secs = max(60, int(words_total / 2.5))
        per_chunk = approx_secs / len(chunks)
        lines = []
        t = 0.0
        for i, chunk in enumerate(chunks):
            wcount = len(chunk.split())
            dur = per_chunk
            lines.append(f"{i+1}\n"
                         f"{_hms(t)} --> {_hms(t + dur)}\n"
                         f"{chunk}\n\n")
            t += dur
        pathlib.Path(srt_path).write_text("\n".join(lines), encoding="utf-8")

def _hms(s):
    h, r = divmod(int(s), 3600); m, sec = divmod(r, 60); ms = int((s - int(s)) * 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", required=True)
    p.add_argument("--write-media", required=True)
    p.add_argument("--write-subtitles", default="")
    p.add_argument("--voice", default="")
    p.add_argument("--rate", default="")
    args = p.parse_args()
    r = edge_attempt(args)
    print("edge-TTS exit:", r.returncode, r.stderr[-150:] if r.stderr else "")
    if r.returncode == 0:
        return
    print("falling back to gTTS...")
    gtts_fallback(args)

if __name__ == "__main__":
    main()
