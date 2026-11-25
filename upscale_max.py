#!/usr/bin/env python3
"""Maximal-quality 1080p TRUE-60fps tier for source materials ONLY.

Per source clip in _sm/ + _ai/ (never _dup, never finished episodes),
one clip at a time, shortest first, 10 s segments, resumable:

  source frames -> Real-ESRGAN ncnn AI upscale toward 4K
    (realesr-animevideov3-x4 below 1080p; -x2 at 1080p..1440p;
     >=2160p sources skip ESRGAN - already 4K)
  -> lanczos DOWN to 1920x1080 (supersampling: the 4K pass exists
     only to make the 1080 downscale carry AI detail)
  -> TRUE 60 fps motion: minterpolate mci/aobmc/bidir (synthesized
     in-between frames, NOT fps duplication) for fps<59
  -> h264_nvenc CQ18 segment, concat, source audio AAC 192k.

Output: _max1080/<_sm|_ai>/<stem>_max1080p60.mp4 (1920x1080, 60 fps).

Measured on this GTX 1060 (2026-11-24): animevideov3-x4 ~2.2 s/frame
at 720p (x4plus ~20 s/frame - rejected, 9x slower for marginal gain);
minterpolate at 1080p ~1 fps output. Whole library (~1.1M source
frames) is a multi-week background grind - this script is the
resumable queue, not a promise of same-day completion. Segments and
clips verify frame-exact and skip on rerun. Aborts if G: < 5 GB free.
"""
import json, shutil, subprocess, sys, time
from pathlib import Path

WORK = Path(__file__).resolve().parent
FFD = WORK / "tools" / "ffmpeg-7.1.1-essentials_build" / "bin"
FF, FP = FFD / "ffmpeg.exe", FFD / "ffprobe.exe"
ESR = Path(r"C:\Users\hyper\workspace\hyperporn\comfy-pipeline\tools\realesrgan\realesrgan-ncnn-vulkan.exe")
OUT = WORK / "_max1080"
SEG_S = 10
MI = "minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1"

def log(m): print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)

def probe(p):
    r = subprocess.run([str(FP), "-v", "error", "-show_entries",
                        "stream=codec_type,width,height,avg_frame_rate,nb_frames",
                        "-show_entries", "format=duration", "-of", "json", str(p)],
                       capture_output=True, text=True)
    d = json.loads(r.stdout)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    num, _, den = v["avg_frame_rate"].partition("/")
    rate = float(num) / float(den or 1) if float(den or 1) else 0
    return {"dur": float(d["format"]["duration"]), "w": v["width"], "h": v["height"],
            "fps": rate, "frames": int(v.get("nb_frames") or 0)}

def done_ok(p, want_frames):
    if not p.exists():
        return False
    try:
        i = probe(p)
        return (i["w"] == 1920 and i["h"] == 1080
                and abs(i["fps"] - 60) < 0.5 and abs(i["frames"] - want_frames) <= 180)
    except Exception:
        return False

def seg_ok(p, want_frames):
    # Segment timestamps can drift on tiny tails; frames+res is the gate
    # (the final clip still gets the strict fps check in done_ok).
    if not p.exists():
        return False
    try:
        i = probe(p)
        return i["w"] == 1920 and i["h"] == 1080 and abs(i["frames"] - want_frames) <= 180
    except Exception:
        return False

def free_gb(): return shutil.disk_usage(WORK).free / 1e9

def enc_seg(inp_args, src_fps, seg_dur, seg):
    vf = ("scale=1920:1080:force_original_aspect_ratio=decrease:flags=lanczos,"
          "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p,"
          + (MI + "," if src_fps < 59 else "fps=60,")
          + "tpad=stop_mode=clone:stop_duration=2,setpts=N/60/TB")
    cmd = [str(FF), "-y", "-hide_banner", "-loglevel", "error", *inp_args,
           "-vf", vf, "-an", "-c:v", "h264_nvenc", "-preset", "p5",
           "-rc", "vbr", "-cq", "18", "-b:v", "0",
           "-frames:v", str(round(seg_dur * 60)), str(seg)]
    return subprocess.run(cmd, capture_output=True, text=True)

def run_clip(src, dst, info, clip_work):
    bounds = []
    t = 0.0
    while t < info["dur"] - 0.05:
        d = min(SEG_S, info["dur"] - t)
        if info["dur"] - (t + d) < 1.0:
            d = info["dur"] - t
        bounds.append((t, d)); t += d
    segs = []
    for si, (start, seg_dur) in enumerate(bounds):
        seg = clip_work / f"seg_{si:04d}.mp4"
        segs.append(seg)
        if seg_ok(seg, round(seg_dur * 60)):
            continue
        if free_gb() < 5:
            log("DISK LOW - abort"); return False
        if info["h"] >= 2000:  # already 4K: no ESRGAN, direct segment
            r = enc_seg(["-ss", f"{start:.3f}", "-i", str(src), "-t", f"{seg_dur:.3f}"],
                        info["fps"], seg_dur, seg)
            if r.returncode != 0 or not seg_ok(seg, round(seg_dur * 60)):
                log(f"seg FAIL {src.name} {si} {(r.stderr or '')[-200:]}"); return False
        else:
            fin, fout = clip_work / f"f{si}", clip_work / f"u{si}"
            for d in (fin, fout):
                if d.exists():
                    shutil.rmtree(d)
                d.mkdir(parents=True)
            r = subprocess.run([str(FF), "-y", "-hide_banner", "-loglevel", "error",
                                "-ss", f"{start:.3f}", "-i", str(src), "-t", f"{seg_dur:.3f}",
                                "-an", "-map", "0:v:0", str(fin / "f%05d.png")],
                               capture_output=True, text=True)
            if r.returncode != 0:
                log(f"extract FAIL {src.name} seg{si}"); return False
            src_frames = len(list(fin.glob("*.png")))
            scale = "4" if info["h"] < 1080 else "2"
            r = subprocess.run([str(ESR), "-i", str(fin), "-o", str(fout),
                                "-n", f"realesr-animevideov3-x{scale}", "-s", scale,
                                "-t", "256", "-g", "0", "-j", "1:1:1", "-f", "png"],
                               capture_output=True, text=True)
            up = len(list(fout.glob("*.png"))) if fout.exists() else 0
            if r.returncode != 0 or up != src_frames or src_frames == 0:
                log(f"esrgan FAIL {src.name} seg{si} {up}/{src_frames}"); return False
            r = enc_seg(["-framerate", f"{info['fps']:.6f}", "-i", str(fout / "f%05d.png")],
                        info["fps"], seg_dur, seg)
            shutil.rmtree(fin, ignore_errors=True); shutil.rmtree(fout, ignore_errors=True)
            if r.returncode != 0 or not seg_ok(seg, round(seg_dur * 60)):
                log(f"seg encode FAIL {src.name} seg{si} {(r.stderr or '')[-200:]}")
                return False
        log(f"  {src.name} seg {si+1}/{len(bounds)} ok (free {free_gb():.1f} GB)")
    listf = clip_work / "list.txt"
    with listf.open("w") as f:
        for s in segs:
            f.write(f"file '{s.resolve().as_posix()}'\n")
    tmp = clip_work / "video_only.mp4"
    r = subprocess.run([str(FF), "-y", "-hide_banner", "-loglevel", "error",
                        "-f", "concat", "-safe", "0", "-i", str(listf),
                        "-c", "copy", str(tmp)], capture_output=True, text=True)
    if r.returncode != 0:
        log(f"concat FAIL {src.name}"); return False
    # Segment timestamps drift (~59.3 fps aggregate); rewrite the
    # video timestamps onto the exact 60 fps grid (timebase 1/15360,
    # 256 units/frame) losslessly at mux time - same fix as ep3.
    r = subprocess.run([str(FF), "-y", "-hide_banner", "-loglevel", "error",
                        "-i", str(tmp), "-i", str(src), "-map", "0:v", "-map", "1:a?",
                        "-c:v", "copy", "-bsf:v", "setts=ts=N*256:duration=256",
                        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                        "-ac", "2", "-movflags", "+faststart", str(dst)],
                       capture_output=True, text=True)
    return r.returncode == 0

def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    clips = []
    for folder in ("_sm", "_ai"):
        for src in sorted((WORK / folder).glob("*.mp4")):
            clips.append((folder, src, probe(src)))
    clips.sort(key=lambda c: c[2]["dur"])  # one at a time, shortest first
    for folder, src, info in clips:
        if only and only != src.stem:
            continue
        dst = OUT / folder / f"{src.stem}_max1080p60.mp4"
        dst.parent.mkdir(parents=True, exist_ok=True)
        want = round(info["dur"] * 60)
        if done_ok(dst, want):
            log(f"{dst.name} exists, skip"); continue
        if free_gb() < 5:
            log("DISK LOW - abort"); return 1
        log(f"MAX {src.name} {info['w']}x{info['h']}@{info['fps']:.2f} "
            f"dur={info['dur']:.0f}s -> {dst.name}")
        t0 = time.time()
        ok = run_clip(src, dst, info, OUT / "work" / src.stem)
        good = ok and done_ok(dst, want)
        log(f"{'OK' if good else 'FAIL'} {dst.name} elapsed={time.time()-t0:.0f}s")
        if not good:
            return 1
    log("DONE")
    return 0

if __name__ == "__main__":
    sys.exit(main())
