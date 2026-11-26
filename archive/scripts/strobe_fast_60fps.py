#!/usr/bin/env python3
"""Fast strobe liveset: stream-copy clips from GOP26 intermediates."""
import subprocess, sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

SISSY_DIR = Path(r"C:\Users\hyper\Videos\sissymaker")
OUT = SISSY_DIR / "liveset60_strobe"
INTER = SISSY_DIR / "intermediates"
SISSY_INT = INTER / "sissy_gop26.mp4"
WET_INT = INTER / "wet_gop26.mp4"
AUDIO = Path(r"C:\Users\hyper\Music\Ajja 2026 (Modern Psytrance of Today) @DimensionFestivalNZ.mp3")
FINAL = SISSY_DIR / "Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps.mp4"

CLIP_FRAMES = 26
CLIP_DUR = CLIP_FRAMES / 60.0  # 0.433333s

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
    n_clips = int(audio_dur / CLIP_DUR) + 1
    print(f"sissy={sissy_dur:.1f} wet={wet_dur:.1f} audio={audio_dur:.1f} n_clips={n_clips}", flush=True)

    OUT.mkdir(exist_ok=True)

    def cut(i):
        out = OUT / f"clip_{i:06d}.mp4"
        if out.exists() and out.stat().st_size > 1500:
            return i, 0, ""
        if i % 2 == 0:
            src, total = SISSY_INT, sissy_dur
            start = ((i // 2) * CLIP_DUR) % total
        else:
            src, total = WET_INT, wet_dur
            start = ((i // 2) * CLIP_DUR) % total
        # align to keyframe grid
        start = round(start / CLIP_DUR) * CLIP_DUR
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-ss", f"{start:.6f}", "-i", str(src),
            "-t", f"{CLIP_DUR:.6f}", "-an",
            "-c:v", "copy", "-avoid_negative_ts", "make_zero",
            str(out),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0 or not out.exists() or out.stat().st_size <= 1500:
            # fallback re-encode
            cmd = [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-ss", f"{start:.6f}", "-i", str(src),
                "-t", f"{CLIP_DUR:.6f}", "-an",
                "-vf", "fps=60,format=yuv420p", "-frames:v", str(CLIP_FRAMES),
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "25",
                str(out),
            ]
            r = subprocess.run(cmd, capture_output=True, text=True)
        return i, r.returncode, (r.stderr or "")[-150:]

    print(f"cutting {n_clips} clips...", flush=True)
    done = fails = 0
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = [ex.submit(cut, i) for i in range(n_clips)]
        for fut in as_completed(futs):
            i, rc, err = fut.result()
            done += 1
            if rc != 0:
                fails += 1
                if fails <= 5:
                    print("FAIL", i, err, flush=True)
            if done % 500 == 0 or done == n_clips:
                print(f"  {done}/{n_clips} fails={fails}", flush=True)

    missing = [i for i in range(n_clips)
               if not (OUT / f"clip_{i:06d}.mp4").exists()
               or (OUT / f"clip_{i:06d}.mp4").stat().st_size <= 1500]
    print("missing", len(missing), flush=True)
    if missing:
        with ThreadPoolExecutor(max_workers=6) as ex:
            list(ex.map(cut, missing))
        missing = [i for i in missing
                   if not (OUT / f"clip_{i:06d}.mp4").exists()
                   or (OUT / f"clip_{i:06d}.mp4").stat().st_size <= 1500]
        if missing:
            print("still missing", len(missing), flush=True)
            sys.exit(1)

    listf = OUT / "list.txt"
    with listf.open("w", encoding="utf-8") as f:
        for i in range(n_clips):
            f.write("file 'clip_%06d.mp4'\n" % i)

    copy_mp4 = OUT / "video_copy.mp4"
    print("concat copy...", flush=True)
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(listf),
         "-c", "copy", str(copy_mp4)],
        capture_output=True, text=True,
    )
    print("concat rc", r.returncode, flush=True)
    if r.returncode != 0:
        print(r.stderr[-400:], flush=True)
        sys.exit(1)

    print("mux audio...", flush=True)
    if FINAL.exists():
        FINAL.unlink()
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(copy_mp4), "-i", str(AUDIO),
         "-map", "0:v:0", "-map", "1:a:0",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-t", "%.6f" % min(n_clips * CLIP_DUR, audio_dur),
         str(FINAL)],
        capture_output=True, text=True,
    )
    print("mux rc", r.returncode, flush=True)
    if r.returncode != 0:
        print(r.stderr[-400:], flush=True)
        sys.exit(1)
    print(f"DONE {FINAL.name} {FINAL.stat().st_size/1e6:.1f}MB", flush=True)

if __name__ == "__main__":
    main()
