# IDEAS (aggressive, unfiltered - none committed)

- **Rent one GPU day**: the entire max-tier tail (drip1 +
  ext05/06 + wet, ~440k frames) is a weekend on a rented
  4090-class card with the same scripts; the local queue is
  the free-but-slow path. Cost/benefit is now measured
  (AB_TEST.md) - this is the single highest-leverage spend.
- **Episode generation from the max library**: once
  `_max1080` completes, rebuild ep1-3 from those clips
  (interpolated motion + supersampled detail) as "remasters".
- **Strobe-free / reduced-flash exports**: same intermediates,
  mask depth configurable; a `-mask-depth` flag (1.0 current,
  0.4 gentle, 0 off) costs one fade encode per variant.
- **Beat-grid honesty**: replace the fixed 26-frame assumption
  with per-track BPM analysis (librosa onset/beat track on
  the beds) and quantize clip boundaries to the measured
  grid - kills any slow drift against the kick.
- **Manifest-driven single pipeline** (ChatGPT fix #2):
  `pipeline.json` describing ingest->trim->edit->fx->upscale
  ->export stages, one driver, content-addressed stage cache
  keyed by input hash + config hash (fix #3).
- **Scene-aware mask vocabulary** (PROJECT_BRIEF 1): mask
  treatments that change per musical section instead of one
  dip for 8 hours.
- **HLS packaging** of the finished episodes (already
  keyframe-aligned) for smooth local streaming via Jellyfin.
- **Provenance ledger**: per-source hashes + rights notes in
  the catalog (the repo already hashes everything - formalize
  it), so any future distribution conversation starts from
  facts.
- **Watch-folder ingest**: new files in `_sm` auto-catalog,
  dedupe, trim-detect, and queue (tonight's manual loop,
  automated) - with a hard rule: never move sources while a
  queue is running (learned the hard way, 2026-11-24).
