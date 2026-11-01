s=open('v5.build.html',encoding='utf8').read()
# N4: quatro kanji, menores
s=s.replace('T(g,"神",440,52,30,rd,\'center\',JP);','for(const[i,k]of[..."新世界神"].entries())T(g,k,448,34+i*24,20,rd,\'center\',JP);',1)
# N1 original (preto/branco, só segundos vermelhos) + N1b vermelho
a=s.index('function N1(');b=s.index('function N2(');red=s[a:b]
bw='''function N1(g,t,c,p){R(g,0,0,W,H,"#060606");for(let x=0;x<W;x+=3)R(g,x,0,1,H,"#0a0a0a");const sv="#cfcfcf";S(g,14,14,452,292,"#5a5a5a",1);for(const[x,y,a,b]of[[20,20,1,1],[460,20,-1,1],[20,300,1,-1],[460,300,-1,-1]])corner(g,x,y,a,b,sv);
 T(g,"DEATH NOTE",240,52,26,sv,'center',GARA);T(g,"How to use it",240,68,11,"#7a7a7a",'center',GARA);
 big(g,c.h+":"+c.m,86,84,10,sv);T(g,c.s,86+bigW("00:00",10)+10,84+70,20,"#b3202a",'left',GARA);
 tick(g,t,40,184,400,15,"#d8d8d8",GARA);T(g,ART,40,202,12,"#8a8a8a",'left',GARA);T(g,fmt(p*TOT)+" / "+fmt(TOT),440,202,12,"#8a8a8a",'right',GARA);
 R(g,40,210,400,1,"#555");R(g,40,209,400*p,3,sv);
 ICONS.forEach((b,i)=>{S(g,40+i*104,226,94,30,"#8a8a8a",1);T(g,b,87+i*104,246,13,sv,'center')});
 bars(g,t,40,296,44,6,3,20,"#8a8a8a",sv)}
'''
s=s[:a]+bw+red.replace('function N1(','function N1b(',1)+s[b:]
i=s.index('["N1"');print(s[i:i+120])
open('v5.build.html','w',encoding='utf8').write(s)
s=s.replace('["N1","Capa do caderno","prata gótica, cantoneiras",N1],','["N1","Capa do caderno","prata gótica, só os segundos em vermelho",N1],\n ["N1b","Capa do caderno vermelha","mesma capa, com detalhes em vermelho",N1b],',1)
open('v5.build.html','w',encoding='utf8').write(s)
open('../docs/temas-jogos-v5.html','w',encoding='utf8').write(s.replace('/*ASSETS*/',open('out/assets3.js',encoding='utf8').read()))
