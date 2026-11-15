$ErrorActionPreference = 'SilentlyContinue'
for ($i = 0; $i -lt 55; $i++) {
    $ff = Get-CimInstance Win32_Process -Filter "Name='ffmpeg.exe'" | Where-Object { $_.CommandLine -like '*topaz_test_real1s_4k.mp4*' } | Select-Object -First 1
    if (-not $ff) { "iter=$i done" | Out-File -Append -Encoding ascii topaz_real1s_guard.log; break }
    $p = Get-Process -Id $ff.ProcessId
    if ($p) { $p.PriorityClass = 'High' }
    $out = Get-Item topaz_test_real1s_4k.mp4
    "iter=$i cpu=$([math]::Round($p.CPU,1)) mb=$([math]::Round($p.WorkingSet64/1MB,0)) out=$($out.Length)" | Out-File -Append -Encoding ascii topaz_real1s_guard.log
    Start-Sleep -Seconds 5
}
Get-Content topaz_real1s_guard.log -Tail 12
