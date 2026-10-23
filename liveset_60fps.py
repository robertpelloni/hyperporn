#!/usr/bin/env python3
"""Liveset mashup at 60fps: sissymaker 1-9 x wet dream, AJJA liveset audio."""
import subprocess, sys, shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

SISSY_DIR = Path(r"C:\Users\hyper\Videos\sissymaker")
MUSIC = Path(r"C:\Users\hyper\Music")
AUDIO = MUSIC / "Ajja 2026 (Modern Psytrance of Today) @DimensionFestivalNZ.mp3"
WET = SISSY_DIR / "JPVT1109 - Wet Dreams AI Goon Therapy (parts 1-15).mp4"
SISSY = [
    SISSY_DIR / "Sissy Maker 1 by Emperor Hypnos (1).mp4",
    SISSY_DIR / "Emperor Hypnos Sissymaker II (1).mp4",
    SISSY_DIR / "EmperorHypnos - Sissy Maker III [720p].mp4",
    SISSY_DIR / "Sissy Maker IV by Emperor Hypnos (1).mp4",
    SISSY_DIR / "Sissymaker 5 - EmperorHypnos.mp4",
    SISSY_DIR / "Sissy Maker 6 by Emperor Hypnos (1).mp4",
    SISSY_DIR / "Sissymaker 7 BBC edition.mp4",
    SISSY_DIR / "Sissymaker 8 - Rapture PMV (1).mp4",
    SISSY_DIR / "SissyMaker 9 - Breed Black PMV (1).mp4",
]
W, H, FPS = 1280, 720, 60
PSY_BPM = 140.0

def probe(p):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
        capture_output=True, text=True, check=True,
    )
    return float(r.stdout.strip())

def sissy_at(sissy_dur, sissy_total, t):
    t = t % sissy_total
    acc = 0.0
    for p, d in sissy_dur:
        if t < acc + d:
            return p, t - acc
        acc += d
    p, d = sissy_dur[-1]
    return p, 0.0

def build(clip_dur: float, frames: int, tag: str, out_name: str, workers: int = 8, keep_clips: bool = False):
    out_dir = SISSY_DIR / f"liveset60_{tag}"
    final = SISSY_DIR / out_name
    print(f"\n=== {tag}: clip={clip_dur:.6f}s frames={frames} ===", flush=True)

    sissy_dur = [(p, probe(p)) for p in SISSY]
    wet_dur = probe(WET)
    audio_dur = probe(AUDIO)
    sissy_total = sum(d for _, d in sissy_dur)
    n_clips = int(audio_dur / clip_dur) + 1
    print(f"audio={audio_dur:.1f}s n_clips={n_clips} video={n_clips*clip_dur:.1f}s", flush=True)

    if out_dir.exists():
        shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    def render(i):
        if i % 2 == 0:
            src, start = sissy_at(sissy_dur, sissy_total, (i // 2) * clip_dur)
        else:
            start = ((i // 2) * clip_dur) % wet_dur
            src = WET
        out = out_dir / f"clip_{i:06d}.mp4"
        if out.exists() and out.stat().st_size > 2000:
            return i, 0, ""
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-ss", f"{start:.6f}", "-i", str(src), "-an",
            "-vf", (
                f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
                f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS},format=yuv420p,"
                f"tpad=stop_mode=clone:stop_duration=1"
            ),
            "-frames:v", str(frames),
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "25",
            "-g", str(frames), str(out),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        return i, r.returncode, (r.stderr or "")[-200:]

    print(f"rendering {n_clips} clips, {workers} workers...", flush=True)
    done = fails = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(render, i) for i in range(n_clips)]
        for fut in as_completed(futs):
            i, rc, err = fut.result()
            done += 1
            if rc != 0:
                fails += 1
                if fails <= 8:
                    print(f"FAIL {i}: {err}", flush=True)
            if done % 100 == 0 or done == n_clips:
                print(f"  {done}/{n_clips} fails={fails}", flush=True)

    missing = [i for i in range(n_clips)
               if not (out_dir / f"clip_{i:06d}.mp4").exists()
               or (out_dir / f"clip_{i:06d}.mp4").stat().st_size <= 2000]
    if missing:
        print(f"missing {len(missing)}: {missing[:15]}", flush=True)
        # retry missing once
        with ThreadPoolExecutor(max_workers=4) as ex:
            list(ex.map(render, missing))
        missing = [i for i in missing
                   if not (out_dir / f"clip_{i:06d}.mp4").exists()
                   or (out_dir / f"clip_{i:06d}.mp4").stat().st_size <= 2000]
        if missing:
            print(f"still missing {len(missing)}", flush=True)
            sys.exit(1)

    listf = out_dir / "list.txt"
    with listf.open("w", encoding="utf-8") as f:
        for i in range(n_clips):
            f.write("file 'clip_%06d.mp4'\n" % i)
    concat_mp4 = out_dir / "video_copy.mp4"
    print("concat copy...", flush=True)
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(listf),
         "-c", "copy", str(concat_mp4)],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(r.stderr[-400:], flush=True)
        sys.exit(1)

    print("mux audio...", flush=True)
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(concat_mp4), "-i", str(AUDIO),
         "-map", "0:v:0", "-map", "1:a:0",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-t", "%.6f" % min(n_clips * clip_dur, audio_dur),
         str(final)],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(r.stderr[-400:], flush=True)
        sys.exit(1)
    print(f"DONE {final.name} {final.stat().st_size/1e6:.1f}MB", flush=True)

    if not keep_clips:
        shutil.rmtree(out_dir, ignore_errors=True)
        print("cleaned clips", flush=True)

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "14beats"
    # frames at 60fps
    if which == "14beats":
        build(clip_dur=14.0 * (60.0 / PSY_BPM), frames=360, tag="14beats",
              out_name="Ajja_Liveset3h_Sissymaker_WetDream_14BEATS_60fps.mp4")
    elif which == "14bpm":
        build(clip_dur=60.0 / 14.0, frames=257, tag="14bpm",
              out_name="Ajja_Liveset3h_Sissymaker_WetDream_14bpm_60fps.mp4")
    elif which == "strobe":
        build(clip_dur=60.0 / PSY_BPM, frames=26, tag="strobe",
              out_name="Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps.mp4",
              workers=10)
    else:
        print("usage: 14beats|14bpm|strobe")
        sys.exit(1)
