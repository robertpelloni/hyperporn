# STORAGE map (2026-11-26)

| Path (as scripts see it) | Physical location | Contents |
|---|---|---|
| `G:\hyperporn\_sm`, `_ai` | G: | Source pools (32 + 21 files) |
| `G:\hyperporn\ultramix_ep*.mp4` | G: | Episode finals (ep3 = fixed build) |
| `G:\hyperporn\hyperporn_v8_*.mp4`, `hyperporn_v9_extended.mp4` | C: checkout | v8/v9 masters (moved 2026-11-24) |
| `G:\hyperporn\_up1080` | junction -> `M:\hyperporn_media\_up1080` | x2 library (49 outputs) + work segments |
| `G:\hyperporn\_max1080` | junction -> `M:\hyperporn_media\_max1080` | Maximal library + work segments |
| `C:\hyperporn_ultra_work` | junction -> `M:\hyperporn_ultra_work` | Episode intermediates/chunks (regenerable) |
| `G:\hyperporn\intermediates` | G: | GOP26 intermediates (v8 lineage) |
| `C:\Users\hyper\workspace\hyperporn` | C: | Second checkout, ComfyUI/gen_v9, submodules |

Rules: media is always git-ignored; junctions are transparent
to scripts (use the G:/C: paths in code, never the M: targets);
never move source files while an upscale/build queue is
running (its clip list was enumerated at startup - moving a
source mid-run killed the 2026-11-24 AI tier); free-space
guards in the builders watch the *script* drive, so keep
>5 GB free on G: even though outputs land on M:.
