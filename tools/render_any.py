import numpy as np, sys, struct
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
SRC=sys.argv[1]; OUT=sys.argv[2]
hdr=open(SRC,'rb').read(18); BW=struct.unpack('<H',hdr[10:12])[0]; BH=struct.unpack('<H',hdr[14:16])[0]
L0=0x12; NB=BW*BH; IDX=L0+NB*64*6; NONE=0x7fffffffffffffff
land=np.fromfile(SRC,dtype='<u2',count=NB*64*3,offset=L0).reshape(BH,BW,8,8,3)
tid=land[...,0].transpose(0,2,1,3).reshape(BH*8,BW*8)
z=land[...,2].astype('<i2').transpose(0,2,1,3).reshape(BH*8,BW*8).astype(np.int16)
del land
rc=np.fromfile(SRC.rsplit('/',1)[0]+'/radarcol.mul',dtype='<u2')
col=rc[tid]; topz=z.copy()
idx=np.fromfile(SRC,dtype='<i8',count=NB,offset=IDX)
st=np.dtype([('d','u1'),('id','<u2'),('hue','<u2'),('u','<u2'),('z','<i2')])
data=open(SRC,'rb').read()
for b in np.nonzero(idx!=NONE)[0]:
    o=int(idx[b])+L0; c=int.from_bytes(data[o:o+4],'little')
    e=np.frombuffer(data,dtype=st,count=c,offset=o+4)
    pos=np.cumsum(e['d'].astype(np.int32)); by,bx=divmod(int(b),BW)
    Y=by*8+pos//8; X=bx*8+pos%8
    for i in range(c):
        y,x=Y[i],X[i]
        if 0<=y<BH*8 and 0<=x<BW*8 and e['z'][i]>=topz[y,x]:
            topz[y,x]=e['z'][i]; col[y,x]=rc[0x4000+int(e['id'][i])]
r=((col>>10)&31)*255//31; g=((col>>5)&31)*255//31; bb=(col&31)*255//31
img=np.stack([r,g,bb],-1).astype(np.uint8)
np.save(OUT+'.npy',img); Image.fromarray(img).resize((img.shape[1]//8,img.shape[0]//8)).save(OUT+'_preview.png')
print(SRC,img.shape)
