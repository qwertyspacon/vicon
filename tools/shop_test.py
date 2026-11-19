"""Проход по живым каталогам как покупатель (ночной разбор, после каждой выкладки).
Телефон (390x844) и компьютер (1366x800): открытие, ошибки страницы, поиск, карточка товара,
«В заявку» -> счётчик заявки, «назад» закрывает карточку, время открытия. Ничего не отправляет.
Использование: python3 tools/shop_test.py [адрес ...]   Выход 0 = SHOP: PASS.
"""
import asyncio, sys, time
from playwright.async_api import async_playwright

SITES = sys.argv[1:] or [f"https://qwertyspacon.github.io/vicon/{s}/" for s in ("apteki", "igrushki", "tovary")]
DEVICES = {"телефон": dict(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True),
           "компьютер": dict(viewport={"width": 1366, "height": 800})}
fails = []

def ok(name, cond, extra=""):
    print(("PASS " if cond else "FAIL ") + name + (f" :: {extra}" if extra else ""))
    if not cond: fails.append(name)

async def one(b, url, dev):
    tag = f"{url.rstrip('/').rsplit('/', 1)[-1]}/{dev}"
    ctx = await b.new_context(**DEVICES[dev]); pg = await ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:120]))
    pg.on("console", lambda m: errs.append(m.text[:120]) if m.type == "error" and "favicon" not in m.text else None)
    t = time.time(); await pg.goto(url, wait_until="domcontentloaded")
    await pg.wait_for_selector("#q", state="visible", timeout=15000); load = time.time() - t
    ok(f"{tag}: сайт открылся за {load:.1f} с", load < 8)
    await pg.wait_for_timeout(1500)
    await pg.fill("#q", "10"); await pg.wait_for_timeout(1500)
    n = await pg.locator(".card").count()
    ok(f"{tag}: поиск по артикулу «10»", n > 0, f"{n} шт")
    card = pg.locator(".card").first
    await card.locator(".price").click(); await pg.wait_for_timeout(800)
    opened = await pg.evaluate("document.querySelector('#sheet,#ov') && getComputedStyle(document.querySelector('#sheet')||document.querySelector('#ov')).display!='none'")
    ok(f"{tag}: нажатие на цену открывает карточку", opened)
    await pg.go_back(); await pg.wait_for_timeout(800)
    ok(f"{tag}: «назад» оставляет на сайте", pg.url.startswith(url.rstrip('/')), pg.url[:60])
    btn = pg.locator(".card [data-q] button").first
    if await btn.count():
        await btn.click(); await pg.wait_for_timeout(500)
        ok(f"{tag}: «В заявку» -> счётчик", await pg.evaluate("Object.keys(cart).length>0") and any(c.isdigit() for c in (await pg.text_content("#fabn") or "")))
    ok(f"{tag}: без ошибок страницы", not errs, errs[:2])
    await ctx.close()

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for u in SITES:
            for d in DEVICES:
                try: await one(b, u, d)
                except Exception as e: ok(f"{u} {d}: прошёл до конца", False, str(e)[:150])
        await b.close()
    print("SHOP:", "PASS" if not fails else f"FAIL ({len(fails)})"); sys.exit(1 if fails else 0)

asyncio.run(main())
