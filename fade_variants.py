#!/usr/bin/env python3
"""Apply short periodic fade-in/out at every clip boundary (softens hard cuts)."""
import subprocess, sys
from pathlib import Path

SISSY_DIR = Path(r"C:\Users\hyper\Videos\sissymaker")

# (source, period_frames, fade_in_frames, fade_out_frames, out_name)
JOBS = [
    (
        SISSY_DIR / "Ajja_Liveset3h_Sissymaker_WetDream_14BEATS_60fps.mp4",
        360, 4, 6,  # 6.0s clips @60fps
        "Ajja_Liveset3h_Sissymaker_WetDream_14BEATS_60fps_FADE.mp4",
    ),
    (
        SISSY_DIR / "Ajja_Liveset3h_Sissymaker_WetDream_14bpm_60fps.mp4",
        257, 4, 6,  # 4.285s clips @60fps
        "Ajja_Liveset3h_Sissymaker_WetDream_14bpm_60fps_FADE.mp4",
    ),
    (
        SISSY_DIR / "Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps.mp4",
        26, 2, 4,  # 0.433s clips @60fps — shorter fade
        "Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps_FADE.mp4",
    ),
]

def fade_lut(period: int, fi: int, fo: int) -> str:
    # y' = if lt(mod(n,P),Fi): y*mod(n,P)/Fi
    #     elif gt(mod(n,P),P-Fo-1): y*(P-mod(n,P))/Fo
    #     else: y
    return (
        "lutyuv=y='"
        f"if(lt(mod(n\\,{period})\\,{fi})\\,"
        f"val*mod(n\\,{period})/{fi}\\,"
        f"if(gt(mod(n\\,{period})\\,{period - fo - 1})\\,"
        f"val*({period}-mod(n\\,{period}))/{fo}\\,val))'"
    )

def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    for src, period, fi, fo, name in JOBS:
        if which != "all":
            if which not in name and which not in src.name:
                continue
        out = SISSY_DIR / name
        if not src.exists():
            print("skip missing", src.name, flush=True)
            continue
        if out.exists() and out.stat().st_size > 1_000_000:
            print("skip exists", name, flush=True)
            continue
        lut = fade_lut(period, fi, fo)
        print("FADE", src.name, "->", name, flush=True)
        print(" lut", lut, flush=True)
        r = subprocess.run(
            [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-i", str(src),
                "-vf", lut,
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "24",
                "-c:a", "copy",
                str(out),
            ],
            capture_output=True, text=True,
        )
        print("rc", r.returncode, flush=True)
        if r.stderr:
            print(r.stderr[-400:], flush=True)
        if r.returncode == 0:
            print("SIZE_MB", out.stat().st_size / 1e6, flush=True)
            pr = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out)],
                capture_output=True, text=True,
            )
            print("DURATION", pr.stdout.strip(), flush=True)
    print("FADE_ALL_DONE", flush=True)

if __name__ == "__main__":
    main()
