#!/usr/bin/env python3
"""v9 extension: apply the prior pipeline processes to ext01..ext15 and
append them after the v8 master.

Per new file (finished PMVs, used whole like wet_gop26 was):
  scale/pad to 1280x720, fps=60, GOP 26, 26-frame triangular strobe mask
  (mask_p26_fixed.mp4, RGB multiply, same filter as build_v8_full.py),
  own audio kept as AAC 192k/48k (same as hyperporn_v8_autodj.mp4).
Resumable: a segment whose frame count is within 120 frames of
duration*60 is skipped. Final: concat demuxer -c copy of
hyperporn_v8_autodj.mp4 + all segments -> hyperporn_v9_extended.mp4
(original 3h is never re-encoded).
"""
import json, subprocess, sys, time
from pathlib import Path

WORK = Path(__file__).resolve().parent
FF = WORK / "tools" / "ffmpeg-7.1.1-essentials_build" / "bin"
MASK = WORK / "mask_p26_fixed.mp4"
BASE = WORK / "hyperporn_v8_autodj.mp4"
OUTDIR = WORK / "liveset60_v9_ext"
OUT = WORK / "hyperporn_v9_extended.mp4"

def log(m): print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)

def probe(p):
    r = subprocess.run([str(FF / "ffprobe.exe"), "-v", "error", "-show_entries",
                        "stream=codec_type,width,height,avg_frame_rate,nb_frames",
                        "-show_entries", "format=duration", "-of", "json", str(p)],
                       capture_output=True, text=True)
    d = json.loads(r.stdout)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    return float(d["format"]["duration"]), int(v.get("nb_frames") or 0)

def main():
    OUTDIR.mkdir(exist_ok=True)
    entries = json.loads((WORK / "new_videos.json").read_text(encoding="utf-8"))
    segs = []
    for e in entries:
        src = WORK / "_ai" / e["new_name"]
        seg = OUTDIR / f"{src.stem}_seg.mp4"
        segs.append(seg)
        dur, _ = probe(src)
        want = round(dur * 60)
        if seg.exists():
            try:
                _, got = probe(seg)
                if abs(got - want) <= 120:
                    log(f"{seg.name} exists frames={got} want~{want}, skip"); continue
            except Exception:
                pass
        fc = ("[0:v]scale=1280:720:force_original_aspect_ratio=decrease,"
              "pad=1280:720:(ow-iw)/2:(oh-ih)/2,fps=60,format=gbrp[a];"
              "[1:v]setpts=N/FRAME_RATE/TB,format=gbrp[m];"
              "[a][m]blend=all_mode=multiply:shortest=1,format=yuv420p[v]")
        cmd = [str(FF / "ffmpeg.exe"), "-y", "-hide_banner", "-loglevel", "error",
               "-i", str(src), "-stream_loop", "-1", "-i", str(MASK),
               "-filter_complex", fc, "-map", "[v]", "-map", "0:a",
               "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
               "-g", "26", "-keyint_min", "26", "-sc_threshold", "0",
               "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
               "-t", f"{dur:.3f}", str(seg)]
        log(f"{seg.name}: encode start dur={dur:.1f}s")
        t0 = time.time()
        r = subprocess.run(cmd, capture_output=True, text=True)
        _, got = probe(seg) if seg.exists() else (0, -1)
        log(f"{seg.name}: rc={r.returncode} frames={got} want~{want} "
            f"elapsed={time.time()-t0:.0f}s {(r.stderr or '')[-200:]}")
        if r.returncode != 0 or abs(got - want) > 120:
            log("SEGMENT FAIL - abort"); return 1
    listf = OUTDIR / "v9_list.txt"
    # Concat demuxer resolves relative paths against the list file's dir.
    with listf.open("w") as f:
        f.write(f"file '{BASE.resolve().as_posix()}'\n")
        for s in segs:
            f.write(f"file '{s.resolve().as_posix()}'\n")
    r = subprocess.run([str(FF / "ffmpeg.exe"), "-y", "-hide_banner", "-loglevel", "error",
                        "-f", "concat", "-safe", "0", "-i", str(listf),
                        "-c", "copy", "-movflags", "+faststart", str(OUT)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        log(f"concat FAIL {(r.stderr or '')[-400:]}"); return 1
    dur, frames = probe(OUT)
    log(f"FINAL {OUT.name} dur={dur:.1f}s frames={frames}")
    log("DONE")
    return 0

if __name__ == "__main__":
    sys.exit(main())
