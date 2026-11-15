#!/usr/bin/env python
"""Cut the 3h master into very short, Topaz-ready segments.

Why this shape:
- Master is 1280x720, 60 fps, 10,774.35 s, 646,461 frames.
- Keyframes land every 26 frames (0.4333 s), so stream-copy cutting is
  frame-exact at any segment length. No re-encode, no quality loss.
- Video is identical in every mix (only the audio bed differs), so cut
  and upscale the video ONCE, then remux whichever bed you want.
- Segments are video-only. Audio stays as beds/*.m4a and is muxed back
  once at reassembly, so segment joins cannot drift the audio.

Usage:
  python cut_for_upscale.py --seconds 10            # full run (~1078 files)
  python cut_for_upscale.py --seconds 10 --limit 6  # pilot: first ~60 s
  python cut_for_upscale.py --seconds 30            # fewer, larger segments

Output: upscale_segments/seg_0000.mp4 ... plus manifest.csv with
index,file,frames,duration,width,height (probed, not assumed).
Feed the whole upscale_segments folder to Topaz Video AI as one batch:
Proteus, 3x to 3840x2160, frame interpolation OFF (already 60 fps).
"""
import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def find_master() -> Path:
    for pat in ("*_combined.mp4", "*.mp4"):
        for p in sorted(ROOT.glob(pat)):
            if p.stat().st_size > 1_000_000_000:  # the ~1.8 GB masters
                return p
    raise SystemExit("No ~1.8 GB master .mp4 found in workspace root.")


def probe(path: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,nb_frames,duration",
         "-of", "json", str(path)],
        capture_output=True, text=True, check=True).stdout
    s = json.loads(out)["streams"][0]
    return {"frames": int(s.get("nb_frames", 0)),
            "duration": round(float(s.get("duration", 0)), 3),
            "width": s["width"], "height": s["height"]}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, default=10.0,
                    help="target segment length (snaps to keyframes)")
    ap.add_argument("--limit", type=int, default=0,
                    help="only cut the first N segments (pilot)")
    ap.add_argument("--master", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=ROOT / "upscale_segments")
    args = ap.parse_args()

    master = args.master or find_master()
    args.out.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-hide_banner", "-y", "-i", str(master),
           "-map", "0:v:0", "-an", "-c:v", "copy",
           "-f", "segment", "-segment_time", str(args.seconds),
           "-reset_timestamps", "1", "-segment_format", "mp4"]
    if args.limit:
        # -t as an output option caps total duration before segmenting.
        cmd += ["-t", str(args.seconds * args.limit)]
    cmd += [str(args.out / "seg_%04d.mp4")]
    print("Master:", master.name.encode("ascii", "replace").decode())
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)

    files = sorted(args.out.glob("seg_*.mp4"))
    manifest = args.out / "manifest.csv"
    with manifest.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["index", "file", "frames", "duration", "width", "height", "upscaled"])
        total = 0
        for i, f in enumerate(files):
            info = probe(f)
            total += info["frames"]
            w.writerow([i, f.name, info["frames"], info["duration"],
                        info["width"], info["height"], ""])
    print(f"Segments: {len(files)}  Total frames: {total} (master: 646461)")
    print("Manifest:", manifest)


if __name__ == "__main__":
    main()
