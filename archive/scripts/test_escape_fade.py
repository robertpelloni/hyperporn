#!/usr/bin/env python3
"""Find a working periodic fade expression (comma escaping)."""
import subprocess
from pathlib import Path

work = Path(r"C:\Users\hyper\Videos\sissymaker")
src = work / "intermediates" / "wet_gop26.mp4"

def yavg(path, t):
    png = work / "yy.png"
    subprocess.run(["ffmpeg", "-y", "-ss", str(t), "-i", str(path), "-frames:v", "1", str(png)], capture_output=True)
    r = subprocess.run(
        ["ffmpeg", "-v", "info", "-i", str(png), "-vf",
         "signalstats,metadata=print:key=lavfi.signalstats.YAVG", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    for ln in (r.stderr + r.stdout).splitlines():
        if "YAVG" in ln:
            return ln.split("=")[-1].strip()
    return "?"

tests = [
    ("lut_mod_esc", "lutyuv=y='val*mod(n\\,60)'"),
    ("lut_if_esc", "lutyuv=y='val*if(lt(n\\,30)\\,0.2\\,1)'"),
    ("lut_if_mod_esc", "lutyuv=y='val*if(lt(mod(n\\,60)\\,4)\\,0.2\\,1)'"),
    ("geq_mod_esc", "geq=lum='p(X,Y)*mod(N\\,60)/60':cb='p(X,Y)':cr='p(X,Y)'"),
    ("geq_if_esc", "geq=lum='p(X,Y)*if(lt(mod(T\\,1)\\,0.08)\\,0.1\\,1)':cb='p(X,Y)':cr='p(X,Y)'"),
    ("lut_pct", "lutyuv=y='val*abs(sin(PI*t*2))'"),
]

for label, vf in tests:
    out = work / f"tc_{label}.mp4"
    if out.exists():
        out.unlink()
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-t", "1.5", "-i", str(src), "-vf", vf,
         "-frames:v", "45", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28", str(out)],
        capture_output=True, text=True,
    )
    ok = r.returncode == 0 and out.exists()
    print(label, "rc", r.returncode, "ok", ok, flush=True)
    if not ok:
        err = (r.stderr or "").strip().splitlines()
        print("   ", err[-2:], flush=True)
        continue
    print("   Y@0.1", yavg(out, 0.1), "Y@0.7", yavg(out, 0.7), flush=True)

print("ESCAPE_TESTS_DONE", flush=True)
