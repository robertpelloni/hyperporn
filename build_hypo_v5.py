#!/usr/bin/env python3
"""Build hypo_mix_v5.m4a (attempt 2, correct): smooth the ~6:20 volume jump.

Fix vs attempt 1: afade=t=in zeroes ALL audio before st — it silenced the
first 380s. Instead, split the audio into three regions and apply the
2s gain ramp ONLY to the 3s slice around the onset (380.5-383.5s, where
the voice slams in at 381s after near-silence). Then gentle compressor +
limiter over the whole file (fast filters).
"""
import subprocess, sys
from pathlib import Path

S = Path(r"C:\Users\hyper\Videos\sissymaker")
src = S / "hypo_mix_v4.m4a"
out = S / "hypo_mix_v5.m4a"

fc = (
    # region split: pre / onset slice / post
    "[0:a]asplit=3[pre][mid][post];"
    "[pre]atrim=0:380.5,asetpts=PTS-STARTPTS[pre2];"
    # 2s gentle gain ramp 0.4 -> 1.0 across the onset (eval=frame over only 3s = cheap)
    "[mid]atrim=380.5:383.5,asetpts=PTS-STARTPTS,"
    "volume='if(lt(t,2), 0.4+0.3*t, 1)':eval=frame[mid2];"
    "[post]atrim=383.5,asetpts=PTS-STARTPTS[post2];"
    "[pre2][mid2][post2]concat=n=3:v=0:a=1,"
    # gentle dynamic smoothing + peak cap
    "acompressor=threshold=-20dB:ratio=2:attack=15:release=300:knee=8:makeup=3,"
    "alimiter=limit=0.7:level=false[out]"
)

cmd = [
    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
    "-i", str(src),
    "-filter_complex", fc,
    "-map", "[out]",
    "-c:a", "aac", "-b:a", "192k",
    str(out),
]
print("running ffmpeg...", flush=True)
r = subprocess.run(cmd, capture_output=True, text=True)
print("rc", r.returncode, flush=True)
if r.returncode != 0:
    print(r.stderr[-800:], flush=True)
    sys.exit(1)
print("OK", out.name, f"{out.stat().st_size/1e6:.1f}MB", flush=True)
