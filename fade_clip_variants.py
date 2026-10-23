#!/usr/bin/env python3
"""Rebuild fade livesets with per-clip black fade-in/out (no chroma blend)."""
import subprocess, sys, shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

SISSY_DIR = Path(r"C:\Users\hyper\Videos\sissymaker")
INTER = SISSY_DIR / "intermediates"
SISSY_INT = INTER / "sissy_gop26.mp4"
WET_INT = INTER / "wet_gop26.mp4"
AUDIO = Path(r"C:\Users\hyper\Music\Ajja 2026 (Modern Psytrance of Today) @DimensionFestivalNZ.mp3")
W, H, FPS = 1280, 720, 60

# tag, clip_sec, fade_in_sec, fade_out_sec, frames_per_clip, out_name
JOBS = {
    "14beats": (6.0, 0.07, 0.10, 360,
                "Ajja_Liveset3h_Sissymaker_WetDream_14BEATS_60fps_FADE.mp4"),
    "14bpm": (60.0 / 14.0, 0.07, 0.10, 257,
              "Ajja_Liveset3h_Sissymaker_WetDream_14bpm_60fps_FADE.mp4"),
    "strobe": (26.0 / 60.0, 0.035, 0.05, 26,
               "Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps_FADE.mp4"),
}

def probe(p):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
        capture_output=True, text=True, check=True,
    )
    return float(r.stdout.strip())

def build(tag):
    clip_dur, fi, fo, frames, out_name = JOBS[tag]
    out_dir = SISSY_DIR / f"fadeclips_{tag}"
    final = SISSY_DIR / out_name
    print(f"\n=== {tag} clip={clip_dur:.4f}s frames={frames} ===", flush=True)

    sissy_dur = probe(SISSY_INT)
    wet_dur = probe(WET_INT)
    audio_dur = probe(AUDIO)
    n_clips = int(audio_dur / clip_dur) + 1
    print(f"n_clips={n_clips}", flush=True)

    if out_dir.exists():
        shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    fo_start = max(clip_dur - fo, 0.0)

    def render(i):
        out = out_dir / f"clip_{i:06d}.mp4"
        if out.exists() and out.stat().st_size > 1500:
            return i, 0, ""
        if i % 2 == 0:
            src, total = SISSY_INT, sissy_dur
            start = ((i // 2) * clip_dur) % total
        else:
            src, total = WET_INT, wet_dur
            start = ((i // 2) * clip_dur) % total
        vf = f"fade=t=in:st=0:d={fi}:color=black,fade=t=out:st={fo_start:.6f}:d={fo}:color=black,fps={FPS},format=yuv420p"
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-ss", f"{start:.6f}", "-i", str(src), "-an",
            "-vf", vf,
            "-frames:v", str(frames),
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "25",
            "-g", str(frames),
            str(out),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        return i, r.returncode, (r.stderr or "")[-180:]

    workers = 4
    print(f"rendering {n_clips} clips...", flush=True)
    done = fails = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(render, i) for i in range(n_clips)]
        for fut in as_completed(futs):
            i, rc, err = fut.result()
            done += 1
            if rc != 0:
                fails += 1
                if fails <= 5:
                    print("FAIL", i, err, flush=True)
            if done % 200 == 0 or done == n_clips:
                print(f"  {done}/{n_clips} fails={fails}", flush=True)

    missing = [i for i in range(n_clips)
               if not (out_dir / f"clip_{i:06d}.mp4").exists()
               or (out_dir / f"clip_{i:06d}.mp4").stat().st_size <= 1500]
    if missing:
        print("retry missing", len(missing), flush=True)
        with ThreadPoolExecutor(max_workers=6) as ex:
            list(ex.map(render, missing))
        missing = [i for i in missing
                   if not (out_dir / f"clip_{i:06d}.mp4").exists()
                   or (out_dir / f"clip_{i:06d}.mp4").stat().st_size <= 1500]
        if missing:
            print("still missing", len(missing), flush=True)
            sys.exit(1)

    listf = out_dir / "list.txt"
    with listf.open("w", encoding="utf-8") as f:
        for i in range(n_clips):
            f.write("file 'clip_%06d.mp4'\n" % i)

    copy_mp4 = out_dir / "video_copy.mp4"
    print("concat...", flush=True)
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(listf),
         "-c", "copy", str(copy_mp4)],
        capture_output=True, text=True,
    )
    print("concat rc", r.returncode, flush=True)
    if r.returncode != 0:
        print(r.stderr[-300:], flush=True)
        sys.exit(1)

    print("mux audio...", flush=True)
    if final.exists():
        final.unlink()
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(copy_mp4), "-i", str(AUDIO),
         "-map", "0:v:0", "-map", "1:a:0",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-t", "%.6f" % min(n_clips * clip_dur, audio_dur),
         str(final)],
        capture_output=True, text=True,
    )
    print("mux rc", r.returncode, flush=True)
    if r.returncode != 0:
        print(r.stderr[-300:], flush=True)
        sys.exit(1)
    print(f"DONE {final.name} {final.stat().st_size/1e6:.1f}MB", flush=True)
    # free clip dir after success
    shutil.rmtree(out_dir, ignore_errors=True)
    print("cleaned", flush=True)

if __name__ == "__main__":
    tag = sys.argv[1] if len(sys.argv) > 1 else "14beats"
    if tag == "all":
        for t in ("14beats", "14bpm", "strobe"):
            build(t)
    else:
        build(tag)
