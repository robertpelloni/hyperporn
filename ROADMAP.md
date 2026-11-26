# ROADMAP (rewritten 2026-11-26 after the ChatGPT/Gemini roast cycle)

## Done
- v8 masters (autodj + hypno, 646,464f) and v9 extended cut (1,711,400f, 7.92h)
- Ultramix ep1/ep2/ep3 at 1080p60 (1,494,948f total, 6.92h), ep3 rebuilt with locked mask timestamps
- Source pools organized (_sm 32 deduped / _ai 21), trims + dedupe verified perceptually
- _up1080 x2 library 49/53; _max1080 maximal tier started (10/53 at rewrite time)
- Storage relieved via M: junctions; episodes all in G:
- Roast cleanup: 76 scripts archived, tests + QC report added, A/B decision gate recorded

## Definition of DONE (ChatGPT fix #10)
The project is DONE when: (1) _max1080 queue finishes or is explicitly frozen by the user,
(2) episodes are either accepted as-is or rebuilt from the max library by user choice,
(3) tests + QC pass, (4) docs and git are clean and pushed. No new enhancement tier
starts without a benchmark + A/B gate (AB_TEST.md).

## Next (ranked)
1. Finish or freeze the _max1080 queue (tail: drip1/ext05/ext06/wet; or one rented-GPU day - IDEAS.md)
2. Optional episode remasters from the max library; optional strobe-free variants (mask-depth flag)
3. Manifest-driven single pipeline + content-addressed stage cache (ChatGPT #2/#3)
4. Beat-grid measurement (real BPM per bed) replacing the fixed 26f assumption (#4)
5. Git lock resolution when the external holder releases (resync main index)
6. Compress-to-2GB distribution variants of the episodes

## Layout
Single repo, no submodules in G: (C: checkout carries ComfyUI/sd-scripts/topaz-ffmpeg
submodules, pinned on purpose). See STORAGE.md and DEPLOY.md for the working layout.
