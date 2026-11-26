#!/usr/bin/env python3
import subprocess, sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

SISSY_DIR = Path(r"C:\Users\hyper\Videos\sissymaker")
INTER = SISSY_DIR / "intermediates"
SISSY_INT = INTER / "sissy_gop26.mp4"
WET_INT = INTER / "wet_gop26.mp4"
AUDIO = Path(r"C:\Users\hyper\Music\Ajja 2026 (Modern Psytrance of Today) @DimensionFestivalNZ.mp3")
clip_dur, fi, fo, frames = 26 / 60.0, 0.035, 0.05, 26
out_dir = SISSY_DIR / "fadeclips_strobe"
final = SISSY_DIR / "Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps_FADE.mp4"

def probe(p):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
        capture_output=True, text=True, check=True,
    )
    return float(r.stdout.strip())

def main():
    sissy_dur = probe(SISSY_INT)
    wet_dur = probe(WET_INT)
    audio_dur = probe(AUDIO)
    n_clips = int(audio_dur / clip_dur) + 1
    fo_start = clip_dur - fo

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
        vf = (
            f"fade=t=in:st=0:d={fi}:color=black,"
            f"fade=t=out:st={fo_start:.6f}:d={fo}:color=black,format=yuv420p"
        )
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-ss", f"{start:.6f}", "-i", str(src), "-an", "-vf", vf,
            "-frames:v", str(frames),
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
            "-g", str(frames), str(out),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        return i, r.returncode, (r.stderr or "")[-120:]

    missing = [i for i in range(n_clips)
               if not (out_dir / f"clip_{i:06d}.mp4").exists()
               or (out_dir / f"clip_{i:06d}.mp4").stat().st_size <= 1500]
    print("n", n_clips, "missing", len(missing), flush=True)

    if missing:
        done = fails = 0
        with ThreadPoolExecutor(max_workers=12) as ex:
            futs = [ex.submit(render, i) for i in missing]
            for fut in as_completed(futs):
                i, rc, err = fut.result()
                done += 1
                if rc != 0:
                    fails += 1
                    if fails <= 5:
                        print("FAIL", i, err, flush=True)
                if done % 200 == 0 or done == len(missing):
                    print(f"  {done}/{len(missing)} fails={fails}", flush=True)

    missing = [i for i in range(n_clips)
               if not (out_dir / f"clip_{i:06d}.mp4").exists()
               or (out_dir / f"clip_{i:06d}.mp4").stat().st_size <= 1500]
    print("still missing", len(missing), flush=True)
    if missing:
        sys.exit(1)

    listf = out_dir / "list.txt"
    with listf.open("w") as f:
        for i in range(n_clips):
            f.write("file clip_%06d.mp4\n" % i)
    copy_mp4 = out_dir / "video_copy.mp4"
    print("concat", flush=True)
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(listf), "-c", "copy", str(copy_mp4)],
        capture_output=True, text=True,
    )
    print("concat rc", r.returncode, flush=True)
    if r.returncode != 0:
        print(r.stderr[-300:], flush=True)
        sys.exit(1)
    print("mux", flush=True)
    if final.exists():
        final.unlink()
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(copy_mp4), "-i", str(AUDIO),
         "-map", "0:v:0", "-map", "1:a:0",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-t", str(min(n_clips * clip_dur, audio_dur)), str(final)],
        capture_output=True, text=True,
    )
    print("mux rc", r.returncode, flush=True)
    if r.returncode == 0:
        pr = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(final)],
            capture_output=True, text=True,
        )
        print("DONE", final.stat().st_size / 1e6, "MB", pr.stdout.strip(), flush=True)
    else:
        print(r.stderr[-300:], flush=True)

if __name__ == "__main__":
    main()
