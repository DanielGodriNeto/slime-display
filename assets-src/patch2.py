import re
s=open('v3.build.html',encoding='utf8').read()
def cut(name,nxt):
    a=s.index('function '+name+'(');b=s.index(nxt,a);return a,b
# --- Z2 Fallout
a,b=cut('Z2','function Z3(')
Z2='''function Z2(g,t,c,p){const G="#1aff80",D="#0c8a45",DK="#04170c",M="#3a3b32";
 R(g,0,0,W,H,"#15160f");bevel(g,6,6,468,308,"#6b6c5e","#1c1d16",M);
 for(const[x,y]of[[16,16],[464,16],[16,304],[464,304]]){C(g,x,y,5,"#85866f",1);R(g,x-4,y-1,8,2,"#1c1d16")}
 T(g,"VAULT-TEC  ·  RADIO MODEL 91.5",240,24,8,"#a0a18a",'center',MICH);
 R(g,28,34,424,158,"#0a0b07");R(g,32,38,416,150,DK);
 for(let y=38;y<188;y+=3)R(g,32,y,416,1,"rgba(26,255,128,.07)");
 const tabs=["STAT","INV","DATA","MAP","RADIO"];tabs.forEach((s,i)=>{const x=40+i*66,on=i==4;if(on){R(g,x,42,62,16,G);T(g,s,x+31,55,11,DK,'center')}else{T(g,s,x+31,55,11,D,'center')}});
 R(g,40,62,400,1,D);
 big(g,c.h+":"+c.m+":"+c.s,44,72,5,G);
 tick(g,t,44,134,392,14,G);T(g,ART,44,156,12,D);T(g,fmt(p*TOT)+" / "+fmt(TOT),436,156,12,D,'right');
 for(let i=0;i<50;i++)R(g,44+i*7.9,166,6,8,i<p*50?G:"#0b3a1d");
 for(let i=0;i<4;i++){const x=34+i*88,on=i==1;R(g,x,204,80,38,"#0a0b07");R(g,x+2,206,76,34,on?G:DK);S(g,x+2,206,76,34,G,1);T(g,ICONS[i],x+40,229,13,on?DK:G,'center')}
 const kx=420,ky=224;C(g,kx,ky,26,"#0a0b07",1);C(g,kx,ky,22,"#55564a",1);C(g,kx,ky,16,"#2a2b24",1);
 for(let i=0;i<12;i++){const a=i*Math.PI/6;R(g,kx+Math.cos(a)*24-1,ky+Math.sin(a)*24-1,2,2,"#85866f")}
 const ang=-2+((p*2)%1)*4;g.strokeStyle=G;g.lineWidth=3;g.beginPath();g.moveTo(kx,ky);g.lineTo(kx+Math.cos(ang)*14,ky+Math.sin(ang)*14);g.stroke();
 R(g,28,254,424,50,"#0a0b07");for(let i=0;i<9;i++)R(g,32+i*47,256,43,2,"#15160f");
 for(let i=0;i<24;i++){const h=2+eq(t,i)*34;R(g,36+i*17,298-h,12,h,G)}}
'''
s=s[:a]+Z2+s[b:]
# --- Militech SWAT -> MaxTac x2
a,b=cut('K2','/* ---------- DEATH NOTE')
K2='''const MB="#2a35a8",MR="#ff2a3a";
const imgp=(g,k,x,y,w)=>{const i=IM[k];if(!ok(i))return;g.imageSmoothingEnabled=false;g.drawImage(i,x,y,w,w*i.naturalHeight/i.naturalWidth);g.imageSmoothingEnabled=true};
function K2(g,t,c,p){R(g,0,0,W,H,"#07080c");
 g.save();g.beginPath();g.rect(0,0,W,H);g.clip();g.fillStyle="#10122a";const o=(t/80)%22;for(let x=-H;x<W;x+=22){g.beginPath();g.moveTo(x+o,H);g.lineTo(x+o+8,H);g.lineTo(x+o+8+H,0);g.lineTo(x+o+H,0);g.fill()}g.restore();
 R(g,0,0,W,6,MB);R(g,0,H-6,W,6,MB);
 img(g,"maxword",20,16,150);T(g,"NCPD  ·  MAXIMUM TACTICAL",20,64,9,"#8a90c8",'left',MICH);
 tint(g,"maxskull",MR,368,70,96);
 big(g,c.h+":"+c.m,24,76,10,"#fff");T(g,c.s,24+bigW("00:00",10)+10,76+70,22,"#6f7cff",'left',RAJ);
 R(g,24,166,340,30,"#0b0d1c");S(g,24,166,340,30,MB,2);tick(g,t,32,187,324,15,"#fff",RAJ);
 T(g,ART,24,214,12,"#8a90c8",'left',RAJ);T(g,fmt(p*TOT)+" / "+fmt(TOT),364,214,12,"#fff",'right',RAJ);
 R(g,24,220,340,5,"#14173a");R(g,24,220,340*p,5,MB);
 ICONS.forEach((b,i)=>{const x=24+i*88;R(g,x,238,80,34,i==1?MB:"#0b0d1c");S(g,x,238,80,34,i==1?"#6f7cff":MB,2);T(g,b,x+40,260,13,"#fff",'center',RAJ)});
 bars(g,t,24,308,40,6,3,28,MB,MR)}
function K3(g,t,c,p){R(g,0,0,W,H,MB);R(g,0,0,W,8,"#fff");R(g,0,H-8,W,8,"#fff");R(g,0,12,W,3,"#0b0d3a");R(g,0,H-15,W,3,"#0b0d3a");
 img(g,"maxword",150,22,180);
 big(g,c.h+":"+c.m,30,90,10,"#fff");T(g,c.s,30+bigW("00:00",10)+10,90+70,22,"#c8ceff",'left',RAJ);
 R(g,30,176,420,28,"#0b0d3a");tick(g,t,38,196,404,15,"#fff",RAJ);
 T(g,ART,30,224,12,"#c8ceff",'left',RAJ);T(g,fmt(p*TOT)+" / "+fmt(TOT),450,224,12,"#fff",'right',RAJ);
 R(g,30,230,420,5,"#0b0d3a");R(g,30,230,420*p,5,"#fff");
 ICONS.forEach((b,i)=>{const x=30+i*108;R(g,x,246,96,30,i==1?"#fff":"#0b0d3a");T(g,b,x+48,267,13,i==1?MB:"#fff",'center',RAJ)});
 bars(g,t,30,306,40,6,4,22,"#fff","#c8ceff")}

'''
s=s[:a]+K2+s[b:]
# --- N5 Kira + maçã
N5='''function N5(g,t,c,p){R(g,0,0,W,H,"#0c0706");const rd="#c0261f",cr="#efe3cf";R(g,0,0,W,8,rd);R(g,0,H-8,W,8,rd);
 const by=Math.sin(t/500)*3;imgp(g,"mc_apple",356,50+by,104);
 T(g,"KIRA",28,50,26,cr,'left',GARA);R(g,28,56,150,1,rd);
 big(g,c.h+":"+c.m,28,70,10,cr);T(g,c.s,28+bigW("00:00",10)+8,70+70,22,rd,'left',GARA);
 tick(g,t,28,184,424,16,cr,GARA);T(g,ART,28,202,12,"#9a8a78",'left',GARA);T(g,fmt(p*TOT)+" / "+fmt(TOT),452,202,12,"#9a8a78",'right',GARA);
 R(g,28,212,424,3,"#2a1612");R(g,28,212,424*p,3,rd);imgp(g,"mc_apple",20+424*p,200,16);
 ICONS.forEach((b,i)=>{S(g,28+i*106,230,98,32,i==1?rd:"#6a5648",2);T(g,b,77+i*106,251,13,i==1?rd:cr,'center')});
 bars(g,t,28,304,44,6,4,22,"#9a8a78",rd)}

'''
s=s.replace('/* ---------- MINECRAFT',N5+'/* ---------- MINECRAFT',1)
# --- Minecraft mundo
MCW='''const tx=(g,k,x,y)=>{const i=IM[k];if(ok(i))g.drawImage(i,x,y,16,16)};
const nine=(g,k,x,y,w,h,b)=>{const i=IM[k];if(!ok(i))return;g.imageSmoothingEnabled=false;const n=i.naturalWidth,m=i.naturalHeight,bs=b*2;
 g.drawImage(i,0,0,b,m,x,y,bs,h);g.drawImage(i,n-b,0,b,m,x+w-bs,y,bs,h);g.drawImage(i,b,0,n-2*b,m,x+bs,y,w-2*bs,h);g.imageSmoothingEnabled=true};
function MW(g,t,c,p){const gr=g.createLinearGradient(0,0,0,128);gr.addColorStop(0,"#6fa6ff");gr.addColorStop(1,"#bcd8ff");g.fillStyle=gr;g.fillRect(0,0,W,128);
 for(let i=0;i<4;i++){const x=((i*140+t/90)%620)-70,y=14+(i*22)%60;R(g,x,y,64,12,"#fff");R(g,x+10,y-8,40,10,"#fff")}
 R(g,440,8,24,24,"#ffe45a");
 // montanha de pedra em degraus (direita)
 for(let r=0;r<5;r++)for(let x=288+r*16;x<W-r*16;x+=16)tx(g,"mc_stone",x,112-r*16);
 // casa: paredes, janelas, porta, telhado de tijolo
 for(let r=0;r<3;r++)for(let k=0;k<5;k++)tx(g,"mc_planks",330+k*16,64+r*16);
 for(const x of[330,394])for(let r=0;r<3;r++)tx(g,"mc_log",x,64+r*16);
 tx(g,"mc_glass",346,64);tx(g,"mc_glass",378,64);tx(g,"mc_door_t",362,80);tx(g,"mc_door_b",362,96);tx(g,"mc_glass",346,96);tx(g,"mc_glass",378,96);
 for(let k=-1;k<6;k++)tx(g,"mc_bricks",330+k*16,48);for(let k=0;k<4;k++)tx(g,"mc_bricks",346+k*16-16+16-16+16,32);
 tx(g,"mc_torch",312,96);
 // árvore
 for(let r=0;r<3;r++)tx(g,"mc_log",428,64+r*16);
 for(let r=0;r<2;r++)for(let k=0;k<3;k++)tx(g,"mc_leaves",412+k*16,32+r*16);tx(g,"mc_leaves",428,16);
 // grama + subsolo
 for(let x=0;x<W;x+=16)tx(g,"mc_grass_side",x,112);
 for(let y=128;y<H;y+=16)for(let x=0;x<W;x+=16){const v=rnd(x*5+y*3);let k=y<160?"mc_dirt":"mc_stone";if(y>=160){if(v>.97)k="mc_diamond";else if(v>.93)k="mc_gold";else if(v>.87)k="mc_iron";else if(v>.78)k="mc_coal"}tx(g,k,x,y)}
 // relógio no céu
 g.save();g.globalAlpha=.35;big(g,c.h+":"+c.m,26,22,8,"#000");g.restore();big(g,c.h+":"+c.m,24,20,8,"#fff");
 T(g,":"+c.s,24+bigW("00:00",8)+8,20+56,20,"#fcfc54",'left',PIX);
 // painel subterrâneo
 g.fillStyle="rgba(0,0,0,.6)";g.fillRect(10,136,460,176);S(g,10,136,460,176,"#000",2);
 tick(g,t,20,160,440,15,"#fff",PIX);T(g,ART,20,180,12,"#ccc",'left',PIX);T(g,fmt(p*TOT)+" / "+fmt(TOT),460,180,12,"#ccc",'right',PIX);
 R(g,20,190,440,8,"#222");R(g,20,190,440*p,8,"#7ee04a");R(g,20,190,440*p,2,"#b8ff94");
 ICONS.forEach((b,i)=>{const x=20+i*112;nine(g,i==1?"mc_btn_h":"mc_btn",x,208,104,30,3);T(g,b,x+52,229,13,i==1?"#ffffa0":"#fff",'center',PIX)});
 bars(g,t,20,304,56,6,2,50,"#55aa33","#fcfc54")}

'''
s=s.replace('function M4(',MCW+'function M4(',1)
# --- lista GAMES
a=s.index('const GAMES=[');b=s.index('];',s.index('Mo2]',a))
games='''const GAMES=[
["Project Zomboid · rádio ValuTech","Preto liso, cinza #2a2a2a nos cabeçalhos, vermelho #b3282d nos botões",[
 ["Z1","Rádio ValuTech (fiel)","cabeçalhos cinza, células de sinal como equalizador, barra de bateria",Z1],
 ["Z2","Rádio Pip-Boy (Fallout)","visor verde fósforo, abas STAT/INV/DATA/MAP/RADIO, moldura com rebites, plaqueta Vault-Tec, botão de sintonia",Z2]]],
["Cyberpunk Edgerunners · Arasaka","Vermelho #c0261f, preto, branco",[
 ["A1","Arasaka terminal","logo real, vermelho no preto",A1],
 ["A2","Arasaka vermelho","fundo vermelho cheio",A2]]],
["Cyberpunk Edgerunners · Militech / MaxTac","Militech amarelo #f5d90a; MaxTac azul #2a35a8, branco, vermelho do olho ciber",[
 ["K1","Militech corporativo","amarelo e preto com listras de perigo",K1],
 ["K2","MaxTac (HUD)","wordmark real, caveira ciber com olho vermelho, listras azuis animadas",K2],
 ["K3","MaxTac (cartão azul)","campo azul com wordmark branco, como o logo",K3]]],
["Death Note","Preto, prata, vermelho #c0261f, creme",[
 ["N1","Capa do caderno","prata gótica, cantoneiras",N1],
 ["N3","L","L real gigante",N3],
 ["N4","Light / Kira","vermelho e creme, kanji",N4],
 ["N5","Kira + maçã","maçã de pixel (textura real do Minecraft) flutuando; maçã como marcador do progresso",N5]]],
["Minecraft · mundo","Texturas reais do jogo (jar 26.1.2): grama, terra, pedra, minérios, tábuas",[
 ["M1","Mundo","relógio no céu, casa e montanha, painel de info no subsolo",MW],
 ["M2","Menu inicial","título com 'Now playing!'",M4]]]
'''
s=s[:a]+games+s[b:]
s=s.replace('Temas v3','Temas v4').replace('agora com imagens reais','você escolheu, eu refiz')
s=re.sub(r'<p class="s">.*?</p>','<p class="s">Z2 em Fallout, MaxTac novo, Kira com maçã e Minecraft como mundo (texturas reais do jogo). Nada desenhado por mim: imagens baixadas e recortadas.</p>',s,count=1,flags=re.S)
open('v4.build.html','w',encoding='utf8').write(s)
open('../docs/temas-jogos-v4.html','w',encoding='utf8').write(s.replace('/*ASSETS*/',open('out/assets2.js',encoding='utf8').read()))
print('ok')
