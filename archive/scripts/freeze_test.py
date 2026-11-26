
import subprocess, hashlib
src = r'C:\Users\hyper\Videos\sissymaker\Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps_FADE_v2.mp4'
# grab 5 frames spanning one full clip (26 frames = 0.433s) in the second half
times = [8000.0, 8000.10, 8000.20, 8000.30, 8000.40]
hashes = []
for t in times:
    cmd=['ffmpeg','-v','error','-ss',f'{t:.3f}','-i',src,'-frames:v','1','-f','rawvideo','-pix_fmt','gray','-']
    r=subprocess.run(cmd,capture_output=True)
    h=hashlib.md5(r.stdout).hexdigest()[:12]
    hashes.append(h)
    print(f't={t:.2f} md5={h}')
print('unique:', len(set(hashes)), '/', len(hashes))
print('FREEZE_PASS' if len(set(hashes))==len(hashes) else 'FREEZE_FAIL')
