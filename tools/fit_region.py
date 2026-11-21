import json,base64,io,numpy as np,sys
from PIL import Image, ImageDraw
from numpy.fft import rfft2, irfft2
data=json.load(open('dungeon-maps.json'))
k,f,x0,y0,x1,y1=sys.argv[1],sys.argv[2],*map(int,sys.argv[3:7]); SUP=int(sys.argv[7]) if len(sys.argv)>7 else 1
A=np.load(f'facet{f}.npy')[y0:y1,x0:x1]
def prep(B): return B, rfft2(B), np.pad(B,((1,0),(1,0))).cumsum(0).cumsum(1), np.pad(B*B,((1,0),(1,0))).cumsum(0).cumsum(1)
def ncc(P,T):
  B,FB,I1,I2=P; H,W=B.shape; h,w=T.shape; n=h*w; T0=T-T.mean(); tn=np.sqrt((T0*T0).sum())
  if tn==0 or h>=H or w>=W: return None
  C=irfft2(FB*rfft2(T0[::-1,::-1],s=(H,W)),s=(H,W))[h-1:,w-1:]
  S1=I1[h:,w:]-I1[:-h,w:]-I1[h:,:-w]+I1[:-h,:-w]; S2=I2[h:,w:]-I2[:-h,w:]-I2[h:,:-w]+I2[:-h,:-w]
  return C/(tn*np.sqrt(np.maximum(S2-S1*S1/n,1e-6)))
big=np.asarray(Image.fromarray(A).resize((A.shape[1]*SUP,A.shape[0]*SUP),Image.NEAREST)).astype(float)/255
mask=(big.sum(-1)>0.16).astype(float)
P=[prep(mask)]+[prep(big[...,c]) for c in range(3)]
im=Image.open(io.BytesIO(base64.b64decode(data[k]['png']))).convert('RGBA'); a=np.asarray(im).astype(int)
void=((a[...,:3].min(-1)>215)&(np.ptp(a[...,:3],-1)<20))|(a[...,3]<20)|(a[...,:3].max(-1)<25)
rgb=a[...,:3].copy(); rgb[void]=0; best=None
for s in np.arange(2.0,9.01,0.1):
  w=int(round(im.width/s*SUP)); h=int(round(im.height/s*SUP))
  if w<8 or h<8: continue
  tm=np.asarray(Image.fromarray((~void).astype(np.uint8)*255).resize((w,h),Image.BILINEAR))/255.
  tc=np.asarray(Image.fromarray(rgb.astype(np.uint8)).resize((w,h),Image.BILINEAR))/255.
  cs=[ncc(P[0],tm)]+[ncc(P[i+1],tc[...,i]) for i in range(3)]
  if any(c is None for c in cs): continue
  C=0.5*cs[0]+0.5*(cs[1]+cs[2]+cs[3])/3
  i=np.unravel_index(np.argmax(C),C.shape)
  if best is None or C[i]>best[0]: best=(float(C[i]),float(s),i[1],i[0],w,h)
sc,s,ix,iy,w,h=best
r={'facet':int(f),'score':round(sc,3),'scale':round(s,2),'x':x0+ix/SUP,'y':y0+iy/SUP,'w':w/SUP,'h':h/SUP}; print(k,r)
th=220; t=im.convert('RGB').resize((int(im.width*th/im.height),th))
c=Image.fromarray((big[iy:iy+h,ix:ix+w]*255).astype(np.uint8)).resize((int(w*th/h),th),Image.NEAREST)
cell=Image.new('RGB',(t.width+c.width+10,th),(40,40,40)); cell.paste(t,(0,0)); cell.paste(c,(t.width+10,0)); cell.save(f'fit_{k.replace("|","_")}.png')
json.dump(r,open(f'fit_{k.replace("|","_")}.json','w'))
