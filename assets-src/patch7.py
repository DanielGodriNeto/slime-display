import json,base64,io
from PIL import Image
def cover(f,fx=.5,fy=.5):
    i=Image.open(f).convert('RGB');w,h=i.size;r=1.5
    cw,ch=(w,round(w/r)) if w/h<r else (round(h*r),h)
    x=round((w-cw)*fx);y=round((h-ch)*fy);i=i.crop((x,y,x+cw,y+ch)).resize((480,320),Image.LANCZOS)
    b=io.BytesIO();i.save(b,'JPEG',quality=82);return 'data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode()
d=json.loads(open('out/assets3.js',encoding='utf8').read().rstrip(';')[len('const IMG='):])
d['sm1']=cover('raw3/s1.webp',1,.5);d['sm2']=cover('raw3/s2.jpg',.5,.5);d['sm3']=cover('raw3/s3.webp',.5,0)
open('out/assets3.js','w',encoding='utf8').write('const IMG='+json.dumps(d)+';')
s=open('v5.build.html',encoding='utf8').read()
F='''const sm=(k,acc,sub)=>(g,t,c,p)=>{img(g,k,0,0,480);
 let q=g.createLinearGradient(0,0,0,100);q.addColorStop(0,"rgba(0,0,0,.7)");q.addColorStop(1,"rgba(0,0,0,0)");g.fillStyle=q;g.fillRect(0,0,W,100);
 q=g.createLinearGradient(0,120,0,H);q.addColorStop(0,"rgba(0,0,0,0)");q.addColorStop(.35,"rgba(0,0,0,.72)");q.addColorStop(1,"rgba(0,0,0,.9)");g.fillStyle=q;g.fillRect(0,120,W,200);
 R(g,24,16,4,30,acc);T(g,"ADAM SMASHER",36,38,24,"#000",'left',MICH);T(g,"ADAM SMASHER",34,36,24,"#fff",'left',MICH);T(g,sub,36,52,9,acc,'left',MICH);
 big(g,c.h+":"+c.m,26,80,9,"#000");big(g,c.h+":"+c.m,24,78,9,"#fff");T(g,c.s,24+bigW("00:00",9)+8,78+63,20,acc,'left',RAJ);
 R(g,16,150,448,26,"rgba(0,0,0,.62)");S(g,16,150,448,26,acc,1);tick(g,t,24,170,432,15,"#fff",RAJ);
 T(g,ART,24,198,12,"#c8c8c8",'left',RAJ);T(g,fmt(p*TOT)+" / "+fmt(TOT),456,198,12,"#fff",'right',RAJ);
 R(g,24,206,432,4,"rgba(255,255,255,.2)");R(g,24,206,432*p,4,acc);
 ICONS.forEach((b,i)=>{const x=24+i*110;R(g,x,222,100,34,i==1?acc:"rgba(0,0,0,.6)");S(g,x,222,100,34,acc,2);T(g,b,x+50,245,13,i==1?"#000":"#fff",'center',RAJ)});
 bars(g,t,24,310,52,6,2,34,acc,"#fff")};
const SM1=sm("sm1","#37ffa0","CYBERPUNK  ·  EDGERUNNERS"),SM2=sm("sm2","#ffe600","CYBERPUNK  ·  EDGERUNNERS"),SM3=sm("sm3","#4dffd0","CYBERPUNK  ·  EDGERUNNERS");
'''
i=s.index('const GAMES=[');s=s[:i]+F+s[i:]
G='''["Adam Smasher · fotos suas","Foto de fundo, nome em cima, botões e equalizador por cima",[
 ["S1","Caveira + David","sua imagem do David com a caveira ciber (verde)",SM1],
 ["S2","David amarelo","sua imagem do David de jaqueta amarela",SM2],
 ["S3","Sandevistan","sua imagem do rastro do Sandevistan",SM3]]],
'''
j=s.index('["Death Note"');s=s[:j]+G+s[j:]
open('v5.build.html','w',encoding='utf8').write(s)
open('../docs/temas-jogos-v5.html','w',encoding='utf8').write(s.replace('/*ASSETS*/',open('out/assets3.js',encoding='utf8').read()))
