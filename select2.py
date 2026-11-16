import json,re,collections
b=json.load(open('balances.json')); P=json.load(open('prices.json')); items=json.load(open('my_order_items.json'))
cur={}
for x in sorted(P,key=lambda x:x['created_date']):
    c=float(x['cash_price'] or 0)
    if c>100: cur[x['product']['id']]=c
pop=collections.defaultdict(set)
for i in items: pop[i['pid']].add(i['market'])
def has(n,p): return re.search(p,n,re.I)
def grp(x):
    t=x['type']['name']; n=x['title']
    if t=='Chaqaloqlar': return 'A'
    if t=="Tish Sho'tkalar" or (t=='Zubnaya Pastalar' and has(n,'sho?tka')) or t=='Sprey va Sho\'tka idishlar' and has(n,'Tish|Zub'): return 'B2' if has(n,'detsk|detisk|kids|panja') else 'B3'
    if t=='Zubnaya Pastalar': return 'B1'
    if n.startswith('Zuba Iplik') or has(n,'^Zuba Zajgalka'): return 'C'
    if t in('Uxa Chistkalar','Vatnie Diski') and not has(n,'Bumaga'): return 'D1'
    if t=='Salfetkalar' and has(n,'Tabletka|Natural|Oq qush|Dispenser|Mushuk|Esma|Salfetka Arzon'): return 'D2'
    if t=='Shampun  Xitoy' and has(n,'baby'): return 'E1'
    if (t=='Hayat Shampun' and has(n,'Shampun|Shampoo|Milo|PASUDA')) or (t=='Shampun  Xitoy' and has(n,'Gel|Shampoo|Locion|Hand Wash|Qog.oz Sovun')): return 'E2'
    if t=='Kusachkalar': return 'F'
    if t=='Britvalar' or n.startswith('Dorco'): return 'F2'
    if t=='Dezodarantlar' and has(n,'Dezodarant'): return 'G'
    if t=='Dorilar' and has(n,'Shenke|Spiral|Mosquital|Raptor|Aparat|aparat|lipuchka\$|MENAN'): return 'H'
    if t=='Gigiena Banni Machalkalar' and has(n,'Barmoqcha|Silikon|Setka Mevalik|uzun sop|Atirgul|Lapsha|Spiral'): return 'I'
    if t=='Perchatkalar' and has(n,'Povur'): return 'J'
    if t=='Batarekalar': return 'K'
    return None
rows=collections.defaultdict(list)
for x in b:
    if float(x['available'])<=0 or x['id'] not in cur: continue
    g=grp(x)
    if g: rows[g].append(x)
for g in sorted(rows): print(g,len(rows[g]))
json.dump({'rows':{g:[x['id'] for x in v] for g,v in rows.items()}},open('sel_ids.json','w'))
