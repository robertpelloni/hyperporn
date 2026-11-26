"""Regression tests for the hyperporn pipeline state.

Run: python -m pytest tests/ -x -q
Probes only (no encodes). These lock the verified facts that the
builders rely on, so a future session detects drift early:
sources present, trims sane, finals frame-exact, upscale
libraries at spec, dedupe pool intact.
"""
import json, subprocess
from pathlib import Path

WORK = Path(__file__).resolve().parent.parent
FP = WORK / "tools" / "ffmpeg-7.1.1-essentials_build" / "bin" / "ffprobe.exe"

def probe(p):
    r = subprocess.run([str(FP), "-v", "error", "-show_entries",
                        "stream=codec_type,width,height,avg_frame_rate,nb_frames",
                        "-show_entries", "format=duration", "-of", "json", str(p)],
                       capture_output=True, text=True)
    d = json.loads(r.stdout)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    return v, float(d["format"]["duration"])

def test_sources_exist():
    kept = json.loads((WORK / "dedupe_report.json").read_text())["kept_pool"]
    assert kept, "empty SM pool"
    for stem in kept:
        assert (WORK / "_sm" / f"{stem}.mp4").exists(), f"missing _sm/{stem}"
    for i in range(1, 16):
        assert (WORK / "_ai" / f"ext{i:02d}.mp4").exists(), f"missing ext{i:02d}"

def test_trims_within_durations():
    trims = json.loads((WORK / "trims_v2.json").read_text())
    assert len(trims) >= 25
    for name, t in trims.items():
        assert 0 <= t["head_trim_s"] <= 45, name
        assert 0 <= t["tail_trim_s"] <= 90, name
        assert t["head_trim_s"] + t["tail_trim_s"] < t["dur"], name

def test_ultramix_episodes_frame_exact():
    expect = {"ultramix_ep1_1080p60.mp4": 512408,
              "ultramix_ep2_1080p60.mp4": 512408,
              "ultramix_ep3_1080p60.mp4": 470132}
    for name, frames in expect.items():
        v, dur = probe(WORK / name)
        assert (v["width"], v["height"]) == (1920, 1080), name
        assert int(v["nb_frames"]) == frames, name
        assert abs(dur - frames / 60) < 1.0, name

def test_upscale_library_specs():
    outs = list((WORK / "_up1080").rglob("*_1080p60.mp4"))
    assert len(outs) >= 49
    for p in outs[:8]:  # sample: full sweep is slow
        v, _ = probe(p)
        assert (v["width"], v["height"]) == (1920, 1080), p.name

def test_max_library_specs():
    outs = list((WORK / "_max1080").rglob("*_max1080p60.mp4"))
    assert len(outs) >= 10
    for p in outs:
        v, _ = probe(p)
        assert (v["width"], v["height"]) == (1920, 1080), p.name
        num, _, den = v["avg_frame_rate"].partition("/")
        assert abs(float(num) / float(den) - 60) < 0.6, p.name
