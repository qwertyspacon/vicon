import json,re,collections,html,os,datetime
_now=datetime.datetime.utcnow()+datetime.timedelta(hours=5)
_MON=['января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря']
DATE_RU=f'{_now.day} {_MON[_now.month-1]} {_now.year}'
b={x['id']:x for x in json.load(open('balances.json'))}
P=json.load(open('prices.json')); orders=json.load(open('my_order_items.json'))
rows=json.load(open('sel_ids.json'))['rows']
cur={}
for x in sorted(P,key=lambda x:x['created_date']):
    c=float(x['cash_price'] or 0)
    if c>100: cur[x['product']['id']]=c
pop=collections.defaultdict(set)
for i in orders: pop[i['pid']].add(i['market'])
def key(i): return (-len(pop[i]),-float(b[i]['available']))
def has(i,p): return re.search(p,b[i]['title'],re.I)
A=rows['A']
sections=[]
def sec(title,sub,ids,note=''): sections.append((title,sub,ids,note))
teeth=[i for i in A if has(i,'^Calsi')]
sec('Прорезыватели для зубов','Силиконовые прорезыватели Calsi — для малышей, когда режутся зубки',sorted(teeth,key=key))
sec('Соски, бутылочки, поильники','Для кормления малыша',sorted([i for i in A if i not in teeth],key=key)[:18])
sec('Детские зубные щётки','Мягкие щётки для малышей и школьников',sorted([i for i in rows['B2'] if not has(i,'idish')],key=key)[:8])
sec('Зубные пасты','Детская и взрослые',sorted(rows['B1'],key=lambda i:(0 if has(i,'Detskiy') else 1,)+key(i)))
sec('Зубные щётки для взрослых','Самые ходовые',sorted([i for i in rows['B3'] if not has(i,'idish')],key=key)[:8])
sec('Зубочистки и флосс','Флосс-зубочистки и зубочистки в удобных упаковках',rows['C'])
sec('Ватные палочки, диски, салфетки','Ежедневная гигиена',sorted(rows['D1'],key=key)[:10]+sorted(rows['D2'],key=key)[:8])
sec('Шампуни, гели, мыло','Детские и для всей семьи',sorted(rows['E1'],key=key)+sorted(rows['E2'],key=key)[:13])
sec('Маникюр и бритьё','Щипчики, маникюрные наборы, станки',sorted(rows['F'],key=key)[:12]+sorted(rows['F2'],key=key)[:6])
sec('Нитриловые перчатки','Одноразовые, пачка 100 штук',sorted(rows['J'],key=key)[:8])
sec('Защита от комаров и насекомых','Фумигаторы, жидкость, спираль, спрей',sorted(rows['H'],key=key))
sec('Дезодоранты и освежители','Для тела и дома',sorted(rows['G'],key=key)[:8])
sec('Мочалки и губки для тела','Для ванной',sorted(rows['I'],key=key)[:8])
sec('Батарейки','Для часов, пультов, термометров',sorted(rows['K'],key=key)[:8])
SECKIND={}
def kind(i):
    t=b[i]['title']; ty=b[i]['type']['name']
    if re.match('Calsi',t): return 'Прорезыватель для зубов'
    if re.search('Grudanasos',t,re.I): return 'Молокоотсос'
    if re.search('Sut idish|sut idish|So.rg.ich Idishlik',t) and 'ZAPAS' not in t.upper(): return 'Детская бутылочка'
    if re.search('ZAPAS|So.rg.ich',t,re.I): return 'Соска-пустышка'
    if ty=='Chaqaloqlar': return 'Для малышей'
    if re.search('Pasta',t,re.I) and not re.search('sho.?tka',t,re.I): return 'Зубная паста'
    if re.search('Zub.*sho.?tka|Tish.*sho.?tka|sho.?tka',t,re.I) and ty in("Tish Sho'tkalar",'Zubnaya Pastalar'): return 'Детская зубная щётка' if re.search('detsk|detisk|panja',t,re.I) else 'Зубная щётка'
    if t.startswith('Zuba Iplik'): return 'Флосс-зубочистки'
    if t.startswith('Zuba'): return 'Зубочистки'
    if ty=='Uxa Chistkalar': return 'Ватные палочки'
    if ty=='Vatnie Diski': return 'Ватные диски'
    if ty=='Salfetkalar': return 'Салфетки'
    if re.search('baby',t,re.I): return 'Детский шампунь-гель'
    if re.search('Sovun',t,re.I): return 'Мыло'
    if re.search('Gel',t,re.I): return 'Гель для душа'
    if re.search('Shampun|Shampoo',t,re.I): return 'Шампунь'
    if re.search('Locion',t,re.I): return 'Лосьон'
    if ty=='Kusachkalar': return 'Маникюр, щипчики'
    if ty=='Britvalar' or t.startswith('Dorco'): return 'Бритвенные станки'
    if ty=='Dezodarantlar': return 'Дезодорант'
    if ty=='Perchatkalar': return 'Нитриловые перчатки'
    if ty=='Batarekalar': return 'Батарейка'
    if ty=='Gigiena Banni Machalkalar': return 'Мочалка для тела'
    if ty=='Dorilar': return 'От насекомых'
    return ''
def clean(t):
    t=re.sub(r'\(\s*[\d\s]*sht[^)]*\)?','',t,flags=re.I); t=re.sub(r'\(\s*\d+\s*\)','',t)
    t=re.sub(r'\b\d+\s*sht\b','',t,flags=re.I)
    t=re.sub(r'\s+',' ',t).strip(' -+'); return t
def box(t):
    m=re.search(r'\(\s*(\d[\d\s]*?)\s*sht\s*\)',t,re.I)
    return m.group(1).replace(' ','') if m else None
def card(i):
    x=b[i]; unit=x['measurement']['name']; av=int(float(x['available'])); pr=cur[i]
    k=len(pop[i]); art=x['vendor_code'] or x['barcode'] or i
    fn=f'img2/{i}.jpg'; im=f'<img src="{fn}">' if os.path.exists(fn) else '<div class="no">фото нет</div>'
    bx=box(x['title']); u='за шт' if unit=='шт' else 'за '+unit.lower()
    hit=f'<div class="hit">★ Берут {k} магазинов</div>' if k>=8 else ''
    kd=kind(i); kd=f'<div class="kind">{kd}</div>' if kd else ''
    boxs=f'<div class="m">В коробке: <b>{bx} шт</b></div>' if bx and unit=='шт' else ''
    pk=re.search(r'(\d+)\s*sht\s*$',x['title'],re.I)
    if pk and not bx and unit=='шт' and re.search('ZAPAS',x['title'],re.I): boxs=f'<div class="m">В упаковке: <b>{pk.group(1)} шт</b> (цена за упаковку)</div>'
    return (f'<div class="c"><div class="ph">{im}</div><div class="tx">{kd}<div class="n">{html.escape(clean(x["title"]))}</div>'
            f'<div class="m">Артикул: <b>{art}</b></div><div class="m">В наличии: <b>{av:,} {unit}</b>'.replace(',',' ')+'</div>'+boxs+hit+
            f'<div class="pr">{pr:,.0f} <span>сум</span></div><div class="u">{u}</div></div></div>').replace(f'{pr:,.0f}',f'{pr:,.0f}'.replace(',',' '))
css='''
@page{size:A4;margin:0}
*{box-sizing:border-box}
body{margin:0;font-family:"Noto Sans","Liberation Sans",sans-serif;color:#1c2b2d}
.cover{height:297mm;width:210mm;background:linear-gradient(160deg,#08626b 0%,#0d8a8a 55%,#35b9a5 100%);color:#fff;padding:26mm 20mm;position:relative;page-break-after:always;overflow:hidden}
.cover:before{content:"";position:absolute;right:-60mm;top:-40mm;width:150mm;height:150mm;border-radius:50%;background:rgba(255,255,255,.08)}
.cover:after{content:"";position:absolute;left:-50mm;bottom:-50mm;width:130mm;height:130mm;border-radius:50%;background:rgba(255,255,255,.07)}
.brand{font-size:15pt;letter-spacing:.3em;font-weight:700;opacity:.9}
.cover h1{font-size:50pt;line-height:1.02;margin:46mm 0 8mm;font-weight:700}
.cover .sub{font-size:17pt;max-width:140mm;line-height:1.4;opacity:.95}
.cover .date{position:absolute;left:20mm;bottom:26mm;font-size:13pt}
.cover .date b{display:block;font-size:19pt;margin-bottom:2mm}
.cross{position:absolute;right:22mm;bottom:24mm;width:34mm;height:34mm}
.toc{height:297mm;padding:22mm 20mm;page-break-after:always}
.toc h2{font-size:26pt;color:#08626b;margin:0 0 10mm}
.toc a{display:flex;justify-content:space-between;align-items:baseline;text-decoration:none;color:#1c2b2d;font-size:14pt;padding:3.2mm 0;border-bottom:1px solid #d6e6e6}
.toc a span{color:#0d8a8a;font-weight:700;font-size:12pt}
.toc .n{margin-top:10mm;font-size:10.5pt;color:#51676a;line-height:1.5}
.sec{padding:0 14mm;page-break-before:always}
.sec:first-of-type{page-break-before:auto}
.sh{background:linear-gradient(90deg,#08626b,#0d8a8a);color:#fff;border-radius:3mm;padding:5mm 7mm;margin:12mm 0 5mm}
.sh h2{margin:0;font-size:20pt}.sh p{margin:1mm 0 0;font-size:10.5pt;opacity:.92}
.g{display:grid;grid-template-columns:1fr 1fr;gap:4mm}
.c{display:flex;gap:3mm;border:1px solid #cfe3e3;border-radius:3mm;padding:3mm;break-inside:avoid;height:55mm;background:#fff}
.ph{width:41%;flex:none;background:#f1f8f8;border-radius:2mm;display:flex;align-items:center;justify-content:center;overflow:hidden}
.ph img{width:100%;height:100%;object-fit:contain}
.no{color:#8aa;font-size:9pt}
.tx{flex:1;min-width:0;display:flex;flex-direction:column}
.kind{font-size:7.5pt;font-weight:700;color:#0d8a8a;text-transform:uppercase;letter-spacing:.04em}
.n{font-size:10.5pt;font-weight:700;line-height:1.2;max-height:2.6em;overflow:hidden;margin-bottom:1.2mm}
.m{font-size:9pt;color:#3d5558;line-height:1.35}
.hit{font-size:8pt;color:#b8620b;font-weight:700;margin-top:.8mm}
.pr{margin-top:auto;font-size:17pt;font-weight:700;color:#0a6a4a;line-height:1}
.pr span{font-size:10pt}
.u{font-size:8.5pt;color:#6a8083}
'''
def pages_html():
    out=[]; toc=[]
    for n,(t,s,ids,note) in enumerate(sections,1):
        ids=[i for i in ids if i in cur]
        if not ids: continue
        toc.append((n,t,len(ids)))
        out.append(f'<div class="sec" id="s{n}"><div class="sh"><h2>{n}. {html.escape(t)}</h2><p>{html.escape(s)}</p></div><div class="g">'+''.join(card(i) for i in ids)+'</div></div>')
    return out,toc
secs,toc=pages_html()
total=sum(c for _,_,c in toc)
cover=f'''<div class="cover"><div class="brand">VICON TOSHKENT</div><h1>Товары<br>для аптек</h1>
<div class="sub">Детские товары, гигиена, уход за зубами и телом. Всё в наличии на складе.</div>
<svg class="cross" viewBox="0 0 100 100"><rect x="36" y="6" width="28" height="88" rx="6" fill="#fff" opacity=".9"/><rect x="6" y="36" width="88" height="28" rx="6" fill="#fff" opacity=".9"/></svg>
<div class="date"><b>Остатки и цены на {DATE_RU}</b>{total} товаров · цены в сумах</div></div>'''
tocp='<div class="toc"><h2>Что в каталоге</h2>'+''.join(f'<a href="#s{n}">{n}. {html.escape(t)} <span>{c} шт.</span></a>' for n,t,c in toc)+'<div class="n">Цена указана за единицу, как в складской программе: «за шт» или «за блок». Остаток — сколько есть на складе сейчас. «Берут N магазинов» — столько торговых точек уже заказывали этот товар.</div></div>'
open('catalog2.html','w').write(f'<html><meta charset=utf-8><style>{css}</style><body>{cover}{tocp}{"".join(secs)}</body></html>')
print(total,'товаров',[(n,t,c) for n,t,c in toc])
