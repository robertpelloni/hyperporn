$names = @("python","ffmpeg")
Get-Process -Name $names -ErrorAction SilentlyContinue | ForEach-Object { try { $_.PriorityClass = "BelowNormal" } catch { } }
Write-Output "low-priority-sweep-done"
