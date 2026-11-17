#!/bin/bash
# Живые остатки: каждые 3 минуты (06:30–22:00 Ташкент) читаем ТОЛЬКО остатки из Linko (только чтение, ~6 с)
# и кладём маленький stock.json в ветку «stock» репозитория. Страница при каждом открытии берёт его
# с raw.githubusercontent.com и обновляет «в наличии». Полная пересборка сайта — по-прежнему push_data.sh.
# Запуск цикла:  setsid nohup ~/workspace/projects/vicon-pages/stock_live.sh loop >/dev/null 2>&1 &
# Разово: stock_live.sh once
L=~/workspace/projects/linko; R=~/workspace/projects/vicon-stock; LOG=$R.log
once() {
  if [ ! -d $R/.git ]; then
    rm -rf $R; mkdir -p $R && cd $R && git init -q && git remote add origin https://github.com/qwertyspacon/vicon.git &&
    git checkout -q --orphan stock || return 1
  fi
  cd $R || return 1
  LINKO_TOKEN=$(python3 -c "import json;print(json.load(open('$L/.signin.json'))['token'])") python3 - <<'EOF' || return 1
import json,os,time,urllib.request,sys
tok=os.environ['LINKO_TOKEN'];url='https://vicontoshkent.linko.uz/ru/api/v1/stock/all_balances/?stock=1&page_size=200';res=[]
while url:
    d=json.load(urllib.request.urlopen(urllib.request.Request(url,headers={'Authorization':'Token '+tok}),timeout=60));res+=d['results'];url=d.get('next')
if len(res)<300: sys.exit(f'мало остатков: {len(res)}')
s={str(x['id']):max(0,int(float(x['available']))) for x in res}
old={}
try: old=json.load(open('stock.json'))['s']
except Exception: pass
json.dump({'t':int(time.time()),'s':s},open('stock.json','w'),separators=(',',':'))
print('изменилось' if s!=old else 'без изменений',len(s))
EOF
  # пушим всегда (время проверки нужно странице), но одной правкой — история не растёт
  git add stock.json && git -c user.name=vicon-stock -c user.email=stock@localhost commit -q --amend -m stock 2>/dev/null ||
    git -c user.name=vicon-stock -c user.email=stock@localhost commit -qm stock || return 1
  git push -qf origin stock 2>&1 | tail -2
}
case "$1" in
  once) once; echo "exit $?";;
  loop)
    exec 9>$R.lock; flock -n 9 || { echo "уже работает"; exit 0; }
    while true; do
      hm=$(TZ=Asia/Tashkent date +%H%M)
      if [ "$hm" -ge 0630 ] && [ "$hm" -le 2200 ]; then
        echo "$(date '+%F %T') $( (timeout 120 nice -n 10 bash $0 once) 2>&1 | tr '\n' ' ')" >> $LOG
        tail -n 300 $LOG > $LOG.t && mv $LOG.t $LOG
      fi
      sleep 180
    done;;
  *) echo "stock_live.sh once|loop";;
esac
