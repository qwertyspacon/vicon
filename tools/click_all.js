// click_all.js — робот нажимает КАЖДУЮ карточку (лента, разделы) на телефоне Pixel 7: открывается ли товар, работает ли «В заявку».
// Использование: node tools/click_all.js <база, напр. https://qwertyspacon.github.io/vicon/> [apteki,igrushki,tovary]   (из 18.11, П-068)
const {chromium,devices}=require('playwright');
const base=process.argv[2];
(async()=>{const b=await chromium.launch();
for(const s of (process.argv[3]||'apteki,igrushki,tovary').split(',')){
const c=await b.newContext({...devices['Pixel 7']});const pg=await c.newPage();const errs=[];pg.on('pageerror',e=>errs.push(e.message));
await pg.goto(base+s+'/');await pg.waitForTimeout(2000);
const cats=await pg.evaluate(()=>DATA.cats.map(c=>c.id));let ok=0,bad=[],addOk=0,addBad=0;
const closed=()=>pg.evaluate(()=>!document.getElementById('ov').classList.contains('on'));
// rail
const rn=await pg.locator('.rail .sc').count();
for(let i=0;i<rn;i++){const el=pg.locator('.rail .sc .meta').nth(i);await el.evaluate(e=>e.scrollIntoView({block:'center'}));await el.click();if(await closed())bad.push('rail'+i);else{ok++;await pg.evaluate(()=>closeSheet())}}
for(const cid of cats){await pg.evaluate(c=>{location.hash='#/cat/'+c},cid);await pg.waitForTimeout(400);
 const n=Math.min(await pg.locator('.card').count(),12);
 for(let i=0;i<n;i++){const card=pg.locator('.card').nth(i);
  for(const part of ['.im','.nm','.meta','.price','.bdgs .badge']){const el=card.locator(part).first();if(!await el.count())continue;
   await el.evaluate(e=>e.scrollIntoView({block:'center'}));await el.click({timeout:3000});await pg.waitForTimeout(60);
   if(await closed())bad.push(cid+'#'+i+part);else{ok++;await pg.evaluate(()=>closeSheet())}}
  const add=card.locator('button.add');if(await add.count()){await add.evaluate(e=>e.scrollIntoView({block:'center'}));try{await add.click({timeout:3000})}catch(e){bad.push('ADD'+cid+'#'+i);continue}await pg.waitForTimeout(60);if(await closed())addOk++;else{addBad++;await pg.evaluate(()=>closeSheet())}}
 }}
console.log(s,'opened',ok,'notOpened',bad.length,JSON.stringify(bad.slice(0,8)),'addBtnOk',addOk,'addBtnOpenedSheet',addBad,'cart',await pg.evaluate(()=>Object.keys(cart).length),'errs',JSON.stringify(errs.slice(0,3)));
await c.close()}
await b.close()})();
