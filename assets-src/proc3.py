import sys;sys.argv=['x']
exec(open('proc.py').read().split("alpha_black('raw/L1")[0])
import base64,json
from PIL import Image,ImageDraw
import numpy as np
from collections import deque
# badge: remove branco ligado às bordas
im=Image.open('raw/user_badge.png').convert('RGBA');w,h=im.size;px=im.load()
seen=np.zeros((h,w),bool);q=deque([(x,y) for x in range(w) for y in (0,h-1)]+[(x,y) for y in range(h) for x in (0,w-1)])
while q:
    x,y=q.popleft()
    if x<0 or y<0 or x>=w or y>=h or seen[y,x]:continue
    r,g,b,a=px[x,y]
    if min(r,g,b)<215:continue
    seen[y,x]=True;px[x,y]=(r,g,b,0)
    q.extend([(x+1,y),(x-1,y),(x,y+1),(x,y-1)])
# halo semitransparente nas bordas
a=np.asarray(im).copy();m=np.asarray(seen)
from scipy.ndimage import binary_dilation
ring=binary_dilation(m,iterations=1)&~m
a[ring,3]=90
im=Image.fromarray(a);im=im.crop(im.getchannel('A').point(lambda v:255 if v>40 else 0).getbbox());im=im.resize((im.width*2,im.height*2),Image.LANCZOS);im.save('out/mt_badge.png')
import sys as _s
OFF=40
alpha_black('raw/user_word.png',box=(0,60,300,170),gain=2.5,fit=(300,120)).save('out/mt_word.png')
sh=Image.new('RGB',(520,300),'#2a35a8');x=0
for n in ['mt_badge','mt_word']:
    i=Image.open(f'out/{n}.png');sh.paste(i,(x,10),i);x+=i.width+10
sh.save('chk3.png');print(Image.open('out/mt_badge.png').size,Image.open('out/mt_word.png').size)
s=open('out/assets2.js').read().rstrip(';');d=json.loads(s[len('const IMG='):])
for n in ['mt_badge','mt_word']:d[n]='data:image/png;base64,'+base64.b64encode(open(f'out/{n}.png','rb').read()).decode()
open('out/assets3.js','w').write('const IMG='+json.dumps(d)+';')
