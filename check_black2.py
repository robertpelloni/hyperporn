
import subprocess
src = r'C:\Users\hyper\Videos\sissymaker\Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps_FADE_v2.mp4'
W,H=1280,720
frame=W*H
times = [0, 100, 500, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 10700]
for t in times:
    cmd=['ffmpeg','-v','error','-ss',str(t),'-i',src,'-frames:v','130','-f','rawvideo','-pix_fmt','gray','-']
    r=subprocess.run(cmd,capture_output=True)
    data=r.stdout
    n=len(data)//frame
    if n==0:
        print(f't={t}: no frames')
        continue
    lums=[]
    for i in range(n):
        chunk=data[i*frame:(i+1)*frame]
        lums.append(sum(chunk)/len(chunk) if chunk else -1)
    black=sum(1 for x in lums if x<5)
    mn=min(lums)
    print(f't={t}: n={n} black={black} min={mn:.1f}')
