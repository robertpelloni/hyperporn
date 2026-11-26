#!/usr/bin/env python3
import subprocess
from pathlib import Path

# Test 1: simple if fade-in
vf = "lutyuv=y=if(lt(n,5),val*n/5,val)"
r = subprocess.run([
    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
    "-f", "lavfi", "-i", "testsrc=size=320x240:rate=30:duration=1",
    "-vf", vf, "-frames:v", "15",
    r"C:\Users\hyper\Videos\sissymaker\fade_test4.mp4",
], capture_output=True, text=True)
p = Path(r"C:\Users\hyper\Videos\sissymaker\fade_test4.mp4")
print("test_if", r.returncode, p.stat().st_size if p.exists() else 0, r.stderr[-200:])

# Test 2: periodic fade in+out using min via if
vf2 = "lutyuv=y=if(lt(mod(n,30),6),val*mod(n,30)/6,if(gt(mod(n,30),23),val*(30-mod(n,30))/6,val))"
r = subprocess.run([
    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
    "-f", "lavfi", "-i", "testsrc=size=320x240:rate=30:duration=2",
    "-vf", vf2, "-frames:v", "60",
    r"C:\Users\hyper\Videos\sissymaker\fade_test5.mp4",
], capture_output=True, text=True)
p = Path(r"C:\Users\hyper\Videos\sissymaker\fade_test5.mp4")
print("test_periodic", r.returncode, p.stat().st_size if p.exists() else 0, r.stderr[-200:])
