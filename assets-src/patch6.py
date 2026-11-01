s=open('v5.build.html',encoding='utf8').read()
o="T(g,k,448,34+i*24,20,rd,'center',JP)"
assert o in s
s=s.replace(o,"T(g,k,447,50+i*37,34,rd,'center',JP)")
open('v5.build.html','w',encoding='utf8').write(s)
open('../docs/temas-jogos-v5.html','w',encoding='utf8').write(s.replace('/*ASSETS*/',open('out/assets3.js',encoding='utf8').read()))
