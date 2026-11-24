#!/usr/bin/env python3
"""Maximal 1080p60 normalization for every source clip in _sm/ and _ai/.

Output: _up1080/<_sm|_ai>/<stem>_1080p60.mp4  (1920x1080, 60 fps,
h264_nvenc CQ22, AAC 192k/48k, audio from source).

Tiers (see UPSCALE_1080.md):
- PASS  source already >=1080p: lanczos scale/pad to 1920x1080, fps=60.
  No AI pass (AI on already-1080p+ only hallucinates; >1080p lanczos
  down to 1080 keeps real detail).
- AI    source below 1080p (wet 960x540, csd2/scs/sm2/sm3/sm4 720p):
  Real-ESRGAN ncnn (realesr-animevideov3-x2, -j 1:1:1 -t 256, the
  settings verified stable in the Antigravity A/B) per frame in 10 s
  source segments, then scale to 1920x1080 + fps=60 in the same encode.

Resumable everywhere: finished clips/segments (frame-verified) skip.
Order: PASS first, then AI shortest-first (wet last, it is ~37 h alone).
Aborts if G: free space drops below 5 GB.
"""
import json, shutil, subprocess, sys, time
from pathlib import Path

WORK = Path(__file__).resolve().parent
FFD = WORK / "tools" / "ffmpeg-7.1.1-essentials_build" / "bin"
FF, FP = FFD / "ffmpeg.exe", FFD / "ffprobe.exe"
ESR = Path(r"C:\Users\hyper\workspace\hyperporn\comfy-pipeline\tools\realesrgan\realesrgan-ncnn-vulkan.exe")
OUT = WORK / "_up1080"
SEG_S = 10

def log(m): print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)

def probe(p):
    r = subprocess.run([str(FP), "-v", "error", "-show_entries",
                        "stream=codec_type,width,height,avg_frame_rate,r_frame_rate,nb_frames",
                        "-show_entries", "format=duration", "-of", "json", str(p)],
                       capture_output=True, text=True)
    d = json.loads(r.stdout)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    fps = v["avg_frame_rate"]
    num, _, den = fps.partition("/")
    rate = float(num) / float(den or 1) if float(den or 1) else 0
    return {"dur": float(d["format"]["duration"]), "w": v["width"], "h": v["height"],
            "fps": rate, "frames": int(v.get("nb_frames") or 0)}

def done_ok(p, want_frames):
    if not p.exists():
        return False
    try:
        i = probe(p)
        return i["w"] == 1920 and i["h"] == 1080 and abs(i["frames"] - want_frames) <= 180
    except Exception:
        return False

def free_gb():
    return shutil.disk_usage(WORK).free / 1e9

def enc_args():
    return ["-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "22",
            "-b:v", "0", "-g", "60", "-pix_fmt", "yuv420p"]

def run_pass(src, dst, info):
    vf = ("scale=1920:1080:force_original_aspect_ratio=decrease:flags=lanczos,"
          "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=60,format=yuv420p")
    cmd = [str(FF), "-y", "-hide_banner", "-loglevel", "error", "-i", str(src),
           "-vf", vf, "-map", "0:v:0", "-map", "0:a?", *enc_args(),
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
           "-movflags", "+faststart", str(dst)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0

def run_ai(src, dst, info, clip_work):
    # 10 s source segments -> PNG frames -> ESRGAN x2 -> 1080p60 segment
    # A final sliver (<1 s) merges into the previous segment: extracting
    # it alone can yield zero frames (smb3 seg33, 2026-11-24).
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
        if done_ok(seg, round(seg_dur * 60)):
            continue
        fin, fout = clip_work / f"f{si}", clip_work / f"u{si}"
        for d in (fin, fout):
            if d.exists():
                shutil.rmtree(d)
            d.mkdir(parents=True)
        r = subprocess.run([str(FF), "-y", "-hide_banner", "-loglevel", "error",
                            "-ss", f"{start:.3f}", "-i", str(src), "-t", f"{seg_dur:.3f}",
                            "-an", str(fin / "f%05d.png")], capture_output=True, text=True)
        if r.returncode != 0:
            log(f"extract FAIL {src.name} seg{si}"); return False
        src_frames = len(list(fin.glob("*.png")))
        scale = "4" if info["h"] <= 480 else "2"  # 360p needs x4 to reach 1080
        r = subprocess.run([str(ESR), "-i", str(fin), "-o", str(fout),
                            "-n", f"realesr-animevideov3-x{scale}", "-s", scale,
                            "-t", "256", "-g", "0", "-j", "1:1:1", "-f", "png"],
                           capture_output=True, text=True)
        up_frames = len(list(fout.glob("*.png"))) if fout.exists() else 0
        if r.returncode != 0 or up_frames != src_frames:
            log(f"esrgan FAIL {src.name} seg{si} rc={r.returncode} {up_frames}/{src_frames}")
            return False
        vf = ("scale=1920:1080:force_original_aspect_ratio=decrease:flags=lanczos,"
              "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=60,format=yuv420p")
        r = subprocess.run([str(FF), "-y", "-hide_banner", "-loglevel", "error",
                            "-framerate", f"{info['fps']:.6f}", "-i", str(fout / "f%05d.png"),
                            "-vf", vf, "-an", *enc_args(), "-t", f"{seg_dur:.3f}", str(seg)],
                           capture_output=True, text=True)
        shutil.rmtree(fin, ignore_errors=True); shutil.rmtree(fout, ignore_errors=True)
        if r.returncode != 0 or not done_ok(seg, round(seg_dur * 60)):
            log(f"seg encode FAIL {src.name} seg{si} {(r.stderr or '')[-200:]}"); return False
        log(f"  {src.name} seg {si+1}/{len(bounds)} ok (free {free_gb():.1f} GB)")
        if free_gb() < 5:
            log("DISK LOW - abort"); return False
    listf = clip_work / "list.txt"
    with listf.open("w") as f:
        for s in segs:
            f.write(f"file '{s.resolve().as_posix()}'\n")
    tmp = clip_work / "video_only.mp4"
    r = subprocess.run([str(FF), "-y", "-hide_banner", "-loglevel", "error",
                        "-f", "concat", "-safe", "0", "-i", str(listf), "-c", "copy", str(tmp)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        log(f"concat FAIL {src.name}"); return False
    r = subprocess.run([str(FF), "-y", "-hide_banner", "-loglevel", "error",
                        "-i", str(tmp), "-i", str(src), "-map", "0:v", "-map", "1:a?",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                        "-ac", "2", "-movflags", "+faststart", str(dst)],
                       capture_output=True, text=True)
    return r.returncode == 0

def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None  # pass | ai | <stem>
    clips = []
    for folder in ("_sm", "_ai"):
        for src in sorted((WORK / folder).glob("*.mp4")):
            info = probe(src)
            tier = "pass" if (info["h"] >= 1080 or info["w"] >= 1920) else "ai"
            clips.append((folder, src, info, tier))
    clips.sort(key=lambda c: (0 if c[3] == "pass" else 1, c[2]["dur"]))
    for folder, src, info, tier in clips:
        if only and only not in (tier, src.stem):
            continue
        dst = OUT / folder / f"{src.stem}_1080p60.mp4"
        dst.parent.mkdir(parents=True, exist_ok=True)
        want = round(info["dur"] * 60)
        if done_ok(dst, want):
            log(f"{dst.name} exists, skip"); continue
        if free_gb() < 5:
            log("DISK LOW - abort"); return 1
        log(f"{tier.upper()} {src.name} {info['w']}x{info['h']}@{info['fps']:.2f} "
            f"dur={info['dur']:.0f}s -> {dst.name}")
        t0 = time.time()
        ok = run_pass(src, dst, info) if tier == "pass" else \
            run_ai(src, dst, info, OUT / "work" / src.stem)
        good = ok and done_ok(dst, want)
        log(f"{'OK' if good else 'FAIL'} {dst.name} elapsed={time.time()-t0:.0f}s")
        if not good:
            return 1
    log("DONE")
    return 0

if __name__ == "__main__":
    sys.exit(main())
