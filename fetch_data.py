"""Забирает из Linko (ТОЛЬКО ЧТЕНИЕ) остатки, прайс и заказы в папку argv[1]. Токен — LINKO_TOKEN."""
import json,os,sys,time,subprocess,urllib.request
out=sys.argv[1]; tok=os.environ['LINKO_TOKEN']; B='https://vicontoshkent.linko.uz/ru/api/v1/'
def get_all(p):
    res=[];url=B+p+'&page_size=200'
    while url:
        for a in range(5):
            try:
                d=json.load(urllib.request.urlopen(urllib.request.Request(url,headers={'Authorization':'Token '+tok}),timeout=90)); break
            except urllib.error.HTTPError as e:
                if e.code in (401,403): sys.exit(f'Linko не пустил (код {e.code}): токен устарел')
                if a==4: raise
            except Exception:
                if a==4: raise
            time.sleep(20*(a+1))
        res+=d['results']; url=d.get('next')
    return res
bal=get_all('stock/all_balances/?stock=1'); pr=get_all('sales/price_list_item/?price_list=4')
if len(bal)<300 or len(pr)<500: sys.exit(f'подозрительно мало данных {len(bal)}/{len(pr)}')
json.dump(bal,open(f'{out}/balances.json','w'),ensure_ascii=False); json.dump(pr,open(f'{out}/prices.json','w'),ensure_ascii=False)
here=os.path.dirname(os.path.abspath(__file__))
r=subprocess.run([sys.executable,os.path.join(here,'orders.py')],cwd=out,timeout=900)
if r.returncode or not os.path.exists(f'{out}/my_order_items.json'):
    print('заказы не забрались — без «хитов»'); json.dump([],open(f'{out}/my_order_items.json','w'))
open(f'{out}/stamp.txt','w').write(str(int(time.time())))
print('ok',len(bal),len(pr))
