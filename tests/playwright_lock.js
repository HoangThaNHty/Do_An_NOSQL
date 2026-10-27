async(page)=>{
 const checks=[];
 await page.setViewportSize({width:1440,height:1000});
 await page.goto('http://127.0.0.1:5000/login');
 if(await page.locator('#identifier').count()){await page.locator('#identifier').fill('admin');await page.locator('#password').fill('123456');await page.locator('main button[type=submit]').click();}
 const list=await(await page.request.get('http://127.0.0.1:5000/api/articles?per_page=1')).json();
 const id=list.data.items[0]._id;
 await page.request.post('http://127.0.0.1:5000/api/cache/invalidate/'+id);
 const before=await(await page.request.get('http://127.0.0.1:5000/api/cache/stats')).json();
 const responses=await Promise.all(Array.from({length:12},()=>page.request.get('http://127.0.0.1:5000/api/articles/'+id)));
 const bodies=await Promise.all(responses.map(r=>r.json()));
 const after=await(await page.request.get('http://127.0.0.1:5000/api/cache/stats')).json();
 const sources={database:bodies.filter(x=>x.source==='database').length,cache:bodies.filter(x=>x.source==='cache').length};
 checks.push({id:'LOCK-HTTP-01',pass:responses.every(r=>r.status()===200)&&sources.database===1&&sources.cache===11,detail:sources});
 checks.push({id:'LOCK-HTTP-02',pass:bodies.every(x=>JSON.stringify(x.data)===JSON.stringify(bodies[0].data)),detail:'Cùng payload giữa các nguồn'});
 checks.push({id:'LOCK-HTTP-03',pass:after.data.misses-before.data.misses===1,detail:{dbLoads:after.data.misses-before.data.misses,waits:after.data.lock_waits-before.data.lock_waits}});
 await page.goto('http://127.0.0.1:5000/admin/cache');
 checks.push({id:'LOCK-UI-01',pass:await page.locator('#live-lock-waits').isVisible()&&await page.locator('#live-lock-timeouts').isVisible(),detail:'Hiện thống kê chờ khóa và quá hạn'});
 await page.screenshot({path:'.playwright-mcp/cache-lock-desktop.png',fullPage:true});
 await page.setViewportSize({width:390,height:844});await page.reload();
 checks.push({id:'LOCK-UI-02',pass:await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth),detail:'Bố cục quản trị cache trên điện thoại'});
 await page.goto('http://127.0.0.1:5000/logout');await page.setViewportSize({width:1440,height:1000});await page.goto('http://127.0.0.1:5000/');
 return checks;
}
