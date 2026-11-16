"""Три сайта-каталога Vicon из свежих balances.json / prices.json / my_order_items.json:
   apteka/ (товары для аптек), detskoe/ (игрушки и детские товары), vse/ (все товары в наличии).
Общие картинки: img/ (крупные) и th/ (маленькие) в корне. Каждый сайт — index.html + data.js.
Запуск: python3 build_sites.py   (папка: SITES_OUT или ~/workspace/sites/linko)
"""
import json,os,re,io,shutil,time,datetime,contextlib,collections
from PIL import Image
os.chdir(os.path.dirname(os.path.abspath(__file__)))
with contextlib.redirect_stdout(io.StringIO()):
    import build2 as B
    AP_SECTIONS=list(B.sections); AP_KIND=B.kind
    import toys as T
OUT=os.environ.get('SITES_OUT') or os.path.expanduser('~/workspace/sites/linko')
TG='shara_ooo_001'
b=B.b; cur=B.cur; pop=B.pop
avail=[i for i,x in b.items() if float(x['available'])>0 and i in cur]
def ty(i): return b[i]['type']['name']
def has(i,p): return re.search(p,b[i]['title'],re.I)
def key(i): return (-len(pop[i]),-float(b[i]['available']))
def kind(i): return T.KIND.get(i) or AP_KIND(i) or KIND_ALL.get(ty(i),'')

# ---------- аптека: разделы PDF-каталога ----------
AP=[(t,s,ids) for t,s,ids,_ in AP_SECTIONS]
AP_ICON=['🦷','🍼','🪥','🦷','🪥','🧵','🧻','🧴','✂️','🧤','🦟','🌸','🧽','🔋']
# ---------- детское ----------
TOY_ICON={'Водные пистолеты и автоматы':'🔫','Мыльные пузыри':'🫧','Мячи':'⚽','Ночники':'🌙','Куклы и фигурки':'🪆','Машинки, самолёты, дроны':'🚗',
 'Сюжетные наборы':'👮','Музыкальные игрушки':'🎸','Для малышей':'🧸','Развивающие и антистресс':'🧩','Водные игры':'💧','Для бассейна и пляжа':'🏊',
 'Сюрпризы в пакетиках':'🎁','Мини-вентиляторы':'🌀','Для праздника':'🎉'}
baby=[i for i in avail if ty(i)=='Chaqaloqlar']
teeth=[i for i in baby if has(i,'^Calsi')]
kids_care=[i for i in avail if (ty(i) in("Tish Sho'tkalar",'Zubnaya Pastalar') and has(i,'detsk|detisk|kids|panja|Detskiy'))
           or (ty(i) in('Shampun  Xitoy','Hayat Shampun') and has(i,'baby|kids|detsk'))]
toy_used=set(i for _,_,ids,_ in T.B.sections for i in ids)
toy_rest=[i for i in avail if ty(i)=="O'yinchoqlar" and i not in toy_used and not has(i,T.SKIP)]
DET=[('Прорезыватели для зубов','Силиконовые прорезыватели Calsi',sorted(teeth,key=key),'🦷'),
     ('Соски, бутылочки, для малышей','Соски, бутылочки, поильники, молокоотсосы',sorted([i for i in baby if i not in teeth],key=key),'🍼'),
     ('Детские щётки, пасты, шампуни','Уход для детей',sorted(kids_care,key=key),'🪥')]
REN={'Для малышей':('Погремушки и игрушки для ванной','Для самых маленьких')}
DET+=[(*REN.get(t,(t,s)),ids,TOY_ICON.get(t,'🧸')) for t,s,ids,_ in T.B.sections]
if toy_rest: DET.append(('Другие игрушки','Всё остальное из игрушек',sorted(toy_rest,key=key),'🎈'))
# сначала яркие игрушки, товары для малышей — в конце (чтобы не начиналось как аптека)
_ORD=['Машинки, самолёты, дроны','Куклы и фигурки','Ночники','Водные пистолеты и автоматы','Сюжетные наборы','Мячи','Развивающие и антистресс',
 'Музыкальные игрушки','Мыльные пузыри','Для праздника','Сюрпризы в пакетиках','Водные игры','Для бассейна и пляжа','Мини-вентиляторы',
 'Погремушки и игрушки для ванной','Другие игрушки','Соски, бутылочки, для малышей','Прорезыватели для зубов','Детские щётки, пасты, шампуни']
DET.sort(key=lambda x:_ORD.index(x[0]) if x[0] in _ORD else 15.5)
# ---------- все товары: по видам из Linko ----------
G=[ # (раздел, подпись, иконка, типы Linko) — порядок = порядок на сайте
 ('Телефонные аксессуары','Наушники, кабели, зарядки','🎧',['Aksesuar']),
 ('Игрушки','Все игрушки склада','🧸',["O'yinchoqlar"]),
 ('Хозяйственные товары','Вешалки, прищепки и другое','🏠',["Xo'jalik Mollari"]),
 ('Чистящие средства','Для туалета и уборки','🧹',['Tozalash Maxsulotlari']),
 ('Уход за зубами','Щётки, пасты, зубочистки, флосс','🦷',["Tish Sho'tkalar",'Zubnaya Pastalar','Zuba Chistkalar',"Sprey va Sho'tka idishlar"]),
 ('Шампуни, гели, мыло','Для всей семьи','🧴',['Shampun  Xitoy','Hayat Shampun']),
 ('Ватные палочки, диски, салфетки','Ежедневная гигиена','🧻',['Uxa Chistkalar','Vatnie Diski','Salfetkalar']),
 ('Мочалки и для ванной','Мочалки, губки для тела','🛁',['Gigiena Banni Machalkalar']),
 ('Мыльницы','Мыльницы и подставки','🧼',['Sovun Qutilar']),
 ('Маникюр и бритьё','Щипчики, наборы, станки','✂️',['Kusachkalar','Britvalar']),
 ('Дезодоранты и освежители','Для тела и дома','🌸',['Dezodarantlar']),
 ('Губки для посуды','Губки и сетки для мытья посуды','🧽',['Gupkalar']),
 ('Металлические мочалки','Для кастрюль и сковородок','🍳',["Sim sho'tkalar"]),
 ('Тряпки и микрофибра','Тряпки, полотенца из микрофибры','🧺',['Dilfin Latalar']),
 ('Щётки','Для ковров, одежды, хозяйства','🪮',['Shotkalar']),
 ('Крючки','Крючки-наклейки','🪝',['Ilmoqlar']),
 ('Перчатки','Нитриловые и хозяйственные','🧤',['Perchatkalar']),
 ('От комаров и насекомых','Фумигаторы, спирали, спреи','🦟',['Dorilar']),
 ('Скотч','Скотч разных размеров','📦',['Skoch']),
 ('Для обуви','Крем и уход за обувью','👞',['Oyoq Kiyim']),
 ('Для малышей','Соски, бутылочки, прорезыватели','🍼',['Chaqaloqlar']),
 ('Батарейки и лампочки','Батарейки, лампочки','🔋',['Batarekalar','Lampochkalar']),
 ('Разное','Другие товары','🛍️',['Aralash tovar','KPI dan tashqarisi','Zakolka','Penza toshlar','Kaltak']),
]
KIND_ALL={'Aksesuar':'Аксессуар','Gupkalar':'Губка для посуды','Skoch':'Скотч',"Xo'jalik Mollari":'Хозяйственное','Tozalash Maxsulotlari':'Чистящее средство',
 "Sim sho'tkalar":'Металлическая мочалка','Shotkalar':'Щётка','Sovun Qutilar':'Мыльница','Ilmoqlar':'Крючок','Oyoq Kiyim':'Для обуви','Dilfin Latalar':'Тряпка',
 'Lampochkalar':'Лампочка','Zakolka':'Заколка','Penza toshlar':'Пемза',"O'yinchoqlar":'Игрушка','Zuba Chistkalar':'Зубочистки'}
seen=set(); VSE=[]
for t,s,ic,types in G:
    ids=[i for i in avail if ty(i) in types and i not in seen]; seen|=set(ids)
    if ids: VSE.append((t,s,sorted(ids,key=key),ic))
rest=[i for i in avail if i not in seen]
if rest: VSE.append(('Разное','Другие товары',sorted(rest,key=key),'🛍️'))

SITES=[
 dict(key='apteka',icon='💊',h1='Товары для аптек',title='товары для аптек',lead='Детские товары, гигиена, уход за зубами и телом. Всё в наличии на складе.',
      d='#0b3b38',m='#11796c',l='#86e3cc',bg='#f6f2ea',acc='#c8a15a',hf="'Playfair Display',Georgia,serif",
      eyebrow='Для аптек и оптики · опт',feat='Выбор аптек',featsub='То, что аптеки берут чаще всего',pdf='apteka-katalog-vicon-*.pdf',secs=[(t,s,ids,AP_ICON[n%len(AP_ICON)]) for n,(t,s,ids) in enumerate(AP)]),
 dict(key='detskoe',icon='🧸',h1='Игрушки и детские товары',title='игрушки и детские товары',lead='Игрушки, товары для малышей, детский уход. Всё в наличии на складе.',
      d='#1f0b52',m='#ff4f8b',l='#ffc83d',bg='#fff6ef',acc='#3fe0ff',hf="'Unbounded',system-ui,sans-serif",
      eyebrow='Игрушки оптом · Ташкент',feat='Самое яркое',featsub='Игрушки, которые дети замечают первыми',pdf='igrushki-katalog-vicon-*.pdf',secs=DET),
 dict(key='vse',icon='🛒',h1='Все товары Vicon',title='все товары',lead='Весь склад Vicon Toshkent: гигиена, хозяйство, игрушки, аксессуары. Всё в наличии.',
      d='#0c1122',m='#3d6bff',l='#38d6f5',bg='#f3f4f8',acc='#f3c252',hf="'Unbounded',system-ui,sans-serif",
      eyebrow='Весь склад · опт · Ташкент',feat='Хиты склада',featsub='Лучшее из каждого раздела',pdf=None,secs=VSE),
]
now=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)+datetime.timedelta(hours=5)
MON=['января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря']
DATE=f'{now.day} {MON[now.month-1]} {now.year}, {now:%H:%M}'
os.makedirs(OUT+'/img',exist_ok=True); os.makedirs(OUT+'/th',exist_ok=True)
IMGV=not os.path.exists(OUT+'/.imgv2')
def pic(i):
    src=f'img_big/{i}.jpg'
    if not os.path.exists(src): return False
    d,t=f'{OUT}/img/{i}.jpg',f'{OUT}/th/{i}.jpg'
    if IMGV or not os.path.exists(t) or os.path.getmtime(t)<os.path.getmtime(src):   # лёгкие фото для слабого интернета
        im=Image.open(src).convert('RGB'); im.thumbnail((1100,1100)); im.save(d+'.tmp',format='JPEG',quality=74,optimize=True,progressive=True); os.replace(d+'.tmp',d)   # атомарно: телефон не получит полфайла
        im.thumbnail((360,450)); im.save(t+'.tmp',format='JPEG',quality=62,optimize=True,progressive=True); os.replace(t+'.tmp',t)
    return True
tpl=open('site_tpl.html').read()
if IMGV: open(OUT+'/.imgv2','w').write('1')
used=set(); report=[]
_IF=os.path.join(os.path.dirname(os.path.abspath(__file__)),'info','info.json')
INFO=json.load(open(_IF)) if os.path.exists(_IF) else {}   # описания «Подробнее»: {id: {ru,uz,media}}
for S in SITES:
    cats=[];prods=[];seen=set()
    for n,(t,s,ids,ic) in enumerate(S['secs'],1):
        ids=[i for i in ids if i in cur and float(b[i]['available'])>0 and i not in seen]
        if not ids: continue
        cats.append(dict(id=n,title=t,sub=s,count=len(ids),icon=ic))
        for i in ids:
            seen.add(i); x=b[i]; unit=x['measurement']['name']; im=pic(i); used.add(i)
            bx=B.box(x['title']); m=re.search(r'(\d+)\s*sht\s*$',x['title'],re.I); note=''
            if bx and unit=='шт': note=f'В коробке {bx} шт'
            elif m and 'ZAPAS' in x['title'].upper() and unit=='шт': note=f'В упаковке {m.group(1)} шт, цена за упаковку'
            prods.append(dict(id=i,cat=n,name=B.clean(x['title']) or x['title'],raw=x['title'],kind=kind(i),art=str(x['vendor_code'] or x['barcode'] or i),
                stock=int(float(x['available'])),unit=unit,price=int(cur[i]),per=('за шт' if unit=='шт' else 'за '+unit.lower()),
                hits=len(pop[i]),note=note,img=im,inf=int(str(i) in INFO),box=(int(bx) if bx and unit=='шт' and 1<int(bx)<=5000 else 0)))
    pid={p['id']:p for p in prods}
    def pick(c,by): xs=[p for p in prods if p['cat']==c['id'] and p['img']]; return max(xs,key=by)['id'] if xs else 0
    byp=lambda p:(p['price']*(1+p['hits']),p['stock'])
    for c in cats: c['cover']=pick(c,(lambda p:(p['price'],p['hits'])) if S['key']=='detskoe' else byp)
    feat=[]
    for c in cats[:12]:
        xs=sorted([p for p in prods if p['cat']==c['id'] and p['img']],key=(lambda p:-p['price']) if S['key']=='detskoe' else (lambda p:(-p['hits'],-p['price'])))
        feat+= [p['id'] for p in xs[:1 if S['key']!='apteka' else 2]]
    feat=feat[:12]
    import glob; pf=sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)),'pdf',S['pdf']))) if S['pdf'] else []
    site=dict(key=S['key'],icon=S['icon'],h1=S['h1'],lead=S['lead'],tg=TG,pdf=bool(pf),feat=feat,ft=S['feat'],fs=S['featsub'],eyebrow=S['eyebrow'],
              others=[dict(key=o['key'],icon=o['icon'],h1=o['h1']) for o in SITES if o is not S])
    d=f'{OUT}/{S["key"]}.new'; shutil.rmtree(d,ignore_errors=True); os.makedirs(d)
    open(d+'/data.js','w').write('window.DATA='+json.dumps(dict(cats=cats,prods=prods,date=DATE,ts=int(time.time()),site=site),ensure_ascii=False)+';')
    h=tpl
    for k,v in dict(__TITLE__=S['title'],__DESC__=S['lead'],__D__=S['d'],__M__=S['m'],__L__=S['l'],__BG__=S['bg'],__ACC__=S['acc'],__HF__=S['hf'],__THEME__=S['key'],__ICON__=S['icon'],__V__=str(int(time.time())),__UZ__=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'uz.json')).read()).items(): h=h.replace(k,v)
    open(d+'/index.html','w').write(h)
    shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)),'sw_tpl.js'),d+'/sw.js')
    if pf: shutil.copy(pf[-1],d+'/katalog.pdf')
    old=f'{OUT}/{S["key"]}'
    if os.path.exists(old): shutil.rmtree(old+'.old',ignore_errors=True); os.rename(old,old+'.old')
    os.rename(d,old); shutil.rmtree(old+'.old',ignore_errors=True)
    report.append(f'{S["key"]}: {len(prods)} товаров, {len(cats)} разделов, без фото {sum(not p["img"] for p in prods)}')
# главная со ссылками на три каталога
links=''.join(f'<a href="{S["key"]}/" style="display:block;margin:12px 0;padding:18px;border-radius:16px;color:#fff;text-decoration:none;font:700 20px system-ui;background:linear-gradient(90deg,{S["d"]},{S["m"]})">{S["icon"]} {S["h1"]}</a>' for S in SITES)
open(OUT+'/index.html','w').write(f'<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>Vicon Toshkent — каталоги</title><body style="margin:0;padding:24px;background:#f3f6fa;font-family:system-ui"><h1 style="font:800 26px system-ui">Vicon Toshkent</h1><p style="color:#556">Каталоги с остатками на {DATE}</p>{links}</body>')
# подробности: по файлу на товар, грузится только при открытии
_ID=f'{OUT}/info'; shutil.rmtree(_ID,ignore_errors=True); os.makedirs(_ID+'/img')
for i in used:
    v=INFO.get(str(i))
    if not v: continue
    for m in v.get('media',[]):
        if m.get('src'):
            src=os.path.join(os.path.dirname(_IF),m['src'])
            if os.path.exists(src): shutil.copy(src,f'{_ID}/{m["src"]}')
    v=dict(v,media=[m for m in v.get('media',[]) if m.get('type')=='video' or (m.get('src') and os.path.exists(f'{_ID}/{m["src"]}'))])
    open(f'{_ID}/{i}.json','w').write(json.dumps(v,ensure_ascii=False))
report.append(f'подробности: {sum(1 for i in used if str(i) in INFO)} товаров')
for dname in ('img','th'):   # убрать фото товаров, которых больше нет
    for f in os.listdir(f'{OUT}/{dname}'):
        if f.endswith('.jpg') and int(f[:-4]) not in used: os.remove(f'{OUT}/{dname}/{f}')
print('\n'.join(report)); print('остатки на',DATE)
