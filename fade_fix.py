#!/usr/bin/env python3
"""Fixed fade mask + loop-safe blend.

Bug: `-stream_loop -1` resets mask PTS; blend pairs by timestamp so half the
content frames get multiplied by black. Fix: `setpts=N/FRAME_RATE/TB` on the
looped mask before blend, so frame numbers stay continuous.

Bug 2: old mask frame 0 was pure black (fade=t=in:st=0) -> 1-frame black flash
per cut. New mask is a triangular dip to a non-zero floor (default 48/255).
"""
import subprocess, sys
from pathlib import Path

SISSY = Path(r"C:\Users\hyper\Videos\sissymaker")
W, H, FPS = 1280, 720, 60

def make_mask(period, dip_frames, floor, path):
    """Write `period` gray frames: triangular dip to `floor` centered on frame 0."""
    n = period
    k = dip_frames  # total frames in the dip (half before wrap, half after)
    half = k / 2.0
    frames = bytearray()
    for i in range(n):
        # distance from wrap point (frame 0), periodic
        d = min(i, n - i)  # 0 at wrap, n/2 at middle
        if d >= half:
            v = 255
        else:
            # triangular: floor at d=0, 255 at d=half
            v = int(floor + (255 - floor) * (d / half))
        frames.extend(bytes([v]) * (W * H))
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{W}x{H}", "-r", str(FPS),
        "-i", "-",
        "-frames:v", str(n),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
        "-pix_fmt", "yuv420p", str(path),
    ]
    r = subprocess.run(cmd, input=bytes(frames), capture_output=True, timeout=120)
    print(f"mask_p{period}_dip{k}_floor{floor}: rc={r.returncode} size={path.stat().st_size}")
    return r.returncode == 0

def fade_filter(period):
    """Loop-safe blend: setpts keeps frame numbers continuous across the loop."""
    return (
        "[1:v]setpts=N/FRAME_RATE/TB,format=gbrp[m];"
        "[0:v]format=gbrp[a];"
        "[a][m]blend=all_mode=multiply:shortest=1,format=yuv420p[v]"
    )

def test_sample():
    """3s sample from the clean intermediate + fixed mask -> verify luma."""
    src = SISSY / "intermediates" / "sissy_all_gop26.mp4"
    mask = SISSY / "mask_p26_fixed.mp4"
    out = SISSY / "fade_test_fixed.mp4"
    make_mask(26, 6, 48, mask)
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-ss", "100", "-t", "3", "-i", str(src),
        "-stream_loop", "-1", "-i", str(mask),
        "-filter_complex", fade_filter(26),
        "-map", "[v]",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
        "-frames:v", "180", str(out),
    ]
    r = subprocess.run(cmd, capture_output=True, timeout=180)
    print(f"test encode rc={r.returncode} {out.name} {out.stat().st_size if out.exists() else 0}")
    if r.returncode != 0:
        print(r.stderr.decode()[-500:])
        return False

    # luma dump
    W, H = 1280, 720
    FSZ = W * H
    r2 = subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(out),
         "-frames:v", "90", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
        capture_output=True, timeout=120,
    )
    data = r2.stdout
    n = len(data) // FSZ
    black = dim = bright = 0
    for i in range(n):
        g = sum(data[i * FSZ:(i + 1) * FSZ]) / FSZ
        if g < 8:
            black += 1
            print(f"  f{i:2d} {g:.1f} FULL BLACK")
        elif g < 200:
            dim += 1
            if i < 40 or (i % 26) < 8:
                print(f"  f{i:2d} {g:.1f} dim")
        else:
            bright += 1
    print(f"frames={n} black={black} dim={dim} bright={bright}")
    return black == 0

if __name__ == "__main__":
    if sys.argv[1:] and sys.argv[1] == "test":
        ok = test_sample()
        print("TEST_PASS" if ok else "TEST_FAIL")
    else:
        # just build masks
        make_mask(26, 6, 48, SISSY / "mask_p26_fixed.mp4")
        make_mask(257, 10, 48, SISSY / "mask_p257_fixed.mp4")
        make_mask(360, 10, 48, SISSY / "mask_p360_fixed.mp4")
        print("MASKS_OK")
