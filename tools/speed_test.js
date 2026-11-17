const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const c=await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:1,isMobile:true,userAgent:'Mozilla/5.0 (Linux; Android 12; SM-A125F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36 Telegram-Android/11.0'});
const p=await c.newPage();const cdp=await c.newCDPSession(p);
await cdp.send('Network.enable');await cdp.send('Network.setCacheDisabled',{cacheDisabled:true});
await cdp.send('Network.emulateNetworkConditions',{offline:false,latency:400,downloadThroughput:400e3/8,uploadThroughput:400e3/8});
const t=Date.now();let bytes=0;p.on('response',r=>{r.body().then(x=>{bytes+=x.length; console.log(((Date.now()-t)/1000).toFixed(1)+'s',x.length,r.url().slice(0,80))}).catch(()=>{})});
p.goto(process.argv[2]).catch(e=>console.log('goto',e.message));
for(const s of [1,2,3,5,8]){await new Promise(r=>setTimeout(r,(s*1000)-(Date.now()-t)));await p.screenshot({path:`shot${s}.png`});}
const fcp=await p.evaluate(()=>{const e=performance.getEntriesByName('first-contentful-paint')[0];return e&&e.startTime});console.log('FCP',fcp);
await b.close()})();
