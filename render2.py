from playwright.sync_api import sync_playwright
import os,datetime,sys
D=(datetime.datetime.utcnow()+datetime.timedelta(hours=5)).strftime('%d.%m.%Y')
SRC=sys.argv[1] if len(sys.argv)>1 else 'catalog2.html'; DST=sys.argv[2] if len(sys.argv)>2 else 'catalog2.pdf'; LBL=sys.argv[3] if len(sys.argv)>3 else 'товары для аптек'
with sync_playwright() as p:
    br=p.chromium.launch(); pg=br.new_page()
    pg.goto('file://'+os.path.abspath(SRC)); pg.wait_for_timeout(1500)
    foot='<div style="width:100%;font-size:8px;color:#6a8083;padding:0 14mm;display:flex;justify-content:space-between;font-family:Noto Sans"><span>Vicon Toshkent · '+LBL+' · цены в сумах на '+D+'</span><span class="pageNumber"></span></div>'
    pg.pdf(path=DST,format='A4',print_background=True,display_header_footer=True,header_template='<div></div>',footer_template=foot,margin={'top':'8mm','bottom':'12mm','left':'0','right':'0'})
    br.close()
