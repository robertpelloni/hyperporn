# Maximal tier: AI-to-4K -> down to 1080, true 60 fps (`upscale_max.py`)

Requested 2026-11-24, superseding the `upscale1080.py` AI tier
(x2 -> 1080, duplicated frames) for the clips that tier had not
finished (drip1, ext05, ext06, wet; its 110 finished drip1 segments
remain in `_up1080/work/drip1/` if ever wanted).

## Per clip (source materials in `_sm/` + `_ai/` only, one at a time)

1. Frames -> Real-ESRGAN ncnn toward 4K: `realesr-animevideov3-x4`
   below 1080p, `-x2` at 1080-1440p, skipped at >=2160p (already 4K).
   Settings `-j 1:1:1 -t 256` (verified stable since the A/B).
2. Lanczos **down** to 1920x1080 - the 4K pass is supersampling:
   AI detail survives the downscale, upscale artifacts average out.
3. **True 60 fps motion**: `minterpolate=fps=60:mi_mode=mci:
   mc_mode=aobmc:me_mode=bidir:vsbmc=1` - synthesized in-between
   frames for 24/25/30 fps sources, not duplication.
4. `h264_nvenc` CQ18, 10 s segments, concat, source audio AAC 192k.

Output: `_max1080/<folder>/<stem>_max1080p60.mp4`.

## Measured costs on this GTX 1060 (why this is a grind)

| Stage | Rate |
|---|---|
| animevideov3-x4 at 720p | ~2.2 s/source frame |
| realesrgan-x4plus at 720p | ~20 s/source frame (rejected: 9x slower) |
| minterpolate mci/aobmc at 1080p | ~1 output fps (58x slow for 10 s test) |

Library: ~36,000 s / ~1.1M source frames -> ESRGAN weeks +
interpolation weeks. Shortest-first ordering means most clips
finish in the first days; wet/ext05/ext06 (7,340 s combined,
~440k source frames after drip1) dominate the tail. Resumable
per segment; rerun `python upscale_max.py` (or with a stem to
run one clip). Aborts below 5 GB free on G:.

## Ep3 "extra black strobe" - measured verdict (2026-11-24)

Same mask, same builder as ep1/ep2. Numeric checks (160x90 luma,
frame-exact samples): ep3 near-black frames 4.5% vs ep1 10.2%
(ep2 2.9%) across five windows; openings are 1.9-3.8% in both;
the 26-frame mask fold in ep3 is *shallower* (dip ratio 0.76)
than ep1 (0.20, = mask floor 48/255). Sampled ep3 sources
(ext09, drip1, ley5, sgas) contain 0% near-black frames.
Conclusion: no extra black strobe was added in ep3 - the
perceived effect is most plausibly (a) luminance/resolution
contrast between the dark low-res SM PMVs and the bright 4K AI
sources alternating every 0.43 s, and/or (b) a specific section
not sampled. Give a timestamp in ep3 and that exact window will
be measured the same way.
