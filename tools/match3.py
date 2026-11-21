import json,base64,io,numpy as np
from PIL import Image
from numpy.fft import rfft2, irfft2
X0=4736; TX0=X0//256
BIG=np.load('big.npy'); M=BIG[:, X0-TX0*256:]          # dungeon area RGB, 1px=1tile
full=np.load('mapmask.npy')
data=json.load(open('/mnt/user-data/uploads/Games/uorunes-build/dungeon-maps.json'))
al=json.load(open('align2.json'))
bad=['SC|1','TT|1']
claimed=np.zeros(full.shape,bool)
for k,a in al.items():
  if k in bad: continue
  claimed[a['y']:a['y']+a['h'], a['x']-X0:a['x']-X0+a['w']]=True
def prep(B):
  return B, rfft2(B), np.pad(B,((1,0),(1,0))).cumsum(0).cumsum(1), np.pad(B*B,((1,0),(1,0))).cumsum(0).cumsum(1)
def ncc(P,T):
  B,FB,I1,I2=P; H,W=B.shape; h,w=T.shape; n=h*w; T0=T-T.mean(); tn=np.sqrt((T0*T0).sum())
  if tn==0 or h>=H or w>=W: return None
  C=irfft2(FB*rfft2(T0[::-1,::-1],s=(H,W)),s=(H,W))[h-1:,w-1:]
  S1=I1[h:,w:]-I1[:-h,w:]-I1[h:,:-w]+I1[:-h,:-w]; S2=I2[h:,w:]-I2[:-h,w:]-I2[h:,:-w]+I2[:-h,:-w]
  return C/(tn*np.sqrt(np.maximum(S2-S1*S1/n,1e-6)))
Mh=M[::2,::2].astype(np.float64)/255; fh=full[::2,::2]; ch=claimed[::2,::2]
P=[prep(fh)]+[prep(Mh[...,c]) for c in range(3)]
CI=np.pad(ch.astype(float),((1,0),(1,0))).cumsum(0).cumsum(1)
anchors={'SC|1':(5176,2489),'TT|1':(6660,2058)}
out={}
for k in bad:
  im=Image.open(io.BytesIO(base64.b64decode(data[k]['png']))).convert('RGBA'); a=np.asarray(im).astype(int)
  void=((a[...,:3].min(-1)>215)&(np.ptp(a[...,:3],-1)<20))|(a[...,3]<20)|(a[...,:3].max(-1)<25)
  rgb=a[...,:3].copy(); rgb[void]=0
  best=[]
  for s in np.arange(2.2,6.6,0.1):
    w=int(round(im.width/s/2)); h=int(round(im.height/s/2))
    if w<6 or h<6: continue
    tm=np.asarray(Image.fromarray((~void).astype(np.uint8)*255).resize((w,h),Image.BILINEAR))/255.
    tc=np.asarray(Image.fromarray(rgb.astype(np.uint8)).resize((w,h),Image.BILINEAR))/255.
    cs=[ncc(P[0],tm)]+[ncc(P[i+1],tc[...,i]) for i in range(3)]
    if any(c is None for c in cs): continue
    C=0.6*cs[0]+0.4*(cs[1]+cs[2]+cs[3])/3
    # penalise overlap with claimed regions
    ov=(CI[h:,w:]-CI[:-h,w:]-CI[h:,:-w]+CI[:-h,:-w])/(h*w)
    C=C-1.0*ov[:C.shape[0],:C.shape[1]]
    if k in anchors:
      ax,ay=anchors[k]; ax=(ax-X0)//2; ay=ay//2
      yy,xx=np.mgrid[0:C.shape[0],0:C.shape[1]]
      inside=(xx<=ax)&(ax<xx+w)&(yy<=ay)&(ay<yy+h); C=np.where(inside,C,-9)
    i=np.unravel_index(np.argmax(C),C.shape)
    best.append((float(C[i]),float(s),int(i[1])*2+X0,int(i[0])*2,w*2,h*2))
  best.sort(reverse=True); b=best[0]
  out[k]={'score':round(b[0],3),'scale':round(b[1],2),'x':b[2],'y':b[3],'w':b[4],'h':b[5],'name':data[k]['name']}
  print(k,out[k],flush=True)
json.dump(out,open('align3b.json','w'),indent=1)
