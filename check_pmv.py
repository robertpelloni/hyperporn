import subprocess, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

r = subprocess.run(["cmd", "/c", "tasklist /FI \"IMAGENAME eq ffmpeg.exe\" /FO CSV"],
                    capture_output=True)
print("ffmpeg:", r.stdout.decode(errors="replace"))

r = subprocess.run(["cmd", "/c", "tasklist /FI \"IMAGENAME eq python.exe\" /FO CSV"],
                    capture_output=True)
print("python:", r.stdout.decode(errors="replace"))
