$ErrorActionPreference = 'SilentlyContinue'
Remove-Item -LiteralPath topaz_test_small2_720p.mp4 -Force
$cmd = Start-Process -FilePath cmd.exe -ArgumentList '/c','run_topaz_small2.bat' -PassThru -WindowStyle Hidden -RedirectStandardOutput topaz_small2_babysit.out -RedirectStandardError topaz_small2_babysit.err
"started cmd pid=$($cmd.Id)" | Out-File -Encoding ascii topaz_small2_babysit.log
for ($i = 0; $i -lt 300; $i++) {
    $ff = Get-CimInstance Win32_Process -Filter "Name='ffmpeg.exe'" | Where-Object { $_.CommandLine -like '*topaz_test_small2_720p.mp4*' } | Select-Object -First 1
    if ($ff) {
        $p = Get-Process -Id $ff.ProcessId
        if ($p) { $p.PriorityClass = 'High' }
        $out = Get-Item topaz_test_small2_720p.mp4
        "iter=$i pid=$($ff.ProcessId) cpu=$([math]::Round($p.CPU,1)) mb=$([math]::Round($p.WorkingSet64/1MB,0)) out=$($out.Length)" | Out-File -Append -Encoding ascii topaz_small2_babysit.log
    } else {
        "iter=$i no-ffmpeg cmdExited=$($cmd.HasExited)" | Out-File -Append -Encoding ascii topaz_small2_babysit.log
        if ($cmd.HasExited) { break }
    }
    Start-Sleep -Seconds 5
}
Get-Content topaz_small2_babysit.log -Tail 25
