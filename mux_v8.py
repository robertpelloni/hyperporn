#!/usr/bin/env python3
"""Mux liveset60_v8/video_fade_v8.mp4 with the AutoDJ mix (autodj_mix.flac).
Audio is padded/trimmed to exactly the video duration, AAC 192k/48k.
Output: hyperporn_v8_autodj.mp4. Verifies frames/duration/streams."""
import subprocess, sys, json
from pathlib import Path

WORK = Path(__file__).resolve().parent
VIDEO = WORK / "liveset60_v8" / "video_fade_v8.mp4"
AUDIO = WORK / "autodj_mix.flac"
OUT = WORK / "hyperporn_v8_autodj.mp4"
TARGET = 10774.35

def probe(p):
    r = subprocess.run(["ffprobe","-v","error","-show_entries",
                        "stream=codec_type,codec_name,width,height,avg_frame_rate,nb_frames",
                        "-show_entries","format=duration",
                        "-of","json",str(p)], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)

def main():
    if not VIDEO.exists(): print("missing video_fade_v8.mp4"); return 1
    if not AUDIO.exists(): print("missing autodj_mix.flac"); return 1
    cmd = ["ffmpeg","-y","-hide_banner","-loglevel","error",
           "-i",str(VIDEO),"-i",str(AUDIO),
           "-filter_complex",f"[1:a]apad,atrim=0:{TARGET:.3f},asetpts=N/SR/TB,aresample=48000[a]",
           "-map","0:v","-map","[a]","-c:v","copy","-c:a","aac","-b:a","192k",
           "-movflags","+faststart",str(OUT)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("mux FAIL", (r.stderr or "")[-400:]); return 1
    info = probe(OUT)
    dur = float(info["format"]["duration"])
    v = next(s for s in info["streams"] if s["codec_type"]=="video")
    a = next(s for s in info["streams"] if s["codec_type"]=="audio")
    print(f"OUT dur={dur:.3f} video={v['codec_name']} {v['width']}x{v['height']} "
          f"fps={v['avg_frame_rate']} frames={v.get('nb_frames')} audio={a['codec_name']}")
    ok = abs(dur - TARGET) < 0.6 and int(v.get("nb_frames","0")) == 646461
    print("VERIFY", "PASS" if ok else "FAIL")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
