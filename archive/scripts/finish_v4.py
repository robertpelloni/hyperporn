import subprocess, sys, time
from pathlib import Path

SISSY = Path(r"C:\Users\hyper\Videos\sissymaker")
VIDEO_FADE = SISSY / "liveset60_strobe" / "video_fade.mp4"
HYPO_MIX = SISSY / "hypo_mix_v2.m4a"
ST_MIX = SISSY / "spacetribe_mix.m4a"
OUT_AJJA = SISSY / "Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps_FADE_v3.mp4"
OUT_ST = SISSY / "SpaceTribe_Sissymaker_WetDream_STROBE140_60fps_FADE_v3.mp4"
RUN_TIME = 10774.336


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def mux_audio(bgm, out):
    if out.exists() and out.stat().st_size > 1_000_000_000:
        log(f"mux exists {out.name} {out.stat().st_size/1e6:.1f}MB")
        return True
    if out.exists():
        out.unlink()
    fc = (
        "[1:a]volume=0.70[bgm];"
        "[2:a]volume=0.90[hyp];"
        "[bgm][hyp]amix=inputs=2:duration=first:dropout_transition=0,"
        "alimiter=limit=0.95[aout]"
    )
    log(f"mux {out.name} ...")
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(VIDEO_FADE),
         "-i", str(bgm),
         "-i", str(HYPO_MIX),
         "-filter_complex", fc,
         "-map", "0:v", "-map", "[aout]",
         "-c:v", "copy",
         "-c:a", "aac", "-b:a", "320k",
         "-t", f"{RUN_TIME:.6f}",
         str(out)],
        capture_output=True, text=True,
    )
    log(f"mux rc={r.returncode} size={out.stat().st_size/1e6:.1f}MB")
    if r.returncode != 0:
        log((r.stderr or "")[-400:])
    return r.returncode == 0


def compress(src, out):
    if out.exists() and out.stat().st_size > 100_000_000:
        log(f"compress exists {out.name} {out.stat().st_size/1e6:.1f}MB")
        return True
    if out.exists():
        out.unlink()
    log(f"compress {out.name} ...")
    r = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(src),
         "-c:v", "libx264", "-preset", "veryfast",
         "-b:v", "1350k", "-maxrate", "1400k", "-bufsize", "2800k",
         "-vf", "scale=1280:720",
         "-c:a", "aac", "-b:a", "128k",
         "-movflags", "+faststart",
         str(out)],
        capture_output=True, text=True,
    )
    log(f"compress rc={r.returncode} size={out.stat().st_size/1e6:.1f}MB")
    return r.returncode == 0


def main():
    for p in (VIDEO_FADE, HYPO_MIX, ST_MIX, OUT_AJJA):
        if not p.exists():
            sys.exit(f"missing {p}")
    if not mux_audio(ST_MIX, OUT_ST):
        sys.exit("st mux failed")
    if not compress(OUT_AJJA, SISSY / "Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps_FADE_v3_2GB.mp4"):
        sys.exit("ajja compress failed")
    if not compress(OUT_ST, SISSY / "SpaceTribe_Sissymaker_WetDream_STROBE140_60fps_FADE_v3_2GB.mp4"):
        sys.exit("st compress failed")
    log("FINISH_OK")


if __name__ == "__main__":
    main()
