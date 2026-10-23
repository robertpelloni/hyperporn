#!/usr/bin/env python3
"""Speed-test geq periodic fade on 30s of the clean 14BEATS liveset."""
import subprocess, time
from pathlib import Path

work = Path(r"C:\Users\hyper\Videos\sissymaker")
src = work / "Ajja_Liveset3h_Sissymaker_WetDream_14BEATS_60fps.mp4"
out = work / "t_geq_speed.mp4"

P, FI, FO = 6.0, 0.07, 0.10
vf = (
    f"geq=lum='p(X,Y)*if(lt(mod(T\\,{P})\\,{FI})\\,mod(T\\,{P})/{FI}\\,"
    f"if(gt(mod(T\\,{P})\\,{P-FO})\\,({P}-mod(T\\,{P}))/{FO}\\,1))':"
    f"cb='p(X,Y)':cr='p(X,Y)'"
)
print("VF", vf, flush=True)

t0 = time.time()
r = subprocess.run(
    ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
     "-t", "30", "-i", str(src),
     "-vf", vf,
     "-c:v", "libx264", "-preset", "ultrafast", "-crf", "24",
     "-an", str(out)],
    capture_output=True, text=True,
)
dt = time.time() - t0
print("rc", r.returncode, "sec", round(dt, 1), "size", out.stat().st_size if out.exists() else 0, flush=True)
if r.returncode != 0:
    print((r.stderr or "")[-400:], flush=True)
else:
    # expected 3h / 30s * dt
    full = 10774 / 30 * dt
    print(f"EST_FULL_HOURS {full/3600:.2f}", flush=True)
    # sample near a cut (t=6.0 is boundary -> should be dark) and mid-clip
    for label, t in (("mid_clip", 3.0), ("at_cut", 5.98), ("after_cut", 6.05)):
        png = work / "gs.png"
        subprocess.run(["ffmpeg", "-y", "-ss", str(t), "-i", str(out), "-frames:v", "1", str(png)], capture_output=True)
        rr = subprocess.run(
            ["ffmpeg", "-v", "info", "-i", str(png), "-vf",
             "signalstats,metadata=print:key=lavfi.signalstats.YAVG", "-f", "null", "-"],
            capture_output=True, text=True,
        )
        y = [ln.split("=")[-1] for ln in (rr.stderr + rr.stdout).splitlines() if "YAVG" in ln]
        print(label, "Y", y, flush=True)
print("SPEED_TEST_DONE", flush=True)
