#!/usr/bin/env python
"""Upscale every seg_*.mp4 with the extracted Topaz ffmpeg (tvai_up).

Uses the free redistributable runtime extracted from TopazVideo-1.2.1.msi:
no GUI, no install. Sets TVAI_MODEL_DIR (model .json definitions from the
extract) and TVAI_MODEL_DATA_DIR (downloaded .tz weights, writable).

Resumable: a segment whose output already probes at 3840x2160 with the
same frame count as its source is skipped.

Usage:
  python upscale_topaz.py --input upscale_pilot --output upscale_pilot_4k
  python upscale_topaz.py --model ahq-12 --device -1   # CPU instead of auto
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOPAZ_DIR = ROOT / "topaz-extract" / "PFiles" / "Topaz Labs LLC" / "Topaz Video"
MODEL_DIR = ROOT / "topaz-extract" / "Topaz Labs LLC" / "Topaz Video" / "models"
DATA_DIR = ROOT / "topaz-models"


def probe(path: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,nb_frames", "-of", "json", str(path)],
        capture_output=True, text=True).stdout
    try:
        s = json.loads(out)["streams"][0]
        return {"w": s["width"], "h": s["height"], "frames": int(s.get("nb_frames", 0))}
    except Exception:
        return {"w": 0, "h": 0, "frames": 0}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=ROOT / "upscale_segments")
    ap.add_argument("--output", type=Path, default=ROOT / "upscale_out")
    ap.add_argument("--model", default="prob-4")
    ap.add_argument("--device", default="-2", help="-2 auto, -1 CPU, 0 first GPU")
    ap.add_argument("--encoder", default="hevc_qsv",
                    help="Topaz ffmpeg has no libx264/x265; hevc_qsv uses the Intel iGPU")
    ap.add_argument("--quality", default="16",
                    help="QSV global_quality (lower=better) or CRF for sw encoders")
    args = ap.parse_args()

    ffmpeg = TOPAZ_DIR / "ffmpeg.exe"
    if not ffmpeg.exists():
        raise SystemExit(f"Topaz ffmpeg not found: {ffmpeg}")
    args.output.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    import os
    env = dict(os.environ)
    env["TVAI_MODEL_DIR"] = str(MODEL_DIR)
    env["TVAI_MODEL_DATA_DIR"] = str(DATA_DIR)
    env["PATH"] = str(TOPAZ_DIR) + os.pathsep + env.get("PATH", "")

    files = sorted(args.input.glob("seg_*.mp4"))
    print(f"{len(files)} segments, model={args.model} device={args.device}")
    for src in files:
        dst = args.output / src.name
        want = probe(src)
        if dst.exists() and probe(dst) == {"w": 3840, "h": 2160, "frames": want["frames"]}:
            print("skip", src.name)
            continue
        vf = f"tvai_up=model={args.model}:scale=0:w=3840:h=2160:device={args.device}"
        qopt = ["-global_quality", args.quality] if args.encoder.endswith("_qsv") else ["-crf", args.quality]
        cmd = [str(ffmpeg), "-hide_banner", "-y", "-i", str(src), "-vf", vf,
               "-c:v", args.encoder] + qopt + ["-pix_fmt", "yuv420p",
               "-r", "60", str(dst)]
        print("upscale", src.name, flush=True)
        r = subprocess.run(cmd, env=env)
        got = probe(dst) if dst.exists() else {"w": 0, "h": 0, "frames": 0}
        print(" ->", got, "exit", r.returncode)
        if got != {"w": 3840, "h": 2160, "frames": want["frames"]}:
            raise SystemExit(f"Segment failed verification: {src.name} {got} != {want}")


if __name__ == "__main__":
    main()
