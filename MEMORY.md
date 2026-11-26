# MEMORY - architecture & traits (maintained, not a session log)

- Canonical builders only in root (15 `.py`): v8/v9/episode
  builders, three upscale tiers, catalog/trim/dedupe tools.
  Everything iterated lives in `archive/scripts/` (see its
  README). Do not resurrect archived files; copy snippets.
- Two content pools: `_sm/` (32 deduped studio files) and
  `_ai/` (wet original + ext01-15 + magnific). `_sm/_dup/`
  quarantines perceptually-verified duplicates.
- Outputs: `_up1080/` (x2 tier, 49/53) and `_max1080/`
  (maximal tier, in progress) are junctions to
  `M:\hyperporn_media\`; episode scratch `C:\hyperporn_ultra_work`
  junctions to `M:\hyperporn_ultra_work`. Scripts use the
  G:/C: paths unchanged (see STORAGE.md).
- Finals: ultramix ep1-3 + v8 masters + v9 extended. Episodes
  are built from lanczos intermediates (UPSCALE_1080.md) - the
  ESRGAN libraries are per-clip deliverables, not (yet)
  episode inputs.
- Verification culture: ffprobe frame counts, fold ratios,
  aHash sequence matching, VMAF. `tests/test_pipeline.py`
  locks these facts; run it after any move/rebuild.
- Git: media is ignored; commits go through a temporary
  index while an external process holds `.git/index.lock`
  (do not kill it; `git reset --mixed HEAD` resyncs later).
- GPU is a GTX 1060 3GB: every AI stage must be benchmarked
  per-frame before a queue is promised. Heavy jobs run
  BelowNormal priority.
- Coordination lanes: Muse Code (this, G:), muse.ai sidechat
  (Bobbi), ChatGPT and Gemini tabs via Edge CDP :9222. Each
  identifies as "[model in harness in cwd on laptop]" and
  leaves markers (HPN-*) in-thread.
