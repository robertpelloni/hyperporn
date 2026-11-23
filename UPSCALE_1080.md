# 1080p60 upscale — all clips (`upscale1080.py`)

Goal: every source clip in `_sm/` + `_ai/` at 1920x1080, 60 fps,
as upscaled as it can get on this machine (GTX 1060 3GB).

## Method (measured, not assumed)

| Tier | Sources | Treatment |
|---|---|---|
| PASS | already ≥1080p (most `_sm`, most `ext*`, magnific portrait) | lanczos scale/pad to 1920x1080, `fps=60`, `h264_nvenc` CQ22. No AI: AI on ≥1080p only hallucinates; >1080p lanczos-down keeps real detail. |
| AI | below 1080p: wet 960x540, `csd2/scs/sm2/sm3/sm4` 720p, all 2026-11-23 new SM (240p/360p/720p) | Real-ESRGAN ncnn (`realesr-animevideov3-x2`, 360p-and-below `x4`), `-j 1:1:1 -t 256` (verified stable in the 2026-11-14 Antigravity A/B), 10 s segments, then scale to 1920x1080 + `fps=60` in the same encode. |

Benchmarks on this GPU: animevideov3-x2 ≈ 1.1 s/frame at 720p,
0.82 s/frame at 540p; x4plus ≈ 9.1 s/frame at 540p (rejected).
AI tier total ≈ 212k old frames + ≈103k new-SM frames ≈ **50-70 h**
of background grind. `python upscale1080.py` is resumable
(frame-verified skips); run `pass` first (done first), then `ai`,
then a plain rerun picks up any SM added later.

Outputs: `_up1080/<_sm|_ai>/<stem>_1080p60.mp4` (audio AAC 192k/48k).
The v9 segments in `liveset60_v9_ext/` were deleted after the v9
final verified (18.9 GB freed; regenerable via `build_v9_extend.py`).

## Ultramix episodes (`build_episodes.py`)

SM×AI overlapping with all prior effects: intro/outro+logo trim
(old SM: PIPELINE table; new SM + `ext*`: `detect_trims_v2.py`
numeric luma, `trims_v2.json`), GOP26 intermediates at 1080p60,
frame-exact 26-frame alternating clips, 26-frame triangular strobe
mask at 1080 (RGB multiply), chunked resumable fade, AutoDJ bed.
SM pool (deduped, 25 files) trims to 8,567 s, so the paired
ultramix is 17,134 s ≈ 4.76 h → `ultramix_ep1_1080p60.mp4` +
`ultramix_ep2_1080p60.mp4` (AI side uses ext01..ext06-partial;
remaining AI stays in `hyperporn_v9_extended.mp4`).
Episode intermediates use lanczos; when the ESRGAN `_up1080`
library finishes, rebuild episodes from it for the AI-upscaled
version (same script, point intermediates at `_up1080` outputs).

## Dedupe (2026-11-23, `dedupe_newsm.py`)

Duration grouping is only a candidate filter (sas/bost2 share
317.1 s and are *different* content). Verified by 5 s-interval
aHash sequence alignment (same content ≈ 6-9/64 bits differing;
different content ≈ 28-30/64). Quarantined in `_sm/_dup/`:
`scs2` (= scs), `scds2v` (= scds), `Sissymaker` (= sm1). Kept SM
pool: 25 files. Report: `dedupe_report.json`.
