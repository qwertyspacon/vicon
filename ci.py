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
        for a in range(3):   # Linko не пускает GitHub — долго не ждём, есть данные с нашего сервера
            try:
                r=urllib.request.Request(url,headers={'Authorization':'Token '+tok})
                d=json.load(urllib.request.urlopen(r,timeout=60)); break
            except urllib.error.HTTPError as e:
                if e.code in (401,403): sys.exit(f'Linko не пустил (код {e.code}): токен устарел, нужен новый вход')
                if a==2: raise
            except Exception as e:
                step(f'Linko не ответил ({type(e).__name__}), попытка {a+1}/3')
                if a==2: raise
            time.sleep(30*(a+1))
        out+=d['results']; url=d.get('next')
    return out
def run(*args):
    step('▶ '+' '.join(args)); subprocess.run([PY,*args],check=True,timeout=1800)

for d in ('img2','img_big','pdf'): os.makedirs(d,exist_ok=True)   # на чистой машине GitHub папок нет
def from_server(max_age_h):
    """Данные, которые забрал наш сервер (push_data.sh): ветка linko-data, файл зашифрован (секрет LINKO_DATA_KEY)."""
    key=os.environ.get('LINKO_DATA_KEY')
    if not key: return False
    try:
        subprocess.run(['git','fetch','-q','--depth','1','origin','linko-data'],check=True,timeout=120)
        enc=subprocess.run(['git','show','FETCH_HEAD:linko-data.enc'],check=True,capture_output=True).stdout
        tgz=subprocess.run(['openssl','enc','-d','-aes-256-cbc','-pbkdf2','-iter','200000','-pass','env:K'],input=enc,check=True,capture_output=True,env=dict(os.environ,K=key)).stdout
        os.makedirs('srv',exist_ok=True); subprocess.run(['tar','xzf','-','-C','srv'],input=tgz,check=True)
        age=(time.time()-int(open('srv/stamp.txt').read()))/3600
        step(f'данные с нашего сервера: {age:.1f} ч назад')
        if age>max_age_h: return False
        for f in ('balances.json','prices.json','my_order_items.json'): shutil.copy(f'srv/{f}',f)
        return True
    except Exception as e:
        step(f'данных с сервера нет: {e}'); return False
    finally: shutil.rmtree('srv',ignore_errors=True)

if from_server(6): step('беру свежие данные с нашего сервера')
else:
    step('остатки и прайс из Linko')
    try:
        bal=get_all('stock/all_balances/?stock=1'); pr=get_all('sales/price_list_item/?price_list=4')
        if len(bal)<300 or len(pr)<500: sys.exit(f'подозрительно мало данных {len(bal)}/{len(pr)} — сайт не трогаю')
        json.dump(bal,open('balances.json','w'),ensure_ascii=False); json.dump(pr,open('prices.json','w'),ensure_ascii=False)
        try: run('orders.py')                     # популярность («хиты»); не критично
        except Exception as e:
            step(f'orders пропущен: {e}')
            if not os.path.exists('my_order_items.json'): json.dump([],open('my_order_items.json','w'))
    except SystemExit: raise
    except Exception as e:
        step(f'Linko не ответил ({e}) — беру последние данные с нашего сервера')
        if not from_server(72): sys.exit('нет ни Linko, ни данных с сервера — сайт не трогаю')
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
