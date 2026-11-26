# TODO

- RUNNING (BelowNormal): _max1080 queue - continue: python upscale_max.py (resumable).
  Remaining after wct: ~42 clips; long tail drip1/ext05/ext06/wet. Do NOT move _sm/_ai sources mid-run.
- Awaiting user: logo/intro timestamps spotted in episodes (targeted trim + episode rebuild);
  decision on rented-GPU day vs finishing the max queue locally; roast continuation if wanted.
- When .git/index.lock clears (external holder): git reset --mixed HEAD in G:\hyperporn to resync the main index, then retire temp-index commits.
- Optional: rebuild episodes from _max1080 once complete; add -mask-depth variants (strobe-free export).
- Optional: finish _up1080 x2 for drip1/ext05/ext06/wet only if max tier is frozen (else duplicate effort).
- Re-run after any rebuild/move: python -m pytest tests/ -q ; python qc_check.py
- Prune stale *.log/*.err and the drifting ep3 backup (M:\hyperporn_ultra_work\ultramix_ep3_drifting_mask.mp4.bak) when user confirms.
