import urllib.request,os,sys
from PIL import Image,ImageDraw
os.makedirs('raw',exist_ok=True);cnt={}
for ln in open('urls.txt'):
    k,i=ln.split();cnt[k]=cnt.get(k,0)+1;f=f'raw/{k}{cnt[k]}.jpg'
    try:
        d=urllib.request.urlopen(urllib.request.Request(f'https://th.bing.com/th/id/{i}?w=600&h=600&c=7&rs=1',headers={'User-Agent':'Mozilla/5.0'}),timeout=20).read();open(f,'wb').write(d)
    except Exception as e:print('fail',f,e)
for k in cnt:
    fs=[f'raw/{k}{n}.jpg' for n in range(1,cnt[k]+1) if os.path.exists(f'raw/{k}{n}.jpg')]
    sh=Image.new('RGB',(4*260,((len(fs)+3)//4)*260),'#444');d=ImageDraw.Draw(sh)
    for n,f in enumerate(fs):
        im=Image.open(f).convert('RGB');im.thumbnail((250,250));x,y=(n%4)*260,(n//4)*260;sh.paste(im,(x,y));d.text((x+4,y+4),str(n+1),fill='yellow')
    sh.save(f'sheet_{k}.png')
