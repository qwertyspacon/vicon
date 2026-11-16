"""Крупные фото (img_big/, до 1100px) для всех товаров в наличии с ценой. Уже скачанные не трогает."""
import json,re,urllib.request,io,os,sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
os.chdir(os.path.dirname(os.path.abspath(__file__)))
b=json.load(open('balances.json'))
ids=[x['id'] for x in b if float(x['available'])>0]
B={x['id']:x for x in b}
os.makedirs('img_big',exist_ok=True)
def go(i):
    fn=f'img_big/{i}.jpg'
    if os.path.exists(fn): return
    u=B[i]['image']['file'] if B[i].get('image') else None
    if not u: return
    base=re.sub(r'\.\d+x\d+_q\d+_crop\.\w+$','',u)
    try:
        d=urllib.request.urlopen(urllib.request.Request(base,headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read()
        im=Image.open(io.BytesIO(d))
        if im.mode in('RGBA','LA','P'):
            im=im.convert('RGBA'); bg=Image.new('RGB',im.size,'white'); bg.paste(im,mask=im.split()[3]); im=bg
        im=im.convert('RGB'); im.thumbnail((1100,1100)); im.save(fn+'.tmp',format='JPEG',quality=84); os.replace(fn+'.tmp',fn)
    except Exception as e: print('ERR',i,str(e)[:80])
with ThreadPoolExecutor(6) as ex: list(ex.map(go,ids))
print('фото:',sum(os.path.exists(f'img_big/{i}.jpg') for i in ids),'из',len(ids))
