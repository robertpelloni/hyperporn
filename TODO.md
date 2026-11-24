# TODO

- RUNNING: ESRGAN AI upscale tier - continue with: python upscale1080.py ai (resumable; PASS tier done). ~50-85 h total on GTX 1060; wet + ext05/ext06 dominate.
- When _up1080 library is complete, rebuild ultramix episodes from the ESRGAN versions (build_episodes.py intermediates point at _sm/_ai lanczos versions today).
- More SM may still arrive in _sm/: catalog/dedupe/trim/upscale per NEW_SM.md workflow, then a build_episode4.py from remaining AI (ext11 remainder, ext12..ext15, wet).
- G: disk is tight (finals ~19 GB each). ultramix_ep2 lives in the C: checkout for this reason; move it when G: has room.
- Roast coordination with gemini/muse.ai/chatgpt: parked by user 2026-11-23, coordinate later.
- Optional: extend the hypno variant the same way as v9 (segments in liveset60_v9_ext/ were deleted after v9 verified; regenerable).
- Prune stale *.log / *.err build logs once everything is locked.
