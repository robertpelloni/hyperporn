#!/usr/bin/env python3
"""rebuild_v3: all sissymaker/emperorhypnos sources, intros trimmed, strobe with
fixed fade, hypnoshit layered under Ajja.

Changes vs v2:
  - source pool = 15 current videos (incl. PMVArchive / IntenseObsessions / SMX)
  - each source is intro-trimmed per intro_trims.json before normalization
  - intermediates rebuilt (720p60 GOP26, per-file setpts then concat copy)
  - fade uses triangular mask + setpts loop fix (no full-black flashes)
  - hypnoshit under Ajja (0.40 / 0.75)

Output: Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps_FADE_v2.mp4
"""
import subprocess, sys, time, json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

SISSY_DIR = Path(r"C:\Users\hyper\Videos\sissymaker")
INTER = SISSY_DIR / "intermediates"
INTER.mkdir(exist_ok=True)
WET_SRC = SISSY_DIR / "JPVT1109 - Wet Dreams AI Goon Therapy (parts 1-15).mp4"
AUDIO = Path(r"C:\Users\hyper\Music\Ajja - 2026 - Dimension Festival NZ (live).mp3")
HYPO_MIX = SISSY_DIR / "hypo_mix.m4a"
OUTDIR = SISSY_DIR / "liveset60_strobe"
CLIP_FRAMES = 26
CLIP_DUR = CLIP_FRAMES / 60.0
W, H, FPS = 1280, 720, 60

FINAL = SISSY_DIR / "Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps_FADE_v2.mp4"
SISSY_GOP = INTER / "sissy_all_gop26.mp4"
WET_GOP = INTER / "wet_gop26.mp4"
VIDEO_ONLY = OUTDIR / "video_copy.mp4"
MASK = SISSY_DIR / "mask_p26_fixed.mp4"

TRIM = json.loads((SISSY_DIR / "intro_trims.json").read_text())

def log(msg):
    print(f"{time.strftime('%H:%M:%S')} {msg}", flush=True)

def probe(p):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(p)],
        capture_output=True, text=True, check=True,
    )
    return float(r.stdout.strip())

def norm_part(src, ss, out):
    """Intro-trim + normalize to 720p60 CFR GOP26."""
    if out.exists() and out.stat().st_size > 100_000:
        return True
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-ss", f"{ss:.3f}", "-i", str(src),
        "-an",
        "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,fps=60,setpts=N/60/TB,format=yuv420p",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
        "-g", "26", "-keyint_min", "26", "-sc_threshold", "0",
        str(out),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        log(f"PART FAIL {out.name} {(r.stderr or '')[-200:]}")
    return r.returncode == 0

def build_sissy_intermediate():
    if SISSY_GOP.exists() and SISSY_GOP.stat().st_size > 500_000_000:
        log(f"sissy intermediate exists {SISSY_GOP.stat().st_size/1e6:.0f}MB")
        return True
    parts_dir = INTER / "sissy_parts"
    parts_dir.mkdir(exist_ok=True)
    names = list(TRIM.keys())
    log(f"normalizing {len(names)} sissymaker sources (intros trimmed)...")
    ok = True
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {}
        for i, n in enumerate(names):
            src = SISSY_DIR / n
            if not src.exists():
                log(f"MISSING SOURCE {n}")
                ok = False
                continue
            out = parts_dir / f"p_{i:02d}.mp4"
            futs[ex.submit(norm_part, src, TRIM[n], out)] = n
        for fut in as_completed(futs):
            n = futs[fut]
            if not fut.result():
                ok = False
            else:
                log(f"  part ok {n[:50]}")
    if not ok:
        return False

    # probe sum vs concat
    listf = parts_dir / "list.txt"
    parts = sorted(parts_dir.glob("p_*.mp4"))
    total = 0.0
    with listf.open("w", encoding="utf-8") as f:
        for p in parts:
            d = probe(p)
            total += d
            f.write(f"file '{p.name}'\n")
    log(f"parts sum dur={total:.1f}s")
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(listf),
         "-c", "copy", str(SISSY_GOP)],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        log(f"concat fail {(r.stderr or '')[-300:]}")
        return False
    got = probe(SISSY_GOP)
    log(f"sissy_all_gop26 dur={got:.1f}s (sum {total:.1f}s) size={SISSY_GOP.stat().st_size/1e6:.0f}MB")
    if abs(got - total) > 2.0:
        log(f"DURATION MISMATCH {got:.1f} vs {total:.1f}")
        return False
    return True

def build_wet_intermediate():
    if WET_GOP.exists() and WET_GOP.stat().st_size > 500_000_000:
        log(f"wet intermediate exists {WET_GOP.stat().st_size/1e6:.0f}MB")
        return True
    log("building wet intermediate...")
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(WET_SRC), "-an",
         "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,fps=60,setpts=N/60/TB,format=yuv420p",
         "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
         "-g", "26", "-keyint_min", "26", "-sc_threshold", "0",
         str(WET_GOP)],
        capture_output=True, text=True,
    )
    log(f"wet rc={r.returncode} dur={probe(WET_GOP):.1f}s")
    return r.returncode == 0

def make_mask():
    if MASK.exists() and MASK.stat().st_size > 1000:
        log(f"mask exists {MASK.name}")
        return True
    n, k, floor = 26, 6, 48
    half = k / 2.0
    frames = bytearray()
    for i in range(n):
        d = min(i, n - i)
        v = 255 if d >= half else int(floor + (255 - floor) * (d / half))
        frames.extend(bytes([v]) * (W * H))
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-frames:v", str(n),
         "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
         "-pix_fmt", "yuv420p", str(MASK)],
        input=bytes(frames), capture_output=True, timeout=120,
    )
    log(f"mask rc={r.returncode}")
    return r.returncode == 0

def cut_clips(n_clips, sissy_dur, wet_dur):
    OUTDIR.mkdir(exist_ok=True)
    def cut(i):
        out = OUTDIR / f"clip_{i:06d}.mp4"
        if out.exists() and out.stat().st_size > 1500:
            return i, 0, ""
        if i % 2 == 0:
            src, total = SISSY_GOP, sissy_dur
        else:
            src, total = WET_GOP, wet_dur
        start = round((((i // 2) * CLIP_DUR) % total) / CLIP_DUR) * CLIP_DUR
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
               if not (OUTDIR / f"clip_{i:06d}.mp4").exists()
               or (OUTDIR / f"clip_{i:06d}.mp4").stat().st_size <= 1500]
    log(f"missing {len(missing)}")
    if missing:
        with ThreadPoolExecutor(max_workers=6) as ex:
            list(ex.map(cut, missing))
        missing = [i for i in missing
                   if not (OUTDIR / f"clip_{i:06d}.mp4").exists()
                   or (OUTDIR / f"clip_{i:06d}.mp4").stat().st_size <= 1500]
        if missing:
            log(f"STILL MISSING {len(missing)}")
            return False
    return True

def concat_clips(n_clips):
    listf = OUTDIR / "list.txt"
    with listf.open("w", encoding="utf-8") as f:
        for i in range(n_clips):
            f.write("file 'clip_%06d.mp4'\n" % i)
    if VIDEO_ONLY.exists() and VIDEO_ONLY.stat().st_size > 1_000_000_000:
        log(f"concat exists {VIDEO_ONLY.stat().st_size/1e6:.0f}MB")
        return True
    log("concat copy...")
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(listf),
         "-c", "copy", str(VIDEO_ONLY)],
        capture_output=True, text=True,
    )
    log(f"concat rc={r.returncode} size={VIDEO_ONLY.stat().st_size/1e6:.0f}MB")
    return r.returncode == 0

def final_fade_mux(audio_dur, n_clips):
    if not make_mask():
        return False
    if not HYPO_MIX.exists():
        log(f"missing {HYPO_MIX}")
        return False
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
         "-i", str(HYPO_MIX),
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
        return False
    log(f"DONE {FINAL.name} {FINAL.stat().st_size/1e6:.1f}MB dur={probe(FINAL):.1f}s")
    return True

def main():
    log("=== rebuild v3: all sources, intros trimmed, fixed fade, hypnoshit ===")
    for p in (WET_SRC, AUDIO, HYPO_MIX):
        if not p.exists():
            sys.exit(f"missing {p}")
    audio_dur = probe(AUDIO)
    n_clips = int(audio_dur / CLIP_DUR) + 1
    log(f"audio={audio_dur:.1f}s n_clips={n_clips}")

    if not build_sissy_intermediate():
        sys.exit("sissy intermediate failed")
    if not build_wet_intermediate():
        sys.exit("wet intermediate failed")
    sissy_dur = probe(SISSY_GOP)
    wet_dur = probe(WET_GOP)
    log(f"sissy={sissy_dur:.1f} wet={wet_dur:.1f}")

    if not cut_clips(n_clips, sissy_dur, wet_dur):
        sys.exit("cut failed")
    if not concat_clips(n_clips):
        sys.exit("concat failed")
    if not final_fade_mux(audio_dur, n_clips):
        sys.exit("final failed")
    log("REBUILD_V3_OK")

if __name__ == "__main__":
    main()
