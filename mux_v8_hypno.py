#!/usr/bin/env python3
"""Optional hypno variant of the v8 master (music + hypno bed).

Default v8 master (mux_v8.py) is music-only. This variant mixes
autodj_mix.flac (0.70) with hypo_mix_v5.m4a (0.95) using the PIPELINE
section 4.3 rules: amix normalize=0, dropout_transition=0, alimiter 0.95.
Video is stream-copied; only the audio is encoded (AAC 320k).
Run only after liveset60_v8/video_fade_v8.mp4 exists.
Output: hyperporn_v8_hypno.mp4
"""
import subprocess, sys
from pathlib import Path

WORK = Path(__file__).resolve().parent
VIDEO = WORK / "liveset60_v8" / "video_fade_v8.mp4"
MUSIC = WORK / "autodj_mix.flac"
HYPNO = WORK / "hypo_mix_v5.m4a"
OUT = WORK / "hyperporn_v8_hypno.mp4"
TARGET = 10774.35

def main():
    for p in (VIDEO, MUSIC, HYPNO):
        if not p.exists():
            print(f"missing {p}"); return 1
    fc = ("[1:a]apad,atrim=0:{t},volume=0.70[mus];"
          "[2:a]atrim=0:{t},volume=0.95[hyp];"
          "[mus][hyp]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
          "alimiter=limit=0.95,aresample=48000[a]").format(t=TARGET)
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
           "-i", str(VIDEO), "-i", str(MUSIC), "-i", str(HYPNO),
           "-filter_complex", fc, "-map", "0:v", "-map", "[a]",
           "-c:v", "copy", "-c:a", "aac", "-b:a", "320k",
           "-movflags", "+faststart", str(OUT)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("mux FAIL", (r.stderr or "")[-400:]); return 1
    print(f"OK {OUT}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
