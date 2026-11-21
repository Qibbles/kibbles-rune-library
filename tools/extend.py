import json,base64,io,os,numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
data=json.load(open('dungeon-maps.json'))
F=np.load('full.npy',mmap_mode='r'); F5=np.load('facet5.npy')
W,H=8960,4096; X5=7680
C=np.zeros((H,W,3),np.uint8); C[:, :7680]=F[:H,:7680]
C[0:1300, X5:X5+1280]=F5[0:1300,0:1280]
place={}; S=4.0   # Butler level pictures at ~4 image px per tile
x,y,rowh=X5+40,1380,0
for k in ['SC|3','DT|3.5','OS|4','TT|3']:
  im=Image.open(io.BytesIO(base64.b64decode(data[k]['png']))).convert('RGB')
  w,h=int(round(im.width/S)),int(round(im.height/S))
  if x+w>W-20: x=X5+40; y+=rowh+60; rowh=0
  a=np.asarray(im.resize((w,h),Image.LANCZOS)).copy()
  white=(a.min(-1)>215)&(np.ptp(a,-1)<20); a[white]=0
  C[y:y+h,x:x+w]=a; place[k]={'x':x,'y':y,'w':w,'h':h,'name':data[k]['name'],'src':'butler'}
  x+=w+60; rowh=max(rowh,h)
place['IN|2']={'x':400+X5,'y':560,'w':440,'h':400,'name':'Inferno Level 2','src':'map5'}
json.dump(place,open('extra_align.json','w'),indent=1); print(place)
os.makedirs('ext_tiles',exist_ok=True)
img=Image.fromarray(C); MZ=5; n=0
for z in range(MZ,-1,-1):
  sc=2**(z-MZ); w,h=round(W*sc),round(H*sc)
  im=img if z==MZ else img.resize((w,h),Image.LANCZOS)
  for tx in range((w+255)//256):
    if z==MZ and tx<30: continue          # unchanged z5 columns
    for ty in range((h+255)//256):
      t=Image.new('RGB',(256,256)); t.paste(im.crop((tx*256,ty*256,min(w,tx*256+256),min(h,ty*256+256))),(0,0))
      d=f'ext_tiles/{z}/{tx}'; os.makedirs(d,exist_ok=True); t.save(f'{d}/{ty}.png',optimize=True); n+=1
print('tiles',n)
import shutil; shutil.make_archive('ext_tiles','zip','ext_tiles')
