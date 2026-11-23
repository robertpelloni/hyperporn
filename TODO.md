# TODO

- Done 2026-11-23: v8 liveset completed (hyperporn_v8_autodj.mp4, 646,464 frames verified); v9 extension built (hyperporn_v9_extended.mp4, 1,711,400 frames verified).
- Optional: extend the hypno variant the same way (segments in liveset60_v9_ext/ are reusable; audio is 192k vs hypno 320k).
- Optional: alternating sissy/new re-cut is NOT 1:1 feasible (sissy pool 5,649.8 s vs new 17,749.1 s; would repeat ~3.1x) - decide if a partial paired section is wanted.
- Upscaling: no full-master 4K run on this GPU (Topaz ~42 d watermarked; Real-ESRGAN ~110 d clean). Realistic: 1080p ESRGAN on selected chunks, or a stronger GPU. See CATCHUP_2026-11-23.md.
- Prune stale *.log / *.err build logs once v9 is locked.
- Decide retention for backup/wip-leader-sync-20261107 (redundant Syncthing marker only - safe to delete after confirmation).
