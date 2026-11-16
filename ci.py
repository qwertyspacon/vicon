"""Обновление каталогов Vicon из Linko (ТОЛЬКО ЧТЕНИЕ) и сборка сайта в папку _site.
Запускается GitHub Actions (.github/workflows/update.yml). Токен Linko — секрет LINKO_TOKEN.
Если Linko не ответил — выходим с ошибкой, и на GitHub Pages остаётся прошлая версия сайта.
"""
import json,os,sys,time,subprocess,urllib.request,datetime,glob,shutil
HERE=os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
PY=sys.executable; OUT=os.path.join(HERE,'_site')
tok=os.environ['LINKO_TOKEN']; B='https://vicontoshkent.linko.uz/ru/api/v1/'
def step(m): print(time.strftime('%H:%M:%S'),m,flush=True)
def get_all(p):
    out=[];url=B+p+'&page_size=200'
    while url:
        for a in range(4):
            try:
                r=urllib.request.Request(url,headers={'Authorization':'Token '+tok})
                d=json.load(urllib.request.urlopen(r,timeout=120)); break
            except urllib.error.HTTPError as e:
                if e.code in (401,403): sys.exit(f'Linko не пустил (код {e.code}): токен устарел, нужен новый вход')
                if a==3: raise
            except Exception:
                if a==3: raise
            time.sleep(15*(a+1))
        out+=d['results']; url=d.get('next')
    return out
def run(*args):
    step('▶ '+' '.join(args)); subprocess.run([PY,*args],check=True,timeout=1800)

step('остатки и прайс из Linko')
bal=get_all('stock/all_balances/?stock=1'); pr=get_all('sales/price_list_item/?price_list=4')
if len(bal)<300 or len(pr)<500: sys.exit(f'подозрительно мало данных {len(bal)}/{len(pr)} — сайт не трогаю')
json.dump(bal,open('balances.json','w'),ensure_ascii=False); json.dump(pr,open('prices.json','w'),ensure_ascii=False)
try: run('orders.py')                     # популярность («хиты»); не критично
except Exception as e:
    step(f'orders пропущен: {e}')
    if not os.path.exists('my_order_items.json'): json.dump([],open('my_order_items.json','w'))
for s in ('select2.py','dl2.py','toys.py','dl_toys.py','dl_all.py','build2.py','toys.py'): run(s)
day=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(hours=5)).strftime('%Y-%m-%d')
os.makedirs('pdf',exist_ok=True)
for f in glob.glob('pdf/*.pdf'): os.remove(f)
for src,name,lbl in (('catalog2.html','apteka','товары для аптек'),('toys.html','igrushki','игрушки')):
    run('render2.py',src,f'pdf/{name}-katalog-vicon-{day}.pdf',lbl)
shutil.rmtree(OUT,ignore_errors=True)
step('сборка сайтов'); r=subprocess.run([PY,'build_sites.py'],check=True,capture_output=True,text=True,env=dict(os.environ,SITES_OUT=OUT)); print(r.stdout)
for new,old in (('apteki','apteka'),('igrushki','detskoe'),('tovary','vse')):   # короткие адреса для агентов
    shutil.copytree(f'{OUT}/{old}',f'{OUT}/{new}')
for k in ('apteki','igrushki','tovary'):
    assert os.path.getsize(f'{OUT}/{k}/data.js')>10000, k
open(f'{OUT}/.nojekyll','w').close()
step('готово')
