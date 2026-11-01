import re
s=open('v3.src.html',encoding='utf8').read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(a[:50],s.count(a));s=s.replace(a,b)
# loader
rep("const ICONS=['◀◀','▶','▶▶','VOL'];","""const ICONS=['◀◀','▶','▶▶','VOL'];
/*ASSETS*/
const IM={};for(const[k,v]of Object.entries(IMG)){const i=new Image();i.src=v;IM[k]=i}
const ok=i=>i.complete&&i.naturalWidth;
const img=(g,k,x,y,w)=>{const i=IM[k];if(ok(i))g.drawImage(i,x,y,w,w*i.naturalHeight/i.naturalWidth)};
const TC={};const tint=(g,k,col,x,y,w)=>{const i=IM[k];if(!ok(i))return;const key=k+col;if(!TC[key]){const c=document.createElement('canvas');c.width=i.naturalWidth;c.height=i.naturalHeight;const q=c.getContext('2d');q.drawImage(i,0,0);q.globalCompositeOperation='source-in';q.fillStyle=col;q.fillRect(0,0,c.width,c.height);TC[key]=c}const c=TC[key];g.drawImage(c,x,y,w,w*c.height/c.width)};""")
# remove vector placeholders
s=re.sub(r"const eye=\(g,x,y,s,gl\)=>\{.*?\};\n","",s,count=1,flags=re.S)
s=re.sub(r"const mon=\(g,x,y,r,col,bg\)=>\{.*?\};\n","",s,count=1,flags=re.S)
s=re.sub(r"const mtLogo=\(g,x,y,s,col\)=>\{.*?\};\n","",s,count=1,flags=re.S)
rep('eye(g,240,52,30,gl);','img(g,"eye_cyan",206,6,68);')
rep('eye(g,424,44,16,"#ff9a2e");','img(g,"eye_orange",396,26,56);')
s=re.sub(r"for\(let i=0;i<5;i\+\+\)\{const x=318\+i\*28;C\(g,x\+10,92,11,i<3\?gl:\"#0b4a5e\",0,2\)\}T\(g,\"RUNAS\",318,128,10,gl,'left',EXO\);",'img(g,"eye_cyan",350,64,90);',s,count=1)
assert 'eye_cyan",350' in s
rep('mon(g,440,40,22,rd);','img(g,"ara",418,14,46);')
rep('mon(g,400,100,70,"#f2f2f2");','tint(g,"ara","#f2f2f2",428,6,44);')
rep('mtLogo(g,24,28,44,yl);T(g,"MILITECH",80,56,22,yl,\'left\',STEN);T(g,"INTERNATIONAL ARMAMENTS",80,70,8,"#8a8a6a",\'left\',MICH);','img(g,"mil",24,20,64);T(g,"INTERNATIONAL ARMAMENTS",100,52,10,"#8a8a6a",\'left\',MICH);')
rep('T(g,"OPERADOR · SWAT-07",34,40,11,ol,\'left\',RAJ);mtLogo(g,420,26,32,yl);','T(g,"TACTICAL RESPONSE UNIT  ·  CODE 3",34,40,12,ol,\'left\',RAJ);T(g,"ARMED RESPONSE",34,52,9,"#8a8a6a",\'left\',MICH);img(g,"mil",396,18,62);')
rep('T(g,"L",410,250,260,"#d9d9d9",\'center\',FRAK);','img(g,"L",322,40,140);')
# Halo 3 helmet
a=s.index('function H3(');b=s.index('/* ---------- ARASAKA')
s=s[:a]+'''function H3(g,t,c,p){R(g,0,0,W,H,"#05080a");g.imageSmoothingEnabled=false;img(g,"helmet",290,0,190);
 let lg=g.createLinearGradient(290,0,380,0);lg.addColorStop(0,"#05080a");lg.addColorStop(1,"rgba(5,8,10,0)");g.fillStyle=lg;g.fillRect(290,0,100,190);
 lg=g.createLinearGradient(0,130,0,190);lg.addColorStop(0,"rgba(5,8,10,0)");lg.addColorStop(1,"#05080a");g.fillStyle=lg;g.fillRect(290,130,190,60);
 for(let i=0;i<10;i++)R(g,24+i*20,16,16,8,i<8+(Math.sin(t/900)>.8?-1:0)?"#bfe9ff":"#27465a");
 big(g,c.h+":"+c.m,24,36,9,"#d8f0ff");T(g,c.s,24+bigW("00:00",9)+8,36+63,22,"#f0a020",'left',RAJ);
 hbox(g,24,126,250,26);T(g,fmt(p*TOT)+" / "+fmt(TOT),32,145,14,"#e6f6ff",'left',RAJ);T(g,ART,266,145,12,"#9fd8ff",'right',RAJ);
 hbox(g,24,198,432,32);tick(g,t,34,220,412,16,"#fff",RAJ);
 R(g,24,238,432,4,"#27465a");R(g,24,238,432*p,4,"#f0a020");
 ICONS.forEach((b,i)=>{hbox(g,24+i*110,252,100,30);T(g,b,74+i*110,273,13,i==1?"#f0a020":"#bfe9ff",'center',RAJ)});
 bars(g,t,300,172,16,6,3,34,"#7fc4ef","#f0a020")}

'''+s[b:]
# Minecraft: restaurar M1/M2 originais da v1, tirar forno e HUD
v1=open('../docs/temas-jogos.html',encoding='utf8').read()
def fn(name,nxt):
    a=v1.index('function '+name+'(');b=v1.index(nxt,a);return v1[a:b]
m1=fn('M1','function M2(').replace('function M1(','function Mo1(')
m2=fn('M2','function M3(').replace('function M2(','function Mo2(')
a=s.index('function M2(');b=s.index('function M4(')
s=s[:a]+m1+m2+s[b:]
rep('''["M1","Inventário","a que você curtiu, com hotbar de slots no rodapé",M1],
 ["M2","Forno","a seta do forno enche como barra de progresso",M2],
 ["M3","HUD do jogo","corações, barra de XP e hotbar com slot selecionado",M3],
 ["M4","Menu inicial","título com 'Now playing!' amarelo pulsando",M4]''','''["M1","Inventário (original)","a primeira versão que você curtiu",Mo1],
 ["M2","Hotbar no mundo (original)","céu, grama e botões como slots",Mo2],
 ["M3","Inventário v2","com fonte pixel e slots no rodapé",M1],
 ["M4","Menu inicial","título com 'Now playing!' amarelo pulsando",M4]''')
rep('["H3","Menu do Halo 3","faixa de seleção azul translúcida, fonte larga",H3]','["H3","Capacete + visor","capacete real do Halo 3 em pixel, visor dourado, HUD azul",H3]')
rep('["K2","Militech SWAT","verde-oliva, colchetes táticos, mira, operador",K2]','["K2","Militech SWAT","Tactical Response Unit: verde-oliva, colchetes táticos, mira, logo real",K2]')
rep('<title>Slime Display - Temas v2</title>','<title>Slime Display - Temas v3</title>')
rep('<h1>Temas v2: refeitos a partir de referências reais</h1>','<h1>Temas v3: agora com imagens reais</h1>')
s=re.sub(r'<p class="s">.*?</p>','<p class="s">Logos, olho Sheikah, L e capacete são imagens reais baixadas e recortadas (fundo removido por luminância). O capacete foi reduzido para pixel art por ferramenta. Nada desenhado por mim.</p>',s,count=1,flags=re.S)
open('v3.build.html','w',encoding='utf8').write(s)
assets=open('out/assets.js',encoding='utf8').read()
open('../docs/temas-jogos-v3.html','w',encoding='utf8').write(s.replace('/*ASSETS*/',assets))
print('ok')
