$ErrorActionPreference = 'SilentlyContinue'
for ($i = 0; $i -lt 55; $i++) {
    $ff = Get-CimInstance Win32_Process -Filter "Name='ffmpeg.exe'" | Where-Object { $_.ExecutablePath -like '*Topaz*' } | Select-Object -First 1
    if (-not $ff) { "iter=$i none" | Out-File -Append -Encoding ascii topaz_guard_any.log; Start-Sleep -Seconds 5; continue }
    $p = Get-Process -Id $ff.ProcessId
    if ($p) { $p.PriorityClass = 'High' }
    $a = Get-Item topaz_real1s_A.mp4; $b = Get-Item topaz_real1s_B.mp4; $f = Get-Item topaz_test_real1s_4k.mp4
    "iter=$i cpu=$([math]::Round($p.CPU,0)) mb=$([math]::Round($p.WorkingSet64/1MB,0)) A=$($a.Length) B=$($b.Length) FINAL=$($f.Length)" | Out-File -Append -Encoding ascii topaz_guard_any.log
    Start-Sleep -Seconds 5
}
Get-Content topaz_guard_any.log -Tail 10
