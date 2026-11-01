import json,base64,io
from PIL import Image
exec(open('patch7.py',encoding='utf8').read().split("d=json.loads")[0])
d=json.loads(open('out/assets3.js',encoding='utf8').read().rstrip(';')[len('const IMG='):])
d['sm0']=cover('raw3/s0.jpg',.5,.5)
open('out/assets3.js','w',encoding='utf8').write('const IMG='+json.dumps(d)+';')
s=open('v5.build.html',encoding='utf8').read()
a=s.index('const sm=(k,acc,sub)');b=s.index('const GAMES=[');s=s[:a]+s[b:]
a=s.index('["Adam Smasher');b=s.index('["Death Note"');s=s[:a]+s[b:]
F='''const ph=(k,acc)=>(g,t,c,p)=>{img(g,k,0,0,480);
 let q=g.createLinearGradient(0,150,0,H);q.addColorStop(0,"rgba(0,0,0,0)");q.addColorStop(.5,"rgba(0,0,0,.6)");q.addColorStop(1,"rgba(0,0,0,.88)");g.fillStyle=q;g.fillRect(0,150,W,170);
 g.save();g.shadowColor="rgba(0,0,0,.8)";g.shadowBlur=14;T(g,c.h+":"+c.m,240,128,96,"#fff",'center',GARA);g.restore();
 g.save();g.shadowColor="rgba(0,0,0,.9)";g.shadowBlur=6;tick(g,t,40,232,400,18,"#fff",GARA);g.restore();
 T(g,ART,40,256,13,"#d8d8d8",'left',GARA);T(g,"-"+fmt(TOT-p*TOT),440,256,13,"#fff",'right',GARA);
 R(g,40,264,400,2,"rgba(255,255,255,.25)");R(g,40,264,400*p,2,acc);R(g,40+400*p-3,261,6,8,acc);
 ICONS.forEach((b,i)=>T(g,b,90+i*100,302,18,i==1?acc:"#fff",'center',GARA))};
const PH0=ph("sm0","#8fe3d0"),PH1=ph("sm1","#37ffa0"),PH2=ph("sm2","#ffe600"),PH3=ph("sm3","#4dffd0");
'''
i=s.index('const GAMES=[');s=s[:i]+F+s[i:]
G='''["Template de foto · hora serifada","Foto de fundo, só a hora, nome da música, tempo que falta e botões. Fonte, cor e foto editáveis no app",[
 ["P1","Armadura + raio","sua imagem da silhueta com o raio azul",PH0],
 ["P2","Caveira + David","sua imagem do David com a caveira",PH1],
 ["P3","David amarelo","sua imagem de jaqueta amarela",PH2],
 ["P4","Sandevistan","sua imagem do rastro do Sandevistan",PH3]]],
'''
j=s.index('["Death Note"');s=s[:j]+G+s[j:]
open('v5.build.html','w',encoding='utf8').write(s)
open('../docs/temas-jogos-v5.html','w',encoding='utf8').write(s.replace('/*ASSETS*/',open('out/assets3.js',encoding='utf8').read()))
print('ok')
