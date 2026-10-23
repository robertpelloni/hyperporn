#!/usr/bin/env python3
"""Test no-comma lutyuv/geq periodic fade expressions (luma only)."""
import subprocess
from pathlib import Path

work = Path(r"C:\Users\hyper\Videos\sissymaker")
src = work / "intermediates" / "wet_gop26.mp4"

def yuvavgs(path, t):
    png = work / "ya.png"
    subprocess.run(["ffmpeg", "-y", "-ss", str(t), "-i", str(path), "-frames:v", "1", str(png)], capture_output=True)
    out = {}
    for k in ("YAVG", "UAVG", "VAVG"):
        r = subprocess.run(
            ["ffmpeg", "-v", "info", "-i", str(png), "-vf",
             f"signalstats,metadata=print:key=lavfi.signalstats.{k}", "-f", "null", "-"],
            capture_output=True, text=True,
        )
        for ln in (r.stderr + r.stdout).splitlines():
            if k in ln:
                out[k] = ln.split("=")[-1].strip()
    return out

tests = [
    # (label, vf)
    ("lut_sin", "lutyuv=y='val*abs(sin(PI*t*2))'"),
    ("lut_sin_pow", "lutyuv=y='val*abs(sin(PI*t*2))^8'"),
    ("lut_sin_sq", "lutyuv=y='val*abs(sin(PI*t*2))*abs(sin(PI*t*2))*abs(sin(PI*t*2))*abs(sin(PI*t*2))'"),
    ("geq_sin4", "geq=lum='p(X,Y)*abs(sin(PI*T*2))*abs(sin(PI*T*2))*abs(sin(PI*T*2))*abs(sin(PI*T*2))':cb='p(X,Y)':cr='p(X,Y)'"),
]

for label, vf in tests:
    out = work / f"t_{label}.mp4"
    if out.exists():
        out.unlink()
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-t", "2", "-i", str(src), "-vf", vf,
         "-frames:v", "60", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
         str(out)],
        capture_output=True, text=True,
    )
    print(label, "rc", r.returncode, "size", out.stat().st_size if out.exists() else 0, flush=True)
    if r.returncode != 0:
        print("  err", (r.stderr or "").strip().splitlines()[-3:], flush=True)
        continue
    # t=0.25 should be near peak of abs(sin(PI*t*2))=1; t=0.5 near zero
    print("  t=0.25", yuvavgs(out, 0.25), flush=True)
    print("  t=0.50", yuvavgs(out, 0.50), flush=True)

print("NO_COMMA_TESTS_DONE", flush=True)
