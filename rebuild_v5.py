import subprocess, sys, time
from pathlib import Path

SISSY = Path(r"C:\Users\hyper\Videos\sissymaker")
PARTS = SISSY / "hypo_parts_v2"
VIDEO_FADE = SISSY / "liveset60_strobe" / "video_fade.mp4"
AJJA = Path(r"C:\Users\hyper\Music\Ajja - 2026 - Dimension Festival NZ (live).mp3")
HYPO_MIX = SISSY / "hypo_mix_v3.m4a"
OUT = SISSY / "Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps_FADE_v3.mp4"
OUT_2GB = SISSY / "Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps_FADE_v3_2GB.mp4"
RUN_TIME = 10774.336


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def probe(p):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(p)],
        capture_output=True, text=True, check=True,
    )
    return float(r.stdout.strip())


def build_hypo_continuous():
    if HYPO_MIX.exists() and HYPO_MIX.stat().st_size > 1_000_000:
        log(f"hypo v3 exists {HYPO_MIX.stat().st_size/1e6:.1f}MB")
        return True
    parts = sorted(PARTS.glob("[0-9][0-9].m4a"))
    if not parts:
        log("no hypo parts")
        return False
    n = len(parts)
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    for p in parts:
        cmd += ["-i", str(p)]
    labels = "".join(f"[{i}:a]" for i in range(n))
    fc = f"{labels}concat=n={n}:v=0:a=1,aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[aout]"
    cmd += ["-filter_complex", fc, "-map", "[aout]",
            "-c:a", "aac", "-b:a", "192k", str(HYPO_MIX)]
    log(f"concat-filter hypo mix from {n} parts...")
    r = subprocess.run(cmd, capture_output=True, text=True)
    log(f"hypo rc={r.returncode} dur={probe(HYPO_MIX):.1f}s size={HYPO_MIX.stat().st_size/1e6:.1f}MB")
    return r.returncode == 0


def mux():
    if OUT.exists():
        OUT.unlink()
    # normalize=0 -> plain sum, no dropout renormalization (fixes hypnoshit cutouts)
    fc = (
        "[1:a]volume=0.70[bgm];"
        "[2:a]volume=0.95[hyp];"
        "[bgm][hyp]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
        "alimiter=limit=0.95[aout]"
    )
    log("mux Ajja v3 (hyp=0.95, normalize=0)...")
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(VIDEO_FADE),
         "-i", str(AJJA),
         "-i", str(HYPO_MIX),
         "-filter_complex", fc,
         "-map", "0:v", "-map", "[aout]",
         "-c:v", "copy",
         "-c:a", "aac", "-b:a", "320k",
         "-t", f"{RUN_TIME:.6f}",
         str(OUT)],
        capture_output=True, text=True,
    )
    log(f"mux rc={r.returncode} size={OUT.stat().st_size/1e6:.1f}MB")
    if r.returncode != 0:
        log((r.stderr or "")[-500:])
        return False
    return True


def compress():
    if OUT_2GB.exists():
        OUT_2GB.unlink()
    log("compress 2GB (veryfast 1350k)...")
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(OUT),
         "-c:v", "libx264", "-preset", "veryfast",
         "-b:v", "1350k", "-maxrate", "1400k", "-bufsize", "2800k",
         "-vf", "scale=1280:720",
         "-c:a", "aac", "-b:a", "128k",
         "-movflags", "+faststart",
         str(OUT_2GB)],
        capture_output=True, text=True,
    )
    log(f"compress rc={r.returncode} size={OUT_2GB.stat().st_size/1e6:.1f}MB")
    return r.returncode == 0


def main():
    for p in (VIDEO_FADE, AJJA):
        if not p.exists():
            sys.exit(f"missing {p}")
    if not build_hypo_continuous():
        sys.exit("hypo mix failed")
    if not mux():
        sys.exit("mux failed")
    if not compress():
        sys.exit("compress failed")
    log("REBUILD_V5_OK")


if __name__ == "__main__":
    main()
