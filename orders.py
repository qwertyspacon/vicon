import json,os,urllib.request
tok=os.environ['LINKO_TOKEN']
B='https://vicontoshkent.linko.uz/ru/api/v1/'
def get(url):
    r=urllib.request.Request(url,headers={'Authorization':'Token '+tok}); return json.load(urllib.request.urlopen(r,timeout=60))
orders=[];url=B+'sales/order/?page_size=200'
while url:
    d=get(url);orders+=d['results'];url=d.get('next')
items=[]
for o in orders:
    mk=(o.get('market') or {}).get('name')
    url=B+f"sales/order_product/?page_size=200&order={o['id']}"
    while url:
        d=get(url)
        for i in d['results']:
            items.append({'order':o['id'],'market':mk,'date':o.get('created_date') or o.get('tm'),'pid':i['product_id'],'name':i['product_name'],'amount':float(i['amount']),'price':float(i['price']),'unit':i['measurement']['name'],'bonus':i['is_bonus']})
        url=d.get('next')
json.dump(items,open('my_order_items.json','w'),ensure_ascii=False)
print(len(orders),'заказов',len(items),'строк')
