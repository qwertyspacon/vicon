#!/bin/bash
# Наш сервер забирает данные из Linko (GitHub Linko не пускает с 17.11) и отдаёт их сборке сайта.
# Данные шифруются (ключ: ~/workspace/projects/linko/.datakey = секрет LINKO_DATA_KEY), лежат в ветке linko-data
# (одна правка, история не растёт), затем запускается сборка сайта на GitHub.
# Разовый запуск:  push_data.sh once      Цикл (07:00, 12:00, 17:00) — из loop.sh (systemd), не nohup
cd "$(dirname "$0")"; L=~/workspace/projects/linko; W=~/workspace/tmp/linko-data; LOG=$W/push.log
mkdir -p $W; chmod 700 $W
once() {
  export LINKO_TOKEN=$(python3 -c "import json;print(json.load(open('$L/.signin.json'))['token'])")
  export DATA_KEY=$(cat $L/.datakey)
  rm -rf $W/d; mkdir -p $W/d
  python3 fetch_data.py $W/d || return 1
  tar czf $W/data.tgz -C $W/d balances.json prices.json my_order_items.json new.json stamp.txt || return 1
  openssl enc -aes-256-cbc -pbkdf2 -iter 200000 -salt -pass env:DATA_KEY -in $W/data.tgz -out $W/linko-data.enc || return 1
  rm -rf $W/g; git clone -q --depth 1 --no-checkout "$(git remote get-url origin)" $W/g && cd $W/g || return 1
  git checkout -q --orphan linko-data && git rm -rqf . 2>/dev/null; cp $W/linko-data.enc . && git add linko-data.enc &&
  git -c user.name=vicon-data -c user.email=data@localhost commit -qm "данные $(date '+%F %H:%M')" && git push -qf origin linko-data || return 1
  cd - >/dev/null; rm -rf $W/g $W/d $W/data.tgz
  gh workflow run update.yml -R qwertyspacon/vicon --ref main
}
case "$1" in
  once) once; echo "exit $?";;
  loop)
    exec 9>$W/loop.lock; flock -n 9 || { echo "уже работает"; exit 0; }
    while true; do
      h=$(TZ=Asia/Tashkent date +%H); slot="$(TZ=Asia/Tashkent date +%F)-$h"
      if [[ "$h" == 07 || "$h" == 12 || "$h" == 17 ]] && [ "$(cat $W/last 2>/dev/null)" != "$slot" ]; then
        for a in 1 2 3; do
          if timeout 1500 nice -n 10 bash $0 once >> $LOG 2>&1; tail -1 $LOG | grep -q "exit 0"; then break; fi; sleep 300
        done
        echo "$slot" > $W/last; echo "$(date '+%F %T') слот $slot: $(tail -1 $LOG)" >> $LOG
      fi
      tail -n 200 $LOG > $LOG.t 2>/dev/null && mv $LOG.t $LOG
      sleep 300
    done;;
  *) echo "push_data.sh once|loop";;
esac
