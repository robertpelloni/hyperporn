# DEPLOY - environment & setup (this laptop)

This project has no server, UI, dashboard, or tray app - it is
a local media pipeline. "Deployment" is the working layout:

## Hardware/OS
Windows, PowerShell, Python 3.15 (`C:\Python315`), GTX 1060 3GB
(driver 582.66), ffmpeg 7.1.1 gyan essentials at
`tools/ffmpeg-7.1.1-essentials_build/bin` (the PATH ffmpeg is a
minimal build without libx264/ffprobe - always use the tools/
copy or the scripts, which hardcode it). GPU jobs run at
BelowNormal priority.

## Layout (see STORAGE.md for the full map)
- `G:\hyperporn` - repo, sources (`_sm`, `_ai`), finals.
- `C:\Users\hyper\workspace\hyperporn` - second checkout
  (ComfyUI pipeline + its vendor submodules live here;
  submodules are pinned - ComfyUI v0.3.44, because HEAD
  crashes on this torch/GPU combo - do not blindly update).
- `M:\hyperporn_media\_up1080`, `M:\hyperporn_media\_max1080`,
  `M:\hyperporn_ultra_work` - library + scratch volumes,
  junctioned from G:/C: paths.
- Real-ESRGAN: `C:\Users\hyper\workspace\hyperporn\comfy-pipeline\
  tools\realesrgan\realesrgan-ncnn-vulkan.exe` (models included).
- Topaz: extracted MSI under `topaz-extract\` (git-ignored;
  watermark without a legit `auth.tpz` - see TOPAZ_4K_UPSCALE.md).

## Run
- Episodes: `python build_episodes.py`, `python build_episode3.py`
- Extension: `python build_v9_extend.py`
- Libraries: `python upscale1080.py [pass|ai|<stem>]`,
  `python upscale_max.py [<stem>]` (all resumable)
- QC/tests: `python qc_check.py`, `python -m pytest tests/ -q`
- Topaz stage: `python cut_for_upscale.py`,
  `python upscale_topaz.py`, `python reassemble_upscaled.py`

## Coordination
Edge with `--remote-debugging-port=9222`; coordination scripts
enumerate `http://localhost:9222/json/list` and drive the
muse.ai / ChatGPT / Gemini tabs. Identify as
"[model in harness in cwd on laptop]" and leave HPN-* markers.
