import json,base64,io,numpy as np,sys
from PIL import Image, ImageDraw
from numpy.fft import rfft2, irfft2
data=json.load(open('dungeon-maps.json'))
keys=['SC|3','DT|3.5','IN|2','OS|4','TT|3']
def prep(B): return B, rfft2(B), np.pad(B,((1,0),(1,0))).cumsum(0).cumsum(1), np.pad(B*B,((1,0),(1,0))).cumsum(0).cumsum(1)
def ncc(P,T):
  B,FB,I1,I2=P; H,W=B.shape; h,w=T.shape; n=h*w; T0=T-T.mean(); tn=np.sqrt((T0*T0).sum())
  if tn==0 or h>=H or w>=W: return None
  C=irfft2(FB*rfft2(T0[::-1,::-1],s=(H,W)),s=(H,W))[h-1:,w-1:]
  S1=I1[h:,w:]-I1[:-h,w:]-I1[h:,:-w]+I1[:-h,:-w]; S2=I2[h:,w:]-I2[:-h,w:]-I2[h:,:-w]+I2[:-h,:-w]
  return C/(tn*np.sqrt(np.maximum(S2-S1*S1/n,1e-6)))
res={k:None for k in keys}
for f in sys.argv[1:]:
  A=np.load(f'facet{f}.npy'); D=2 if A.shape[1]>3000 else 1
  Ah=A[::D,::D].astype(np.float64)/255; mask=(A[::D,::D].astype(int).sum(-1)>40).astype(float)
  P=[prep(mask)]+[prep(Ah[...,c]) for c in range(3)]
  for k in keys:
    im=Image.open(io.BytesIO(base64.b64decode(data[k]['png']))).convert('RGBA'); a=np.asarray(im).astype(int)
    void=((a[...,:3].min(-1)>215)&(np.ptp(a[...,:3],-1)<20))|(a[...,3]<20)|(a[...,:3].max(-1)<25)
    rgb=a[...,:3].copy(); rgb[void]=0
    for s in np.arange(2.0,8.01,0.1):
      w=int(round(im.width/s/D)); h=int(round(im.height/s/D))
      if w<8 or h<8: continue
      tm=np.asarray(Image.fromarray((~void).astype(np.uint8)*255).resize((w,h),Image.BILINEAR))/255.
      tc=np.asarray(Image.fromarray(rgb.astype(np.uint8)).resize((w,h),Image.BILINEAR))/255.
      cs=[ncc(P[0],tm)]+[ncc(P[i+1],tc[...,i]) for i in range(3)]
      if any(c is None for c in cs): continue
      C=0.5*cs[0]+0.5*(cs[1]+cs[2]+cs[3])/3
      i=np.unravel_index(np.argmax(C),C.shape)
      if res[k] is None or C[i]>res[k]['score']:
        res[k]={'facet':int(f),'score':round(float(C[i]),3),'scale':round(float(s),2),'x':int(i[1])*D,'y':int(i[0])*D,'w':w*D,'h':h*D}
  print('facet',f,'done',flush=True)
json.dump(res,open('facet_search.json','w'),indent=1); print(json.dumps(res,indent=1))
cells=[]
for k,r in res.items():
  A=np.load(f"facet{r['facet']}.npy"); th=200
  im=Image.open(io.BytesIO(base64.b64decode(data[k]['png']))).convert('RGB'); im=im.resize((int(im.width*th/im.height),th))
  c=Image.fromarray(A[r['y']:r['y']+r['h'],r['x']:r['x']+r['w']]).resize((int(r['w']*th/r['h']),th),Image.NEAREST)
  cell=Image.new('RGB',(im.width+c.width+10,th+16),(40,40,40)); cell.paste(im,(0,16)); cell.paste(c,(im.width+10,16))
  ImageDraw.Draw(cell).text((2,2),f"{k} f{r['facet']} {r['score']}",fill=(255,255,0)); cells.append(cell)
W=sum(c.width+8 for c in cells); sh=Image.new('RGB',(W,216)); x=0
for c in cells: sh.paste(c,(x,0)); x+=c.width+8
sh.save('facet_search.png')
