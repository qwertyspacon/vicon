import asyncio, sys
from playwright.async_api import async_playwright
URL = 'https://qwertyspacon.github.io/vicon/tovary/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        c = await b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True, device_scale_factor=2)
        pg = await c.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(URL + '?nc=' + str(int(asyncio.get_event_loop().time())))
        await pg.wait_for_timeout(4000)
        html = await pg.content()
        print('новая версия:', 'по желанию' in html or 'Можно без фото' in html)
        # положить первый товар в заявку
        pid = await pg.evaluate("P[0].id")
        await pg.evaluate(f"cart[{pid}]=2;save&&save();openOrder&&openOrder()")
        await pg.wait_for_timeout(800)
        txt = await pg.evaluate("document.body.innerText")
        print('надпись под камерой:', [l for l in txt.split('\n') if 'фото' in l.lower()][:3])
        await pg.screenshot(path='/home/sharof/workspace/tmp/vsync/shot_order.png')
        # нажать отправку без фото
        nav = []
        await pg.evaluate("window.__h=[];const o=location.assign;")
        toasts = []
        await pg.expose_function('logToast', lambda t: toasts.append(t))
        await pg.evaluate("const T=toast;window.toast=(t,...a)=>{logToast(String(t));return T(t,...a)}")
        await pg.evaluate("document.getElementById('phf').addEventListener('click',()=>logToast('CAMERA_OPENED'))")
        pg.on('framenavigated', lambda f: nav.append(f.url))
        btn = await pg.evaluate("(()=>{const e=[...document.querySelectorAll('[onclick*=goTg]')].map(x=>x.id||x.textContent.trim());return e})()")
        print('кнопки отправки:', btn)
        await pg.evaluate("(()=>{const e=document.querySelector('[onclick*=goTg]');goTg(e)})()")
        await pg.wait_for_timeout(1500)
        print('сообщения:', toasts)
        ok = not any('Сначала' in t or 'CAMERA' in t for t in toasts) and any('скопирован' in t.lower() or 'telegram' in t.lower() for t in toasts)
        print('ошибки страницы:', errs)
        print('NOPHOTO:', 'PASS' if ok and not errs else 'FAIL')
        await b.close()
asyncio.run(main())
