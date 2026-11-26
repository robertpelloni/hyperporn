import cv2, glob, os
import numpy as np
parts = sorted(glob.glob(r"intermediates\sissy_parts4\p_*.mp4"))
names = ["bost","csd2","sm6","smx","sm1","scs","sm2","sm3","sm9","sm7","sm8","sm5p1","sm5p2","scds","sm4"]
os.makedirs("framecheck/trimcheck", exist_ok=True)
TW,TH = 320,180
def grab(cap,t):
    cap.set(cv2.CAP_PROP_POS_MSEC, max(0,t)*1000)
    ok,f = cap.read()
    if not ok: return np.zeros((TH,TW,3),np.uint8)
    f = cv2.resize(f,(TW,TH))
    return f
def sheet(idxs, mode):
    rows=[]
    for i in idxs:
        cap=cv2.VideoCapture(parts[i]); fps=cap.get(cv2.CAP_PROP_FPS); n=cap.get(cv2.CAP_PROP_FRAME_COUNT); dur=n/fps
        times=[0,1,2,4,6,9,13,18,24,32] if mode=="head" else [dur-32,dur-24,dur-18,dur-13,dur-9,dur-6,dur-4,dur-2,dur-1,dur-0.2]
        cells=[]
        for t in times:
            f=grab(cap,t)
            lab = f"+{t:.0f}s" if mode=="head" else f"-{dur-t:.0f}s"
            cv2.putText(f, f"{names[i]} {lab}", (6,22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
            cells.append(f)
        rows.append(np.hstack(cells)); cap.release()
    img=np.vstack(rows)
    out=f"framecheck/trimcheck/{mode}_{idxs[0]:02d}_{idxs[-1]:02d}.jpg"
    cv2.imwrite(out,img,[cv2.IMWRITE_JPEG_QUALITY,82]); print(out, img.shape)
for mode in ("head","tail"):
    sheet(range(0,5),mode); sheet(range(5,10),mode); sheet(range(10,15),mode)
