import sys;sys.argv=['x']
exec(open('proc.py').read().split("alpha_black('raw/L1")[0])
import base64,json,os
from PIL import Image
alpha_black('raw/max4.jpg',box=(0,415,600,600),fit=(240,80)).save('out/maxword.png')
OFF=70;alpha_black('raw/max6.jpg',gain=4,fit=(190,190)).save('out/maxskull.png')
d={}
for n in ['maxword','maxskull']:d[n]='data:image/png;base64,'+base64.b64encode(open(f'out/{n}.png','rb').read()).decode()
mc={'grass_side':'grass_block_side','grass_top':'grass_top_t','dirt':'dirt','stone':'stone','planks':'oak_planks','log':'oak_log','cobble':'cobblestone','glass':'glass','leaves':'leaves_t','coal':'coal_ore','iron':'iron_ore','gold':'gold_ore','diamond':'diamond_ore','redstone':'redstone_ore','bricks':'bricks','door_b':'oak_door_bottom','door_t':'oak_door_top','torch':'torch','deepslate':'deepslate','apple':'apple','btn':'button','btn_h':'button_highlighted','hotbar':'hotbar','sel':'hotbar_selection'}
for k,f in mc.items():d['mc_'+k]='data:image/png;base64,'+base64.b64encode(open(f'mc/{f}.png','rb').read()).decode()
# grass side = side + overlay tintado
a=Image.open('mc/grass_block_side.png').convert('RGBA');o=Image.open('mc/grass_block_side_overlay.png').convert('RGBA');px=o.load()
for y in range(16):
    for x in range(16):
        r,g,b,al=px[x,y];px[x,y]=(r*121//255,g*192//255,b*90//255,al)
a.alpha_composite(o);a.save('mc/grass_side_t.png');d['mc_grass_side']='data:image/png;base64,'+base64.b64encode(open('mc/grass_side_t.png','rb').read()).decode()
s=open('out/assets.js').read().rstrip(';');old=json.loads(s[len('const IMG='):]);old.update(d)
open('out/assets2.js','w').write('const IMG='+json.dumps(old)+';')
sh=Image.new('RGB',(700,200),'#555');x=0
for n in ['maxword','maxskull']:
    i=Image.open(f'out/{n}.png').convert('RGBA');sh.paste(i,(x,10),i);x+=i.width+20
sh.save('chk2.png');print(len(old))
