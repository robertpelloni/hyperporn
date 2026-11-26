import subprocess, sys, time
from pathlib import Path

SISSY = Path(r"C:\Users\hyper\Videos\sissymaker")
V2 = SISSY / "Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps_FADE_v2.mp4"
AUDIO = Path(r"C:\Users\hyper\Music\Ajja - 2026 - Dimension Festival NZ (live).mp3")
HYPO = SISSY / "hypo_mix.m4a"
OUT = SISSY / "Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps_FADE_v2b.mp4"

def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)

for p in (V2, AUDIO, HYPO):
    if not p.exists():
        sys.exit(f"missing {p}")

if OUT.exists():
    OUT.unlink()

fc = (
    "[0:a]volume=0.75[ajja];"
    "[1:a]volume=0.80[hyp];"
    "[ajja][hyp]amix=inputs=2:duration=first:dropout_transition=0,"
    "alimiter=limit=0.95[aout]"
)

log("remixing audio hyp=0.80 ...")
r = subprocess.run(
    ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
     "-i", str(AUDIO),
     "-i", str(HYPO),
     "-i", str(V2),
     "-filter_complex", fc,
     "-map", "2:v", "-map", "[aout]",
     "-c:v", "copy",
     "-c:a", "aac", "-b:a", "320k",
     "-t", "10774.336",
     str(OUT)],
    capture_output=True, text=True,
)
log(f"rc={r.returncode}")
if r.returncode != 0:
    log(r.stderr[-600:])
    sys.exit(1)
sz = OUT.stat().st_size / 1e6
log(f"DONE {OUT.name} {sz:.1f}MB")
