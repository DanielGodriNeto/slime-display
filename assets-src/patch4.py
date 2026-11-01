s=open('v5.build.html',encoding='utf8').read()
def cut(s,a,b):
    i=s.index(a);j=s.index(b,i);return s[:i]+s[j:]
s=cut(s,'function N5(','/* ---------- MINECRA')
i=s.index('["N5"');j=s.index('N5]',i)+3;s=s[:i].rstrip().rstrip(',')+s[j:]
a=s.index('function N4(');b=s.index('function N5(') if 'function N5(' in s else s.index('/* ---------- MINECRA') if '/* ---------- MINECRA' in s else len(s)
n=s[a:]
k=n.index('g.save();g.translate(450,24)');e=n.index('g.restore();',k)+len('g.restore();')
n=n[:k]+'T(g,"神",440,52,30,rd,\'center\',JP);'+n[e:]
n=n.replace('tick(g,t,28,184,380,16,cr,GARA)','tick(g,t,28,184,424,16,cr,GARA)',1)
n=n.replace('fmt(TOT),408,202,','fmt(TOT),452,202,',1)
n=n.replace('R(g,28,210,380,3,"#2a1612");R(g,28,210,380*p,3,rd);','R(g,28,210,424,3,"#2a1612");R(g,28,210,424*p,3,rd);',1)
n=n.replace('S(g,28+i*96,228,88,32,','S(g,28+i*106,228,98,32,',1).replace('T(g,b,72+i*96,249,','T(g,b,77+i*106,249,',1)
s=s[:a]+n
a=s.index('function N1(');b=s.index('function N2(');n=s[a:b]
rd='"#b3202a"'
n=n.replace('corner(g,x,y,a,b,sv)','corner(g,x,y,a,b,%s)'%rd)
n=n.replace('"#7a7a7a",\'center\',GARA);','"#7a7a7a",\'center\',GARA);R(g,150,74,180,1,%s);'%rd,1)
n=n.replace('R(g,40,209,400*p,3,sv)','R(g,40,209,400*p,3,%s)'%rd)
n=n.replace('S(g,40+i*104,226,94,30,"#8a8a8a",1);T(g,b,87+i*104,246,13,sv,','S(g,40+i*104,226,94,30,i==1?%s:"#8a8a8a",i==1?2:1);T(g,b,87+i*104,246,13,i==1?%s:sv,'%(rd,rd))
n=n.replace('"#8a8a8a",sv)}','"#8a8a8a",%s)}'%rd)
s=s[:a]+n+s[b:]
open('v5.build.html','w',encoding='utf8').write(s)
open('../docs/temas-jogos-v5.html','w',encoding='utf8').write(s.replace('/*ASSETS*/',open('out/assets3.js',encoding='utf8').read()))
print('ok','N5' in s)
