import re
s=open('v4.build.html',encoding='utf8').read()
a=s.index('function K2(');b=s.index('/* ---------- DEATH NOTE')
K='''const mtGrid=(g,col)=>{g.fillStyle=col;for(let x=0;x<W;x+=24)g.fillRect(x,0,1,H);for(let y=0;y<H;y+=24)g.fillRect(0,y,W,1)};
const brk=(g,x,y,sx,sy,col,l)=>{g.strokeStyle=col;g.lineWidth=3;g.beginPath();g.moveTo(x,y+sy*l);g.lineTo(x,y);g.lineTo(x+sx*l,y);g.stroke()};
function K2(g,t,c,p){R(g,0,0,W,H,"#07080c");mtGrid(g,"rgba(42,53,168,.14)");
 g.globalAlpha=.07;g.save();g.translate(330,300);g.rotate(-.5);img(g,"mt_word",-60,-20,360);g.restore();g.globalAlpha=1;
 R(g,0,0,W,6,MB);R(g,0,H-6,W,6,MB);R(g,0,6,W,2,"#0b0d3a");
 for(const[x,y,sx,sy]of[[12,16,1,1],[468,16,-1,1],[12,304,1,-1],[468,304,-1,-1]])brk(g,x,y,sx,sy,"#8fa0ff",22);
 img(g,"mt_word",26,24,150);T(g,"NCPD  ·  MAXIMUM TACTICAL",26,66,9,"#8a90c8",'left',MICH);
 R(g,350,24,1,200,MB);img(g,"mt_badge",368,24,100);
 T(g,"NCPD",418,176,10,"#8a90c8",'center',MICH);T(g,"CODE: PSYCHO",418,192,9,"#8fa0ff",'center',MICH);
 big(g,c.h+":"+c.m,26,82,9,"#fff");T(g,c.s,26+bigW("00:00",9)+8,82+63,22,"#8fa0ff",'left',RAJ);
 R(g,26,166,300,30,"#0b0d1c");S(g,26,166,300,30,MB,2);tick(g,t,34,187,284,15,"#fff",RAJ);
 T(g,ART,26,214,12,"#8a90c8",'left',RAJ);T(g,fmt(p*TOT)+" / "+fmt(TOT),326,214,12,"#fff",'right',RAJ);
 for(let i=0;i<30;i++)R(g,26+i*10,222,8,6,i<p*30?"#8fa0ff":"#14173a");
 ICONS.forEach((b,i)=>{const x=26+i*114;R(g,x,238,104,34,i==1?MB:"#0b0d1c");S(g,x,238,104,34,i==1?"#8fa0ff":MB,2);T(g,b,x+52,260,13,"#fff",'center',RAJ)});
 bars(g,t,26,310,52,6,2,30,MB,"#8fa0ff")}
function K3(g,t,c,p){R(g,0,0,W,H,MB);mtGrid(g,"rgba(143,160,255,.18)");g.fillStyle="#1f2890";g.beginPath();g.moveTo(300,0);g.lineTo(W,0);g.lineTo(W,266);g.lineTo(240,266);g.closePath();g.fill();R(g,0,0,W,6,"#fff");R(g,0,10,W,2,"#0b0d3a");
 for(const[x,y,sx,sy]of[[10,18,1,1],[470,18,-1,1]])brk(g,x,y,sx,sy,"#c8ceff",16);R(g,368,16,1,100,"#8fa0ff");
 img(g,"mt_word",24,22,190);img(g,"mt_badge86",378,16,86);
 big(g,c.h+":"+c.m,24,68,10,"#fff");T(g,c.s,24+bigW("00:00",10)+10,68+70,22,"#c8ceff",'left',RAJ);
 R(g,24,150,340,28,"#0b0d3a");tick(g,t,32,170,324,15,"#fff",RAJ);
 T(g,ART,24,198,12,"#c8ceff",'left',RAJ);T(g,fmt(p*TOT)+" / "+fmt(TOT),364,198,12,"#fff",'right',RAJ);
 R(g,24,206,340,5,"#0b0d3a");R(g,24,206,340*p,5,"#fff");
 ICONS.forEach((b,i)=>{const x=24+i*114;R(g,x,222,104,30,i==1?"#fff":"#0b0d3a");T(g,b,x+52,243,13,i==1?MB:"#fff",'center',RAJ)});
 const yl="#fcee09";R(g,0,266,W,54,yl);R(g,0,266,W,3,"#0b0b0c");
 T(g,"LOGO-TYPE →",20,284,9,"#0b0b0c",'left',MICH);T(g,"MAX-TAC",20,308,20,"#0b0b0c",'left',RAJ);
 bars(g,t,200,314,32,6,3,40,"#0b0b0c","#0b0b0c")}

'''
s=s[:a]+K+s[b:]
s=s.replace('tint(g,"ara","#f2f2f2",428,6,44);R(g,24,22,432,1,bk)','tint(g,"ara","#f2f2f2",206,22,36);R(g,24,22,432,1,bk)')
s=s.replace('imgp(g,"mc_apple",356,50+by,104)','img(g,"mc_apple",366,40+by,98)').replace('imgp(g,"mc_apple",20+424*p,200,16)','img(g,"mc_apple16",20+424*p,196,16)')
s=s.replace('hazard(g,0,14,yl,"#0b0b0c",t/60);hazard(g,H-14,14,yl,"#0b0b0c",-t/60);','hazard(g,0,14,yl,"#0b0b0c",0);hazard(g,H-14,14,yl,"#0b0b0c",0);')
s=s.replace('wordmark real, caveira ciber com olho vermelho, listras azuis animadas','só os dois logos que você mandou (wordmark + caveira com capacete), grade, colchetes, marca d\'água, olho vermelho com mira')
s=s.replace('campo azul com wordmark branco, como o logo','cartão azul + faixa amarela estilo Cyberpunk, como a sua imagem do logo')

s=s.replace('Temas v4','Temas v5').replace('você escolheu, eu refiz','versão final dos escolhidos')
s=re.sub(r'<p class="s">.*?</p>','<p class="s">Militech sem barras animadas. MaxTac refeito só com os logos que você enviou.</p>',s,count=1,flags=re.S)
# tirar Minecraft
a=s.index('["Minecraft · mundo"');b=s.index('];',a)
s=s[:a].rstrip().rstrip(',')+'\n'+s[b:]
open('v5.build.html','w',encoding='utf8').write(s)
open('../docs/temas-jogos-v5.html','w',encoding='utf8').write(s.replace('/*ASSETS*/',open('out/assets3.js',encoding='utf8').read()))
print('ok')
