import numpy as np, sys, time
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
SRC=sys.argv[1]; ORDER=sys.argv[2] if len(sys.argv)>2 else 'yx'
BW,BH=1344,768; L0=0x12; NB=BW*BH; IDX=L0+NB*64*6; NONE=0x7fffffffffffffff
t0=time.time()
land=np.fromfile(SRC,dtype='<u2',count=NB*64*3,offset=L0).reshape(BH,BW,8,8,3)
if ORDER=='xy': land=land.transpose(0,1,3,2,4)   # cell idx = x*8+y
tid=land[...,0].transpose(0,2,1,3).reshape(BH*8,BW*8)
z=land[...,2].astype('<i2').transpose(0,2,1,3).reshape(BH*8,BW*8)
del land
rc=np.fromfile(SRC.replace('map0.uoo','radarcol.mul'),dtype='<u2')
col=rc[tid].copy(); topz=z.astype(np.int16).copy()
idx=np.fromfile(SRC,dtype='<i8',count=NB,offset=IDX)
st=np.dtype([('d','u1'),('id','<u2'),('hue','<u2'),('u','<u2'),('z','<i2')])
f=open(SRC,'rb'); data=f.read(); n=0
for b in np.nonzero(idx!=NONE)[0]:
    o=int(idx[b])+L0
    c=int.from_bytes(data[o:o+4],'little')
    e=np.frombuffer(data,dtype=st,count=c,offset=o+4)
    pos=np.cumsum(e['d'].astype(np.int32))
    by,bx=divmod(int(b),BW)
    if ORDER=='xy': cx,cy=pos//8,pos%8
    else: cy,cx=pos//8,pos%8
    Y=by*8+cy; X=bx*8+cx
    for i in range(c):
        y,x=Y[i],X[i]
        if 0<=y<BH*8 and 0<=x<BW*8 and e['z'][i]>=topz[y,x]:
            topz[y,x]=e['z'][i]; col[y,x]=rc[0x4000+int(e['id'][i])]
    n+=c
print('statics',n,'t',time.time()-t0)
r=((col>>10)&31)*255//31; g=((col>>5)&31)*255//31; bb=(col&31)*255//31
img=np.stack([r,g,bb],-1).astype(np.uint8)
np.save('full.npy',img)
print('done',time.time()-t0)
