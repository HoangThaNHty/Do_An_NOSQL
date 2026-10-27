async(page)=>{
 const results=[];await page.setViewportSize({width:1440,height:1000});
 await page.goto('http://127.0.0.1:5000/');
 const input=page.locator('.search-box input[name=q]');
 const pattern='**/api/articles/suggestions?**';
 const handler=async route=>{
  const q=new URL(route.request().url()).searchParams.get('q');
  if(q==='container'){
   await new Promise(resolve=>setTimeout(resolve,550));
   try{await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({success:true,data:{total:1,items:[{_id:'old',title:'KẾT QUẢ CŨ KHÔNG ĐƯỢC HIỆN',image:'/static/images/news_009.jpg',category:'Kinh tế'}]}})});}catch(error){}
  }else if(q==='loi_goi_y_qa'){await route.fulfill({status:500,body:'test failure'});}
  else await route.continue();
 };
 await page.route(pattern,handler);
 try{
  const started=page.waitForRequest(request=>request.url().includes('/api/articles/suggestions?q=container'));
  await input.fill('container');await started;await input.fill('salad');
  await page.waitForFunction(()=>document.querySelector('.search-box .search-suggestion-item')?.textContent.includes('salad'));
  await page.waitForTimeout(650);
  const text=await page.locator('.search-box .search-suggestions').innerText();
  results.push({id:'SEARCH-RACE-01',pass:!text.includes('KẾT QUẢ CŨ') && text.toLowerCase().includes('salad'),detail:'Phản hồi chậm cho từ khóa cũ không ghi đè truy vấn mới'});
  await input.fill('loi_goi_y_qa');
  await page.waitForFunction(()=>document.querySelector('.search-box .search-suggestion-status').textContent.includes('Chưa tải được'));
  results.push({id:'SEARCH-ERROR-01',pass:(await page.locator('.search-box .search-suggestion-status').innerText()).includes('Nhấn Enter'),detail:'Lỗi API gợi ý có thông báo và vẫn cho gửi tìm kiếm'});
 }finally{await page.unroute(pattern,handler);}
 await page.goto('http://127.0.0.1:5000/');
 return results;
}
