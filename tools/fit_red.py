import json,base64,io,numpy as np
from PIL import Image
from numpy.fft import rfft2, irfft2
data=json.load(open('dungeon-maps.json')); k='IN|2'
x0,y0,x1,y1=330,470,1000,1030
A=np.load('facet5.npy')[y0:y1,x0:x1].astype(float)/255
red=lambda a: np.clip(a[...,0]-0.6*(a[...,1]+a[...,2]),0,1)
def prep(B): return B, rfft2(B), np.pad(B,((1,0),(1,0))).cumsum(0).cumsum(1), np.pad(B*B,((1,0),(1,0))).cumsum(0).cumsum(1)
def ncc(P,T):
  B,FB,I1,I2=P; H,W=B.shape; h,w=T.shape; n=h*w; T0=T-T.mean(); tn=np.sqrt((T0*T0).sum())
  if tn==0 or h>=H or w>=W: return None
  C=irfft2(FB*rfft2(T0[::-1,::-1],s=(H,W)),s=(H,W))[h-1:,w-1:]
  S1=I1[h:,w:]-I1[:-h,w:]-I1[h:,:-w]+I1[:-h,:-w]; S2=I2[h:,w:]-I2[:-h,w:]-I2[h:,:-w]+I2[:-h,:-w]
  return C/(tn*np.sqrt(np.maximum(S2-S1*S1/n,1e-6)))
from PIL import ImageFilter
P=prep(np.asarray(Image.fromarray((red(A)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))).astype(float))
im=Image.open(io.BytesIO(base64.b64decode(data[k]['png']))).convert('RGB'); best=None
for s in np.arange(1.5,9.01,0.05):
  w=int(round(im.width/s)); h=int(round(im.height/s))
  if w<8 or h<8: continue
  t=np.asarray(im.resize((w,h),Image.BILINEAR)).astype(float)/255
  T=np.asarray(Image.fromarray((red(t)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))).astype(float)
  C=ncc(P,T)
  if C is None: continue
  i=np.unravel_index(np.argmax(C),C.shape)
  if best is None or C[i]>best[0]: best=(float(C[i]),float(s),i[1],i[0],w,h)
sc,s,ix,iy,w,h=best; r={'facet':5,'score':round(sc,3),'scale':round(s,2),'x':x0+ix,'y':y0+iy,'w':w,'h':h}; print(r)
th=220; t=im.resize((int(im.width*th/im.height),th)); c=Image.fromarray((A[iy:iy+h,ix:ix+w]*255).astype(np.uint8)).resize((int(w*th/h),th),Image.NEAREST)
cell=Image.new('RGB',(t.width+c.width+10,th),(40,40,40)); cell.paste(t,(0,0)); cell.paste(c,(t.width+10,0)); cell.save('fit_IN_2r.png')
json.dump(r,open('fit_IN_2.json','w'))
