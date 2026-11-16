"""Собирает описания из ~/workspace/projects/vicon-info/desc*.json в info/info.json,
качает фото из media в info/img/<id>_<n>.jpg (900px). Запуск: python3 info/merge.py"""
import json,glob,os,io,sys,urllib.request
from PIL import Image
H=os.path.dirname(os.path.abspath(__file__)); SRC=os.path.expanduser('~/workspace/projects/vicon-info')
OUTF=f'{H}/info.json'; I=json.load(open(OUTF)) if os.path.exists(OUTF) else {}
new={}
for f in sorted(glob.glob(f'{SRC}/desc*.json')): new.update(json.load(open(f)))
ok=bad=0
for i,v in new.items():
    med=[];n=0
    for m in v.get('media',[]):
        if m.get('type')=='video' and m.get('url','').startswith('https://'): med.append({'type':'video','url':m['url']}); continue
        if m.get('type')!='photo': continue
        n+=1; fn=f'img/{i}_{n}.jpg'; dst=f'{H}/{fn}'
        if not os.path.exists(dst):
            try:
                r=urllib.request.urlopen(urllib.request.Request(m['url'],headers={'User-Agent':'Mozilla/5.0'}),timeout=20).read()
                im=Image.open(io.BytesIO(r)).convert('RGB')
                if min(im.size)<200: raise ValueError('мелкое')
                im.thumbnail((900,900)); im.save(dst,format='JPEG',quality=78,optimize=True,progressive=True); ok+=1
            except Exception as e: bad+=1; print('фото не скачалось',i,m['url'][:80],e,file=sys.stderr); n-=1; continue
        med.append({'type':'photo','src':fn,'from':m['url']})
    I[i]={'ru':v['ru'],'uz':v['uz'],'media':med}
json.dump(I,open(OUTF,'w'),ensure_ascii=False,indent=0)
print(f'описаний {len(I)}, фото скачано {ok}, не скачалось {bad}, видео {sum(1 for v in I.values() for m in v["media"] if m["type"]=="video")}')
