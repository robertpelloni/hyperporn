#!/usr/bin/env python3
"""Compare fade method speeds on 30s samples."""
import subprocess, time
from pathlib import Path

work = Path(r"C:\Users\hyper\Videos\sissymaker")
src = work / "Ajja_Liveset3h_Sissymaker_WetDream_14BEATS_60fps.mp4"

def timed(cmd, label):
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True)
    dt = time.time() - t0
    print(f"{label} rc={r.returncode} sec={dt:.1f}", flush=True)
    if r.returncode != 0:
        print(" ", (r.stderr or "").strip().splitlines()[-3:], flush=True)
    return dt, r.returncode

# 1) baseline: plain re-encode (no filter)
out = work / "t_base.mp4"
timed(["ffmpeg","-y","-hide_banner","-loglevel","error","-t","30","-i",str(src),
       "-c:v","libx264","-preset","ultrafast","-crf","24","-an",str(out)], "baseline_ultrafast")

# 2) loop-filter mask + yuv multiply (fast path, may green - just for speed)
mask = work / "mask_p360.mp4"
out = work / "t_blend_yuv.mp4"
fc = "[0:v][1:v]loop=loop=9999:size=360:start=0[msk];[0:v][msk]blend=all_mode=multiply[v]"
# simpler: stream_loop mask
fc2 = "[0:v][1:v]blend=all_mode=multiply[v]"
timed(["ffmpeg","-y","-hide_banner","-loglevel","error","-t","30","-i",str(src),
       "-stream_loop","-1","-i",str(mask),
       "-filter_complex","[0:v][1:v]blend=all_mode=multiply[v]","-map","[v]",
       "-c:v","libx264","-preset","ultrafast","-crf","24","-an",str(out)], "blend_yuv_ultrafast")

# 3) gbrp multiply
out = work / "t_blend_rgb.mp4"
timed(["ffmpeg","-y","-hide_banner","-loglevel","error","-t","30","-i",str(src),
       "-stream_loop","-1","-i",str(mask),
       "-filter_complex","[0:v]format=gbrp[a];[1:v]format=gbrp[m];[a][m]blend=all_mode=multiply,format=yuv420p[v]",
       "-map","[v]","-c:v","libx264","-preset","ultrafast","-crf","24","-an",str(out)], "blend_rgb_ultrafast")

# 4) alphamerge onto black
out = work / "t_alpha.mp4"
timed(["ffmpeg","-y","-hide_banner","-loglevel","error","-t","30","-i",str(src),
       "-stream_loop","-1","-i",str(mask),
       "-filter_complex","[0:v][1:v]alphamerge[a];color=c=black:s=1280x720:r=60[bg];[bg][a]overlay=shortest=1[v]",
       "-map","[v]","-c:v","libx264","-preset","ultrafast","-crf","24","-an",str(out)], "alphamerge_overlay")

# 5) just filter, copy codec? no. time geq 10s only
out = work / "t_geq10.mp4"
timed(["ffmpeg","-y","-hide_banner","-loglevel","error","-t","10","-i",str(src),
       "-vf","geq=lum='p(X,Y)*if(lt(mod(T\\,6.0)\\,0.07)\\,mod(T\\,6.0)/0.07\\,1)':cb='p(X,Y)':cr='p(X,Y)'",
       "-c:v","libx264","-preset","ultrafast","-crf","24","-an",str(out)], "geq_10s")

print("SPEED_COMPARE_DONE", flush=True)
