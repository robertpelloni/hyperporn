import cv2, glob
import numpy as np, os
parts = sorted(glob.glob(r"intermediates\sissy_parts5\p_*.mp4"))
names = ["bost","csd2","sm6","smx","sm1","scs","sm2","sm3","sm9","sm7","sm8","sm5p1","sm5p2","scds","sm4"]
TW,TH=256,144
def grab(cap,t):
    cap.set(cv2.CAP_PROP_POS_MSEC, max(0,t)*1000)
    ok,f=cap.read()
    return np.zeros((TH,TW,3),np.uint8) if not ok else cv2.resize(f,(TW,TH))
rows=[]
for i,p in enumerate(parts):
    cap=cv2.VideoCapture(p); fps=cap.get(cv2.CAP_PROP_FPS); dur=cap.get(cv2.CAP_PROP_FRAME_COUNT)/fps
    cells=[]
    for t in [0,1,3,6,10, dur-10,dur-6,dur-3,dur-1,dur-0.2]:
        f=grab(cap,t); lab=f"{names[i]} {'+%.0f'%t if t<100 else '-%.0f'%(dur-t)}"
        cv2.putText(f,lab,(5,18),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,255),2); cells.append(f)
    rows.append(np.hstack(cells)); cap.release()
img=np.vstack(rows)
os.makedirs("framecheck/trimcheck",exist_ok=True)
cv2.imwrite("framecheck/trimcheck/verify_v8.jpg",img,[cv2.IMWRITE_JPEG_QUALITY,80])
print("wrote", img.shape)
