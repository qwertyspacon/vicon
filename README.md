# Каталоги Vicon Toshkent

Сайты: https://qwertyspacon.github.io/vicon/apteki/ · /igrushki/ · /tovary/

## Откуда данные и как обновляется (с 17.11)
- GitHub в Linko больше не пускают, поэтому данные забирает **наш сервер**: `push_data.sh` в 07:00, 12:00, 17:00 (Ташкент) читает Linko (только чтение), шифрует (ключ `~/workspace/projects/linko/.datakey` = секрет `LINKO_DATA_KEY`) и кладёт в ветку `linko-data`, потом запускает сборку на GitHub (`.github/workflows/update.yml` → `ci.py`, публикация на Pages).
- Живые остатки: `stock_live.sh` каждые 3 мин 06:30–22:00 → ветка `stock` (`../vicon-stock`, свой README); страница берёт `stock.json` при каждом открытии.
- Оба цикла запускает `loop.sh` под systemd (строка `vicon-pages` в `projects/loops.txt`), не nohup. Статус: `/var/lib/sharof-loops/status.txt`.
- Шаблон страницы — `site_tpl.html`, офлайн-кэш — `sw_tpl.js` (при каждой выкладке поднимать версию). Пуш в `main` тоже запускает сборку.
- Вручную: `./push_data.sh once` или Actions → «Обновление каталогов из Linko» → Run workflow.
