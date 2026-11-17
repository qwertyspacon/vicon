# vicon-stock — живые остатки для каталогов Vicon

- **Что это:** один файл `stock.json` (артикул → остаток). Каталоги apteki/igrushki/tovary при каждом открытии берут его и обновляют «в наличии».
- **Где живёт:** ветка `stock` репозитория github.com/qwertyspacon/vicon; живая ссылка https://raw.githubusercontent.com/qwertyspacon/vicon/stock/stock.json
- **Откуда данные:** Linko, только чтение остатков (~6 с за раз).
- **Как обновляется:** `projects/vicon-pages/stock_live.sh loop` каждые 3 мин 06:30–22:00, запускается из `projects/vicon-pages/loop.sh` (systemd, строка `vicon-pages` в `projects/loops.txt`). Каждый раз одна правка `--amend` + `push -f` — история не растёт. Руками здесь ничего не менять.
- Новые товары Linko, которых нет на сайте, → `../vicon-stock.new` → пересборка сайта (`push_data.sh once`) не чаще раза в час. Журнал: `../vicon-stock.log`.
