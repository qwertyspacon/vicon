"""Каталог игрушек Vicon (PDF). Нужны свежие balances.json/prices.json (fetch.py).
Запуск: python3 toys.py && python3 dl_toys.py && python3 toys.py && python3 render2.py toys.html toys.pdf "игрушки"
"""
import json,re,io,contextlib,html,os
with contextlib.redirect_stdout(io.StringIO()):
    import build2 as B
b=B.b; cur=B.cur
T=[i for i,x in b.items() if x['type']['name']=="O'yinchoqlar" and float(x['available'])>0 and i in cur]
def h(i,p): return re.search(p,b[i]['title'],re.I)
RULES=[  # (раздел, подпись, вид товара, шаблон)
 ('Водные пистолеты и автоматы','Летний хит: от маленьких до больших','Водный пистолет',r'^Suv (Pistolet|Avtomat)'),
 ('Мыльные пузыри','Пистолеты и вентиляторы с пузырями','Мыльные пузыри',r'Fuzer'),
 ('Мячи','Детские, волейбольные, баскетбольные, игла и сетка','Мяч',r"^To'p"),
 ('Ночники','Светильники-ночники для детской','Ночник',r'SVETILNIK'),
 ('Куклы и фигурки','Куклы, Барби, мягкие фигурки','Кукла',r'Kukla|Barbi|Mickey Mouse (Qiz|O)|Tulki|Mushukcha|It jiji|Quyon'),
 ('Машинки, самолёты, дроны','Транспорт и летающие игрушки','Транспорт',r'Mashina|Moshina|Avtobus|Vertal|Dron|Samal|samal|Mototsikl|Motosikl|StuntCar|Teslacha|Uchadig|Go.nchik|Kuller Mashina'),
 ('Сюжетные наборы','Полиция, доктор, пожарные, кухня, рыбалка','Набор',r'Nabor|Burger|Fast Food|Lenta|Ratsiya|Durbin|Camera|Telefon|Avtomat Spider|Pistolet'),
 ('Музыкальные игрушки','Гитары, пианино, саксофон','Музыкальная игрушка',r'Gitara|Pianino|Saksafon|Vuvuzela'),
 ('Для малышей','Погремушки, игрушки для ванной','Для малышей',r'Shildiroq|Shildiiroq|Rul|Rakushka'),
 ('Развивающие и антистресс','Кубики Рубика, мозаика, пазлы, лабиринты, спиннеры','Развивающая игрушка',r'Rubik|Mozaika|Puzl|Labirint|Antistress|Spinner'),
 ('Водные игры','Игры с кольцами и водой','Водная игра',r'Water Game'),
 ('Для бассейна и пляжа','Надувные круги, жилеты, нарукавники','Для плавания',r'Balon|Suzish'),
 ('Сюрпризы в пакетиках','Фигурки-сюрпризы, блоки по 1152 шт','Сюрприз',r'Paketchal'),
 ('Мини-вентиляторы','Ручные вентиляторы','Мини-вентилятор',r'Ventilyator'),
 ('Для праздника','Хлопушки, веера, бумажные шары, обручи','Праздник',r'Xlapushka|Yelpig|Shar Qogoz|Obrich|Ukaska|Kuller|Raketka|Vertushka|Sakrash|Nayzacha|plastilin|Tuxum'),
]
SKIP=r'Sovun|Pol Latta|Suv Idish|Sut Idish'
KIND={}; secs={r[0]:[] for r in RULES}; left=[]
for i in T:
    if h(i,SKIP): continue
    for t,s,k,p in RULES:
        if h(i,p) and not (t=='Водные пистолеты и автоматы' and h(i,'Fuzer')):
            secs[t].append(i); KIND[i]=k; break
    else: left.append(i)
B.kind=lambda i: KIND.get(i,'')
B.sections=[(t,s,sorted(secs[t],key=B.key),'') for t,s,k,p in RULES if secs[t]]
json.dump({'ids':[i for _,_,ids,_ in B.sections for i in ids]},open('toys_ids.json','w'))
out,toc=B.pages_html(); total=sum(c for _,_,c in toc)
css=B.css.replace('#08626b','#6b2bb8').replace('#0d8a8a','#d9427a').replace('#35b9a5','#ff9f43').replace('#cfe3e3','#ecd9f2').replace('#f1f8f8','#fbf4fb').replace('#d6e6e6','#eddcf2')
cover=f'''<div class="cover"><div class="brand">VICON TOSHKENT</div><h1>Игрушки</h1>
<div class="sub">Водные пистолеты, мячи, ночники, куклы, машинки, развивающие игрушки. Всё в наличии на складе.</div>
<div class="date"><b>Остатки и цены на {B.DATE_RU}</b>{total} товаров · цены в сумах</div></div>'''
tocp='<div class="toc"><h2>Что в каталоге</h2>'+''.join(f'<a href="#s{n}">{n}. {html.escape(t)} <span>{c} шт.</span></a>' for n,t,c in toc)+'<div class="n">Цена указана за единицу, как в складской программе: «за шт» или «за блок». Остаток — сколько есть на складе сейчас. «Берут N магазинов» — столько торговых точек уже заказывали этот товар.</div></div>'
open('toys.html','w').write(f'<html><meta charset=utf-8><style>{css}</style><body>{cover}{tocp}{"".join(out)}</body></html>')
print(total,'игрушек',[(t,c) for n,t,c in toc]); print('не разложено:',[b[i]['title'] for i in left])
