from PIL import Image,ImageChops
import numpy as np,colorsys,base64,json
OFF=18
def alpha_black(f,box=None,gain=1.6,fit=None):
    im=Image.open(f).convert('RGB')
    if box: im=im.crop(box)
    a=np.asarray(im).astype(float);m=a.max(2)
    al=np.clip((m-OFF)*gain,0,255)
    rgb=np.where(m[...,None]>0,a/np.maximum(m[...,None],1)*255,0)
    out=np.dstack([np.clip(rgb,0,255),al]).astype('uint8');o=Image.fromarray(out,'RGBA')
    bb=o.getchannel('A').point(lambda v:255 if v>40 else 0).getbbox()
    o=o.crop(bb)
    if fit:o.thumbnail(fit,Image.LANCZOS)
    return o
alpha_black('raw/L1.jpg',fit=(200,240)).save('out/L.png')
e=alpha_black('raw/eye4.jpg',fit=(150,150));e.save('out/eye_orange.png')
# versão ciano: gira o matiz do laranja
h=np.asarray(e).astype(float);r,g,b,a=[h[...,i] for i in range(4)]
hsv=np.asarray(e.convert('RGB').convert('HSV')).astype(float);hs=hsv[...,0]
shift=((130/360)*255);hs2=np.where((hs>8)&(hs<45),(hs+shift)%256,hs)
hsv[...,0]=hs2;c=Image.fromarray(hsv.astype('uint8'),'HSV').convert('RGB');c=np.dstack([np.asarray(c),a]).astype('uint8');Image.fromarray(c,'RGBA').save('out/eye_cyan.png')
alpha_black('raw/ara1.jpg',box=(0,0,600,432),fit=(170,170)).save('out/ara.png')
alpha_black('raw/mil4.jpg',fit=(180,180)).save('out/mil.png')
# helmet: pixelado 80px, 32 cores
im=Image.open('raw/halo3.jpg').convert('RGB');s=im.resize((100,100),Image.LANCZOS).quantize(40,dither=0).convert('RGB');s.save('out/helmet.png')
sh=Image.new('RGB',(900,260),'#222')
x=0
for n in ['L','eye_orange','eye_cyan','ara','mil','helmet']:
    i=Image.open(f'out/{n}.png').convert('RGBA');sh.paste(i,(x,10),i);x+=i.width+20
sh.save('sheet_out.png')
d={n:'data:image/png;base64,'+base64.b64encode(open(f'out/{n}.png','rb').read()).decode() for n in ['L','eye_orange','eye_cyan','ara','mil','helmet']}
open('out/assets.js','w').write('const IMG='+json.dumps(d)+';')
print({n:Image.open(f'out/{n}.png').size for n in d})
