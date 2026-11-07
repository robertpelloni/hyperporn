import cv2, glob
parts = sorted(glob.glob(r"intermediates\sissy_parts4\p_*.mp4"))
names = ["bost","csd2","sm6","smx","sm1","scs","sm2","sm3","sm9","sm7","sm8","sm5p1","sm5p2","scds","sm4"]
def grab(cap,t):
    cap.set(cv2.CAP_PROP_POS_MSEC, t*1000)
    ok,f = cap.read()
    return cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) if ok else None
for i,p in enumerate(parts):
    cap = cv2.VideoCapture(p); fps=cap.get(cv2.CAP_PROP_FPS); n=cap.get(cv2.CAP_PROP_FRAME_COUNT); dur=n/fps
    print(f"\n== p_{i:02d} {names[i]} dur={dur:.1f}")
    for label,times in [("HEAD",[0.3,1,2,3,5,7,10,15,20,25,30,40]),("TAIL",[dur-40,dur-30,dur-20,dur-15,dur-10,dur-7,dur-5,dur-3,dur-2,dur-1,dur-0.3])]:
        print(" "+label); prev=None
        for t in times:
            g=grab(cap,t)
            if g is None: continue
            d=f" diff={float(cv2.absdiff(g,prev).mean()):.1f}" if prev is not None else ""
            print(f"  t={t:.1f} mean={float(g.mean()):.0f} std={float(g.std()):.0f}{d}"); prev=g
    cap.release()
