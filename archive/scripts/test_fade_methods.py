#!/usr/bin/env python3
"""Find a periodic fade-to-black that preserves chroma."""
import subprocess
from pathlib import Path

work = Path(r"C:\Users\hyper\Videos\sissymaker")
src = work / "intermediates" / "wet_gop26.mp4"
FPS = 60

def run(cmd, label):
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(label, "rc", r.returncode, flush=True)
    if r.returncode != 0:
        err = (r.stderr or "").strip().splitlines()
        print("  ", err[-4:] if err else "no err", flush=True)
    return r.returncode == 0

def yavg(path, t):
    png = work / "yav.png"
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

# 1) plain lutyuv constant
out = work / "t_lut_half.mp4"
if run(["ffmpeg","-y","-hide_banner","-loglevel","error","-t","1","-i",str(src),
        "-vf","lutyuv=y=val*0.5","-frames:v","30","-c:v","libx264","-preset","ultrafast","-crf","28",str(out)],
       "lutyuv_half"):
    print("  YAVG", yavg(out, 0.5), flush=True)

# 2) lutyuv with unescaped commas inside single quotes
out = work / "t_lut_mod.mp4"
vf = "lutyuv=y='val*mod(n,60)/60'"
if run(["ffmpeg","-y","-hide_banner","-loglevel","error","-t","2","-i",str(src),
        "-vf",vf,"-frames:v","60","-c:v","libx264","-preset","ultrafast","-crf","28",str(out)],
       "lutyuv_mod_commas"):
    print("  YAVG t=0.1", yavg(out, 0.1), "t=0.9", yavg(out, 0.9), flush=True)

# 3) geq luma-only with T (timestamp), no comma math via sin
#    factor = 0.5+0.5*sin(2*pi*T*1)  => smooth pulse at 1 Hz
out = work / "t_geq_sin.mp4"
vf = "geq=lum='p(X,Y)*(0.15+0.85*abs(sin(2*PI*T)))':cb='p(X,Y)':cr='p(X,Y)'"
if run(["ffmpeg","-y","-hide_banner","-loglevel","error","-t","2","-i",str(src),
        "-vf",vf,"-frames:v","60","-c:v","libx264","-preset","ultrafast","-crf","28",str(out)],
       "geq_sin"):
    print("  YAVG peak", yavg(out, 0.25), "trough", yavg(out, 0.5), flush=True)

# 4) RGB multiply with looping mask (chroma-safe)
#    build 60-frame mask: black at edges, white in middle
mask = work / "t_mask.mp4"
run(["ffmpeg","-y","-hide_banner","-loglevel","error",
     "-f","lavfi","-i","color=white:s=1280x720:r=60:d=1",
     "-vf","fade=t=in:st=0:d=0.08:color=black,fade=t=out:st=0.84:d=0.16:color=black",
     "-frames:v","60","-c:v","libx264","-preset","ultrafast","-crf","18",str(mask)], "make_mask")

out = work / "t_blend_rgb.mp4"
vf = "setpts=N/60/TB,format=gbrp[a];[a]split[a1][a2];[a2]loop=loop=999:size=60:start=0[msk];[a1][msk]blend=all_mode=multiply,format=yuv420p"
# actually need inputs properly - use filter_complex
fc = "[0:v]setpts=N/60/TB,format=gbrp[a1];[1:v]format=gbrp,loop=loop=999:size=60:start=0[msk];[a1][msk]blend=all_mode=multiply:shortest=1,format=yuv420p[v]"
if run(["ffmpeg","-y","-hide_banner","-loglevel","error","-t","2","-i",str(src),
        "-stream_loop","-1","-i",str(mask),
        "-filter_complex",fc,"-map","[v]","-frames:v","60",
        "-c:v","libx264","-preset","ultrafast","-crf","28",str(out)],
       "blend_rgb"):
    # sample just after a fade-out (~frame 55/60 = 0.92s) vs mid (0.5s)
    print("  YAVG mid", yavg(out, 0.5), "near_cut", yavg(out, 0.92), flush=True)

print("FADE_TESTS_DONE", flush=True)
