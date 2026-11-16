import json,re,urllib.request,io,os
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
b={x['id']:x for x in json.load(open('balances.json'))}
ids=[i for v in json.load(open('sel_ids.json'))['rows'].values() for i in v]
def go(i):
    fn=f'img2/{i}.jpg'
    if os.path.exists(fn): return
    u=b[i]['image']['file'] if b[i].get('image') else None
    if not u: return
    base=re.sub(r'\.80x80_q85_crop\.\w+$','',u)
    try:
        d=urllib.request.urlopen(urllib.request.Request(base,headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read()
        im=Image.open(io.BytesIO(d)); 
        if im.mode in('RGBA','LA','P'):
            im=im.convert('RGBA'); bg=Image.new('RGB',im.size,'white'); bg.paste(im,mask=im.split()[3]); im=bg
        im=im.convert('RGB'); im.thumbnail((640,640)); im.save(fn,quality=88)
    except Exception as e: print('ERR',i,e)
with ThreadPoolExecutor(6) as ex: list(ex.map(go,ids))
print(len(os.listdir('img2')),'из',len(ids))
