#!/usr/bin/env python3
"""v2 rebuild: STROBE cut from clean intermediates + fixed fade + hypnoshit audio mix.

Fixes the v1 black flashes:
  1. mask frame 0 is no longer pure black (triangular dip to floor=48)
  2. looped mask gets setpts=N/FRAME_RATE/TB so blend stops desyncing
     (v1 used -stream_loop alone -> mask PTS reset -> half the frames
      were multiplied by black)

Audio: Ajja BGM at 0.75 + sequenced hypnoshit under it at 0.40.
Output: Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps_FADE_v2.mp4
"""
import subprocess, sys, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

SISSY_DIR = Path(r"C:\Users\hyper\Videos\sissymaker")
INTER = SISSY_DIR / "intermediates"
SISSY_INT = INTER / "sissy_all_gop26.mp4"   # 5119s clean, includes Sissymaker 5-9
WET_INT = INTER / "wet_gop26.mp4"
AUDIO = Path(r"C:\Users\hyper\Music\Ajja 2026 (Modern Psytrance of Today) @DimensionFestivalNZ.mp3")
HYPO = Path(r"C:\Users\hyper\Videos\hypnoshit")
OUTDIR = SISSY_DIR / "liveset60_strobe"
CLIP_DIR = OUTDIR
CLIP_FRAMES = 26
CLIP_DUR = CLIP_FRAMES / 60.0
W, H, FPS = 1280, 720, 60

FINAL = SISSY_DIR / "Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps_FADE_v2.mp4"
VIDEO_ONLY = OUTDIR / "video_copy.mp4"
MASK = SISSY_DIR / "mask_p26_fixed.mp4"

# hypnoshit sequence: (filename pattern, seconds to use) filling ~10774s
HYPO_PLAN = [
    ("You Cant Stop Me", None),
    ("Milking Time", None),
    ("Ultimate-Cuckold-Experience", None),
    ("Drop for Teacher", None),
    ("BeatrixVale", None),
    ("Submissive Sissy Slut", "fill"),  # trimmed to fill remainder
]

def log(msg):
    print(f"{time.strftime('%H:%M:%S')} {msg}", flush=True)

def probe(p):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(p)],
        capture_output=True, text=True, check=True,
    )
    return float(r.stdout.strip())

def find_hypo(pat):
    for f in HYPO.iterdir():
        if pat.lower() in f.name.lower() and f.suffix.lower() in (".mp3", ".m4a", ".wav"):
            return f
    raise SystemExit(f"hypnoshit track not found: {pat}")

def make_mask():
    if MASK.exists() and MASK.stat().st_size > 1000:
        log(f"mask exists {MASK.name}")
        return
    n, k, floor = 26, 6, 48
    half = k / 2.0
    frames = bytearray()
    for i in range(n):
        d = min(i, n - i)
        v = 255 if d >= half else int(floor + (255 - floor) * (d / half))
        frames.extend(bytes([v]) * (W * H))
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-frames:v", str(n),
           "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
           "-pix_fmt", "yuv420p", str(MASK)]
    r = subprocess.run(cmd, input=bytes(frames), capture_output=True, timeout=120)
    log(f"mask rc={r.returncode} size={MASK.stat().st_size}")
    if r.returncode != 0:
        sys.exit(1)

def cut_clips(n_clips, sissy_dur, wet_dur):
    OUTDIR.mkdir(exist_ok=True)
    def cut(i):
        out = CLIP_DIR / f"clip_{i:06d}.mp4"
        if out.exists() and out.stat().st_size > 1500:
            return i, 0, ""
        if i % 2 == 0:
            src, total = SISSY_INT, sissy_dur
        else:
            src, total = WET_INT, wet_dur
        start = (((i // 2) * CLIP_DUR) % total)
        start = round(start / CLIP_DUR) * CLIP_DUR
        cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
               "-ss", f"{start:.6f}", "-i", str(src),
               "-t", f"{CLIP_DUR:.6f}", "-an",
               "-c:v", "copy", "-avoid_negative_ts", "make_zero", str(out)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0 or not out.exists() or out.stat().st_size <= 1500:
            cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                   "-ss", f"{start:.6f}", "-i", str(src),
                   "-t", f"{CLIP_DUR:.6f}", "-an",
                   "-vf", "fps=60,format=yuv420p", "-frames:v", str(CLIP_FRAMES),
                   "-c:v", "libx264", "-preset", "ultrafast", "-crf", "25", str(out)]
            r = subprocess.run(cmd, capture_output=True, text=True)
        return i, r.returncode, (r.stderr or "")[-150:]

    log(f"cutting {n_clips} clips...")
    done = fails = 0
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = [ex.submit(cut, i) for i in range(n_clips)]
        for fut in as_completed(futs):
            i, rc, err = fut.result()
            done += 1
            if rc != 0:
                fails += 1
                if fails <= 5:
                    log(f"FAIL {i} {err}")
            if done % 500 == 0 or done == n_clips:
                log(f"  {done}/{n_clips} fails={fails}")

    missing = [i for i in range(n_clips)
               if not (CLIP_DIR / f"clip_{i:06d}.mp4").exists()
               or (CLIP_DIR / f"clip_{i:06d}.mp4").stat().st_size <= 1500]
    log(f"missing {len(missing)}")
    if missing:
        with ThreadPoolExecutor(max_workers=6) as ex:
            list(ex.map(cut, missing))
        missing = [i for i in missing
                   if not (CLIP_DIR / f"clip_{i:06d}.mp4").exists()
                   or (CLIP_DIR / f"clip_{i:06d}.mp4").stat().st_size <= 1500]
        if missing:
            log(f"STILL MISSING {len(missing)}")
            sys.exit(1)

def concat_clips(n_clips):
    listf = CLIP_DIR / "list.txt"
    with listf.open("w", encoding="utf-8") as f:
        for i in range(n_clips):
            f.write("file 'clip_%06d.mp4'\n" % i)
    if VIDEO_ONLY.exists() and VIDEO_ONLY.stat().st_size > 1_000_000_000:
        log(f"concat exists {VIDEO_ONLY.name} {VIDEO_ONLY.stat().st_size/1e6:.0f}MB")
        return
    log("concat copy...")
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(listf),
         "-c", "copy", str(VIDEO_ONLY)],
        capture_output=True, text=True,
    )
    log(f"concat rc={r.returncode}")
    if r.returncode != 0:
        log(r.stderr[-400:])
        sys.exit(1)
    log(f"concat size={VIDEO_ONLY.stat().st_size/1e6:.0f}MB")

def build_hypo_track(target_dur):
    """Concat hypnoshit tracks to ~target_dur seconds, trim the last."""
    parts = []
    used = 0.0
    for pat, mode in HYPO_PLAN:
        f = find_hypo(pat)
        d = probe(f)
        if mode == "fill":
            take = target_dur - used
        else:
            take = min(d, target_dur - used)
        if take <= 0:
            break
        parts.append((f, take, d))
        used += take
        log(f"  hypo +{take:.1f}s {f.name[:60]} (src {d:.1f}s)")
        if used >= target_dur - 0.1:
            break
    out = SISSY_DIR / "hypo_mix.m4a"
    # build via concat demuxer of per-part trims (m4a/aac)
    tmpdir = SISSY_DIR / "hypo_parts"
    tmpdir.mkdir(exist_ok=True)
    listf = tmpdir / "list.txt"
    with listf.open("w", encoding="utf-8") as lf:
        for idx, (f, take, _) in enumerate(parts):
            seg = tmpdir / f"seg_{idx:02d}.m4a"
            if not seg.exists() or seg.stat().st_size < 1000:
                r = subprocess.run(
                    ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                     "-i", str(f), "-t", f"{take:.6f}",
                     "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-ac", "2",
                     str(seg)],
                    capture_output=True, text=True,
                )
                log(f"  seg {idx} rc={r.returncode} {seg.name}")
            lf.write(f"file '{seg.name}'\n")
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(listf),
         "-c", "copy", str(out)],
        capture_output=True, text=True,
    )
    log(f"hypo_mix rc={r.returncode} dur={probe(out):.1f}s" if out.exists() else f"hypo_mix FAIL {r.stderr[-300:]}")
    return out

def final_fade_mux(audio_dur, n_clips):
    """One pass: fixed fade (loop-safe) + Ajja + hypnoshit mix."""
    make_mask()
    hypo = build_hypo_track(audio_dur)
    if FINAL.exists():
        FINAL.unlink()
    fc = (
        "[1:v]setpts=N/FRAME_RATE/TB,format=gbrp[m];"
        "[0:v]format=gbrp[a];"
        "[a][m]blend=all_mode=multiply:shortest=1,format=yuv420p[v];"
        "[2:a]volume=0.75[ajja];"
        "[3:a]volume=0.40[hyp];"
        "[ajja][hyp]amix=inputs=2:duration=first:dropout_transition=0,"
        "alimiter=limit=0.95[aout]"
    )
    log("final fade+mix encode START (ultrafast CRF 23)...")
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(VIDEO_ONLY),
         "-stream_loop", "-1", "-i", str(MASK),
         "-i", str(AUDIO),
         "-i", str(hypo),
         "-filter_complex", fc,
         "-map", "[v]", "-map", "[aout]",
         "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
         "-c:a", "aac", "-b:a", "320k",
         "-t", f"{min(n_clips * CLIP_DUR, audio_dur):.6f}",
         str(FINAL)],
        capture_output=True, text=True,
    )
    log(f"final rc={r.returncode}")
    if r.returncode != 0:
        log(r.stderr[-800:])
        sys.exit(1)
    log(f"DONE {FINAL.name} {FINAL.stat().st_size/1e6:.1f}MB dur={probe(FINAL):.1f}s")

def main():
    log("=== rebuild v2: fixed fade + hypnoshit mix ===")
    for p in (SISSY_INT, WET_INT, AUDIO):
        if not p.exists():
            sys.exit(f"missing {p}")
    sissy_dur = probe(SISSY_INT)
    wet_dur = probe(WET_INT)
    audio_dur = probe(AUDIO)
    n_clips = int(audio_dur / CLIP_DUR) + 1
    log(f"sissy={sissy_dur:.1f} wet={wet_dur:.1f} audio={audio_dur:.1f} n_clips={n_clips}")

    cut_clips(n_clips, sissy_dur, wet_dur)
    concat_clips(n_clips)
    final_fade_mux(audio_dur, n_clips)
    log("REBUILD_V2_OK")

if __name__ == "__main__":
    main()
