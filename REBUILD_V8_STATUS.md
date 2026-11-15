# v8 rebuild status (2026-11-07, this machine)

## Deliverables (on G:\hyperporn)

| File | Size | Verified |
|---|---|---|
| `liveset60_v8/video_fade_v8.mp4` | 9.91 GB | 646,464 frames, 1280x720, 60 fps, h264, no audio |
| `hyperporn_v8_autodj.mp4` | 10.16 GB | mux VERIFY PASS: dur 10774.400, frames 646,464, AAC bed |
| `hyperporn_v8_hypno.mp4` | optional variant | music 0.70 + hypo_mix_v5 0.95, amix normalize=0 + limiter (PIPELINE 4.3) |

Note: v8 re-cut is 646,464 frames (24,864 clips x 26). The old v3 master
was 646,461 (3 frames / 0.05 s shorter). mux_v8.py constants updated.

## How it was rebuilt

- Sources/intermediates were on G: (C: had only 3.3 GB free; G: 173 GB).
  Copied into this repo: intermediates (sissy_all_gop26_v2, wet_gop26),
  beds/*.m4a, autodj_mix.flac, hypo_mix_v5.m4a, mask_p26_fixed.mp4,
  build_v8_full.py, mux_v8.py, mux_v8_hypno.py, sm_trim_report_v8.json.
- `build_v8_full.py` resumed on G: chunks 0-1 skipped (already faded),
  chunks 2-5 cut + faded (~6-8 min per chunk on this machine), final
  concat stream-copy. Fixed: Windows file-lock crash on clip cleanup
  (safe_unlink retry) that killed the first run after chunk 1.
- Full ffmpeg 7.1.1 (gyan essentials, libx264) at
  `G:\hyperporn\tools\ffmpeg-7.1.1-essentials_build\bin` — the PATH
  ffmpeg 6.0 is a minimal build without libx264/ffprobe.
- Audio: autodj_mix.flac (Auto DJ v8.15, kick-synced, mastered).
  Measured: -15.62 LUFS integrated, TP -0.91, LRA 5.6 — already
  normalized; mux trims/pads to exactly 10774.40 s, AAC 192k.
  Hypno variant script: mux_v8_hypno.py (off by default).

## Topaz 1-second test (this machine, GPU)

- Runtime: extracted MSI ffmpeg at
  `G:\topaz-extract` equivalent on G: (`topaz-extract\...\ffmpeg.exe`),
  tvai_up verified, prob-4 weights present, device=0 (GTX 1060 CUDA).
- `comfy-pipeline/output/topaz_test_1s_4k_h264.mp4`: 3840x2160,
  h264 (h264_nvenc, no libx264 in Topaz build), 60/60 frames, 1.000 s.
  Speed: ~5.7 s/frame at 4K on the 3 GB GTX 1060 (1 s clip = 5m41s).
- WATERMARK: present. A benign test-pattern render
  (`topaz_benign_1s.mp4`, frame 30 extracted and inspected) shows the
  centered "Topaz Labs" watermark, because topaz-models-min has no
  auth.tpz. There is no supported flag to remove it; sign in once in
  the Topaz app (login.exe in the extract) to create a valid auth,
  then re-render. No bypass was attempted.

## Disk notes

- C: free was 3.3 GB. ~44.7 GB of Temp is `jules-verify-*` folders
  (another agent's work, left untouched). Freed only this session's
  pip cache (~9 GB). Final 10 GB masters stay on G:; they do not fit
  on C: alongside the copies. Delete intermediates copies here if C:
  space is needed.
