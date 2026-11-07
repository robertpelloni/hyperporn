$ErrorActionPreference = 'SilentlyContinue'
Remove-Item -LiteralPath topaz_test_real1s_4k.mp4 -Force
$cmd = Start-Process -FilePath cmd.exe -ArgumentList '/c','run_topaz_real1s.bat' -PassThru -WindowStyle Hidden -RedirectStandardOutput topaz_real1s_babysit.out -RedirectStandardError topaz_real1s_babysit.err
"started cmd pid=$($cmd.Id)" | Out-File -Encoding ascii topaz_real1s_babysit.log
for ($i = 0; $i -lt 720; $i++) {
    $ff = Get-CimInstance Win32_Process -Filter "Name='ffmpeg.exe'" | Where-Object { $_.CommandLine -like '*topaz_test_real1s_4k.mp4*' } | Select-Object -First 1
    if ($ff) {
        $p = Get-Process -Id $ff.ProcessId
        if ($p) { $p.PriorityClass = 'High' }
        $out = Get-Item topaz_test_real1s_4k.mp4
        "iter=$i pid=$($ff.ProcessId) cpu=$([math]::Round($p.CPU,1)) mb=$([math]::Round($p.WorkingSet64/1MB,0)) out=$($out.Length)" | Out-File -Append -Encoding ascii topaz_real1s_babysit.log
    } else {
        "iter=$i no-ffmpeg cmdExited=$($cmd.HasExited)" | Out-File -Append -Encoding ascii topaz_real1s_babysit.log
        if ($cmd.HasExited) { break }
    }
    Start-Sleep -Seconds 5
}
Get-Content topaz_real1s_babysit.log -Tail 25
