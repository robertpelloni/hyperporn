import subprocess
import sys
import time
from pathlib import Path

SISSY = Path(r"C:\Users\hyper\Videos\sissymaker")
VIDEO = SISSY / "liveset60_strobe" / "video_fade.mp4"
HYPO = SISSY / "hypo_mix_v3.m4a"
MUSIC_BED = SISSY / "alt_audio" / "music_bed.m4a"
AJJA = Path(r"C:\Users\hyper\Music\Ajja - 2026 - Dimension Festival NZ (live).mp3")

OUT_NORM_FULL = SISSY / "ハイパーポルノ_full.mp4"
OUT_ALT_FULL = SISSY / "ハイパーポルノ_altaudio_full.mp4"
OUT_NORM_2GB = SISSY / "ハイパーポルノ_2GB.mp4"
OUT_ALT_2GB = SISSY / "ハイパーポルノ_altaudio_2GB.mp4"

RUN_TIME = 10774.336
MUS_VOL = "0.70"
HYP_VOL = "1.15"


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def probe(p):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(p)],
        capture_output=True, check=True,
    )
    return float(r.stdout.decode("utf-8", errors="replace").strip())


def mux_full(music_src, out):
    if out.exists() and out.stat().st_size > 9_000_000_000:
        log(f"full exists {out.name} {out.stat().st_size/1e9:.2f}GB")
        return True
    if out.exists():
        out.unlink()
    log(f"mux full {out.name} (mus={MUS_VOL} hyp={HYP_VOL})...")
    fc = (
        f"[1:a]volume={MUS_VOL}[mus];"
        f"[2:a]volume={HYP_VOL}[hyp];"
        "[mus][hyp]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
        "alimiter=limit=0.95[aout]"
    )
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(VIDEO),
         "-i", str(music_src),
         "-i", str(HYPO),
         "-filter_complex", fc,
         "-map", "0:v", "-map", "[aout]",
         "-c:v", "copy",
         "-c:a", "aac", "-b:a", "320k",
         "-t", f"{RUN_TIME:.6f}",
         str(out)],
        capture_output=True, text=True,
    )
    size = out.stat().st_size / 1e6 if out.exists() else 0
    log(f"  rc={r.returncode} size={size:.1f}MB")
    if r.returncode != 0:
        log((r.stderr or "")[-500:])
        return False
    return True


def compress(src, out):
    if out.exists():
        out.unlink()
    log(f"compress {out.name} (veryfast 1200k + aac 192k)...")
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(src),
         "-c:v", "libx264", "-preset", "veryfast",
         "-b:v", "1200k", "-maxrate", "1300k", "-bufsize", "2400k",
         "-vf", "scale=1280:720",
         "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart",
         str(out)],
        capture_output=True, text=True,
    )
    size = out.stat().st_size / 1e6 if out.exists() else 0
    log(f"  rc={r.returncode} size={size:.1f}MB")
    if r.returncode != 0:
        log((r.stderr or "")[-500:])
        return False
    if size >= 2000:
        log(f"  WARNING {size:.1f}MB not under 2000MB")
        return False
    return True


def main():
    for p in (VIDEO, HYPO, MUSIC_BED, AJJA):
        if not p.exists():
            sys.exit(f"missing {p}")

    if not mux_full(AJJA, OUT_NORM_FULL):
        sys.exit("norm full mux failed")
    if not mux_full(MUSIC_BED, OUT_ALT_FULL):
        sys.exit("alt full mux failed")

    if not compress(OUT_NORM_FULL, OUT_NORM_2GB):
        sys.exit("norm 2GB failed")
    if not compress(OUT_ALT_FULL, OUT_ALT_2GB):
        sys.exit("alt 2GB failed")

    for p in (OUT_NORM_FULL, OUT_ALT_FULL, OUT_NORM_2GB, OUT_ALT_2GB):
        log(f"OUT {p.name} {probe(p):.2f}s {p.stat().st_size/1e6:.1f}MB")
    log("REBUILD_FINAL_OK")


if __name__ == "__main__":
    main()
