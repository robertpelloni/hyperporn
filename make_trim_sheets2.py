import cv2, glob, os
import numpy as np
parts = sorted(glob.glob(r"intermediates\sissy_parts4\p_*.mp4"))
names = ["bost","csd2","sm6","smx","sm1","scs","sm2","sm3","sm9","sm7","sm8","sm5p1","sm5p2","scds","sm4"]
idx={n:i for i,n in enumerate(names)}
os.makedirs("framecheck/trimcheck", exist_ok=True)
TW,TH=256,144
def grab(cap,t):
    cap.set(cv2.CAP_PROP_POS_MSEC, max(0,t)*1000)
    ok,f=cap.read()
    return np.zeros((TH,TW,3),np.uint8) if not ok else cv2.resize(f,(TW,TH))
def sheet(name, times, mode):
    cap=cv2.VideoCapture(parts[idx[name]]); fps=cap.get(cv2.CAP_PROP_FPS); dur=cap.get(cv2.CAP_PROP_FRAME_COUNT)/fps
    cells=[]
    for t in times:
        tt=t if mode=="head" else dur+t
        f=grab(cap,tt); cv2.putText(f,f"{name} {t:+.0f}s",(5,18),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,255),2); cells.append(f)
    cap.release()
    cols=10; rows=(len(cells)+cols-1)//cols
    while len(cells)<rows*cols: cells.append(np.zeros((TH,TW,3),np.uint8))
    img=np.vstack([np.hstack(cells[r*cols:(r+1)*cols]) for r in range(rows)])
    out=f"framecheck/trimcheck/fine_{mode}_{name}.jpg"; cv2.imwrite(out,img,[cv2.IMWRITE_JPEG_QUALITY,80]); print(out)
for n in ["sm6","smx","sm1","sm2","sm9","sm8","sm5p1","scds","sm4","scs"]:
    sheet(n, list(range(0,41)), "head")
for n in ["scds","csd2","sm9","sm6"]:
    sheet(n, list(range(-70,1,2)) if n=="scds" else list(range(-24,1)), "tail")
