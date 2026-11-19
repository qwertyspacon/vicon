#!/bin/bash
# Фоновые циклы сайтов Vicon под systemd (sharof-project-loop@vicon-pages, список: projects/loops.txt):
#   push_data.sh loop  — данные Linko в 07/12/17 -> ветка linko-data -> сборка сайта на GitHub
#   stock_live.sh loop — остатки каждые 3 мин 06:30–22:00 -> ветка stock
# Упал один — выходим целиком, systemd перезапустит через 5 мин; второй экземпляр не даст запуститься flock.
cd "$(dirname "$0")" || exit 1
./push_data.sh loop & ./stock_live.sh loop &
wait -n
rc=$?
kill $(jobs -p) 2>/dev/null
wait
exit $((rc == 0 ? 1 : rc))
