"""Скачивает шрифты Google к себе (fonts/), чтобы сайт не ходил на чужие сервера. Запуск один раз: python3 fonts_local.py"""
import re,urllib.request,hashlib,os
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
URL='https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700;800&family=Unbounded:wght@500;700;800&display=swap'
css=urllib.request.urlopen(urllib.request.Request(URL,headers={'User-Agent':UA})).read().decode()
os.makedirs('fonts',exist_ok=True); out={}
for sub,block in re.findall(r'/\* ([a-z-]+) \*/\s*(@font-face\s*\{[^}]+\})',css):
    if sub not in ('cyrillic','latin','latin-ext'): continue
    fam=re.search(r"font-family: '([^']+)'",block).group(1)
    u=re.search(r'url\((https://[^)]+)\)',block).group(1)
    fn=fam.split()[0].lower()+'-'+sub+'.woff2'
    if not os.path.exists('fonts/'+fn): open('fonts/'+fn,'wb').write(urllib.request.urlopen(u).read())
    b=block.replace(u,'../fonts/'+fn)
    out.setdefault(fam,[]); 
    if b not in out[fam]: out[fam].append(b)
for fam,bl in out.items(): open('fonts/'+fam.split()[0].lower()+'.css','w').write('\n'.join(bl)+'\n')
print({f:len(b) for f,b in out.items()}); print(sorted(os.listdir('fonts')))
