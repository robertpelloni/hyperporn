
import subprocess
src = r'C:\Users\hyper\Videos\sissymaker\Ajja_Liveset3h_Sissymaker_WetDream_STROBE140_60fps_FADE_v2.mp4'
W,H=1280,720
frame=W*H
cmd=['ffmpeg','-v','error','-ss','5000','-i',src,'-frames:v','200','-f','rawvideo','-pix_fmt','gray','-']
r=subprocess.run(cmd,capture_output=True)
data=r.stdout
n=len(data)//frame
lums=[]
for i in range(n):
    chunk=data[i*frame:(i+1)*frame]
    lums.append(sum(chunk)/len(chunk))
runs=[]
cur=None; start=0
for i,x in enumerate(lums):
    b = x<5
    if cur is None:
        cur=b; start=0
    elif b!=cur:
        runs.append((cur,start,i-1,i-start))
        cur=b; start=i
runs.append((cur,start,n-1,n-start))
for is_black,s,e,ln in runs:
    tag = 'BLACK' if is_black else 'content'
    print(f'{tag} {s:3d}-{e:3d} len={ln}')
