import json, base64, io, sys, numpy as np
from PIL import Image
from numpy.fft import rfft2, irfft2
TILES='/home/claude/uo-runes/tiles/5'
X0,Y0,X1,Y1=4736,0,7680,4096
TX0=X0//256; BIG=np.zeros((4096,(30-TX0)*256,3),np.uint8)
for tx in range(TX0,30):
  for ty in range(16):
    try: BIG[ty*256:ty*256+256,(tx-TX0)*256:(tx-TX0)*256+256]=np.asarray(Image.open(f'{TILES}/{tx}/{ty}.png').convert('RGB'))
    except Exception: pass
M=BIG[:, X0-TX0*256:X1-TX0*256]
full=(M.astype(int).sum(-1)>40).astype(np.float64)
np.save('/home/claude/dmatch/mapmask.npy', full)
def prep(B):
  H,W=B.shape; return B, rfft2(B), np.pad(B,((1,0),(1,0))).cumsum(0).cumsum(1), np.pad(B*B,((1,0),(1,0))).cumsum(0).cumsum(1)
def ncc(P, T):
  B,FB,I1,I2=P; H,W=B.shape; h,w=T.shape
  n=h*w; T0=T-T.mean(); tn=np.sqrt((T0*T0).sum())
  if tn==0 or h>=H or w>=W: return None
  C=irfft2(FB*rfft2(T0[::-1,::-1],s=(H,W)),s=(H,W))[h-1:,w-1:]
  S1=I1[h:,w:]-I1[:-h,w:]-I1[h:,:-w]+I1[:-h,:-w]; S2=I2[h:,w:]-I2[:-h,w:]-I2[h:,:-w]+I2[:-h,:-w]
  var=np.maximum(S2-S1*S1/n,1e-6)
  return C/(tn*np.sqrt(var))
half=full[::2,::2]; PH=prep(half); PF=prep(full)
data=json.load(open(sys.argv[1])); res={}
def tmask(lv):
  im=Image.open(io.BytesIO(base64.b64decode(lv['png']))).convert('RGBA'); a=np.asarray(im).astype(int)
  void=((a[...,:3].min(-1)>215)&(np.ptp(a[...,:3],-1)<20))|(a[...,3]<20)|(a[...,:3].max(-1)<25)
  return Image.fromarray((~void).astype(np.uint8)*255)
for key,lv in data.items():
  tm=tmask(lv); best=None
  for s in np.arange(2.4,6.21,0.1):   # coarse at half res
    w=int(round(tm.width/s/2)); h=int(round(tm.height/s/2))
    if w<6 or h<6: continue
    T=np.asarray(tm.resize((w,h),Image.BILINEAR))/255.0
    C=ncc(PH,T)
    if C is None: continue
    i=np.unravel_index(np.argmax(C),C.shape)
    if best is None or C[i]>best[0]: best=(C[i],s,i[1]*2,i[0]*2)
  _,s0,x0,y0=best; fb=None
  for s in np.arange(s0-0.12,s0+0.121,0.02):   # refine at full res, local window
    w=int(round(tm.width/s)); h=int(round(tm.height/s))
    T=np.asarray(tm.resize((w,h),Image.BILINEAR))/255.0
    ys,xs=max(0,y0-12),max(0,x0-12); sub=full[ys:ys+h+24, xs:xs+w+24]
    if sub.shape[0]<=h or sub.shape[1]<=w: continue
    C=ncc(prep(sub),T); i=np.unravel_index(np.argmax(C),C.shape)
    if fb is None or C[i]>fb[0]: fb=(C[i],s,xs+i[1],ys+i[0],w,h)
  sc,s,x,y,w,h=fb
  res[key]={'score':round(float(sc),3),'scale':round(float(s),3),'x':int(x)+X0,'y':int(y)+Y0,'w':w,'h':h,'name':lv['name']}
  print(key,res[key],flush=True)
json.dump(res,open('/home/claude/dmatch/align2.json','w'),indent=1)
