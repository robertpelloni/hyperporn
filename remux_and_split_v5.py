#!/usr/bin/env python3
"""Remux the alt-audio 2GB with the v5 hypnoshit bed (video copy, audio re-mix),
then split into 4 pieces each < 512MB.

Stage 1: ffmpeg -c:v copy + audio mix (music_bed*0.70 + hypo_mix_v5*0.95)
         -> ハイパーポルノ_alt_v5.mp4  (~1.9GB)
Stage 2: -f segment keyframe-aligned -c copy -> 4 pieces ~475MB each
"""
import subprocess, sys
from pathlib import Path

# Windows consoles default to cp1252; printing Japanese filenames crashes.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

S = Path(r"C:\Users\hyper\Videos\sissymaker")
SRC_2GB = S / "ハイパーポルノ.mp4"          # existing alt-audio 2GB (video reused)
MUSIC = S / "alt_audio_rg" / "music_bed.m4a"
HYPO = S / "hypo_mix_v5.m4a"
OUT = S / "ハイパーポルノ_alt_v5.mp4"
PIECE_PREFIX = "ハイパーポルノ_alt_v5_p"

def log(m):
    print(m, flush=True)

def probe(p):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
        capture_output=True, text=True, check=True)
    return float(r.stdout.strip())

for p in (SRC_2GB, MUSIC, HYPO):
    if not p.exists():
        log(f"MISSING {p}")
        sys.exit(1)

# ---- stage 1: remux ----
if not (OUT.exists() and OUT.stat().st_size > 1_800_000_000):
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(SRC_2GB), "-i", str(MUSIC), "-i", str(HYPO),
        "-map", "0:v:0",
        "-filter_complex",
        # hyp v5 is +4.3dB hotter than v4 (compressor makeup), so 0.95*10^(-4.3/20)
        # ~= 0.58 keeps the exact same mus/hyp balance as the v6 mix.
        "[1:a]volume=0.70[mus];[2:a]volume=0.58[hyp];"
        "[mus][hyp]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
        "alimiter=limit=0.95[aout]",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(OUT),
    ]
    log("STAGE 1 remux start")
    r = subprocess.run(cmd, capture_output=True, text=True)
    log(f"STAGE 1 rc={r.returncode}")
    if r.returncode != 0:
        log(r.stderr[-800:])
        sys.exit(1)
    log(f"remux done {OUT.name} {OUT.stat().st_size/1e6:.1f}MB")
else:
    log("stage 1 output exists, skipping remux")

dur = probe(OUT)
seg = dur / 4.0
log(f"duration={dur:.1f}s seg={seg:.1f}s")

# ---- stage 2: split into 4 keyframe-aligned pieces ----
# delete old pieces
for f in S.glob(f"{PIECE_PREFIX}*.mp4"):
    f.unlink()

cmd = [
    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
    "-i", str(OUT),
    "-map", "0", "-c", "copy",
    "-f", "segment",
    "-segment_time", f"{seg:.3f}",
    "-reset_timestamps", "1",
    "-movflags", "+faststart",
    str(S / f"{PIECE_PREFIX}%d.mp4"),
]
log("STAGE 2 split start")
r = subprocess.run(cmd, capture_output=True, text=True)
log(f"STAGE 2 rc={r.returncode}")
if r.returncode != 0:
    log(r.stderr[-800:])
    sys.exit(1)

ok = True
for f in sorted(S.glob(f"{PIECE_PREFIX}*.mp4")):
    sz = f.stat().st_size
    d = probe(f)
    flag = "OK " if sz < 512_000_000 else "TOO BIG"
    if sz >= 512_000_000:
        ok = False
    log(f"{flag} {f.name} {sz/1e6:.1f}MB {d:.1f}s")

log("SPLIT_ALL_OK" if ok else "SPLIT_SIZE_FAIL")
sys.exit(0 if ok else 1)
