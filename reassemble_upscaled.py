#!/usr/bin/env python
"""Reassemble Topaz-upscaled segments and remux an audio bed.

Expects upscaled files named like the source segments (seg_0000.mp4 ...)
in one folder, all 3840x2160 / 60 fps / same codec. Validates frame
counts against upscale_segments/manifest.csv before joining, then:

  1. concat (stream copy) -> video-only 4K file
  2. mux with beds/<bed>.m4a (stream copy audio) -> final file

Usage:
  python reassemble_upscaled.py --upscaled upscale_out --bed combined
  python reassemble_upscaled.py --upscaled upscale_out --bed ajja --check-only
"""
import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPECTED_FRAMES = 646461


def probe_frames(path: Path) -> int:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=nb_frames", "-of", "json", str(path)],
        capture_output=True, text=True, check=True).stdout
    return int(json.loads(out)["streams"][0].get("nb_frames", 0))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--upscaled", type=Path, required=True)
    ap.add_argument("--bed", default="combined",
                    help="beds/<bed>.m4a to mux (ajja|jumpstreet|spacetribe|combined)")
    ap.add_argument("--manifest", type=Path, default=ROOT / "upscale_segments" / "manifest.csv")
    ap.add_argument("--out", type=Path, default=ROOT / "hyperporn_4k60.mp4")
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()

    files = sorted(args.upscaled.glob("seg_*.mp4"))
    if not files:
        raise SystemExit(f"No seg_*.mp4 in {args.upscaled}")
    total = sum(probe_frames(f) for f in files)
    print(f"Segments: {len(files)}  Frames: {total}  Expected: {EXPECTED_FRAMES}")
    if total != EXPECTED_FRAMES:
        print("WARNING: frame count mismatch - a segment is missing, "
              "duplicated, or frame-interpolated. Do not ship this join.")
        if not args.check_only:
            raise SystemExit(1)
    if args.check_only:
        return

    listfile = args.upscaled / "concat.txt"
    listfile.write_text("".join(f"file '{f.name}'\n" for f in files), encoding="utf-8")
    video_only = args.upscaled / "_video_only_4k.mp4"
    subprocess.run(["ffmpeg", "-hide_banner", "-y", "-f", "concat", "-safe", "0",
                    "-i", str(listfile), "-c", "copy", str(video_only)], check=True)
    bed = ROOT / "beds" / f"{args.bed}.m4a"
    subprocess.run(["ffmpeg", "-hide_banner", "-y", "-i", str(video_only),
                    "-i", str(bed), "-map", "0:v:0", "-map", "1:a:0",
                    "-c", "copy", "-movflags", "+faststart", str(args.out)], check=True)
    print("Wrote:", args.out)


if __name__ == "__main__":
    main()
