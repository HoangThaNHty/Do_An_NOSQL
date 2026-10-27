async(page)=>{
 const results=[];const check=(id,ok,detail)=>results.push({id,pass:!!ok,detail});
 await page.setViewportSize({width:1440,height:1000});
 await page.goto('http://127.0.0.1:5000/');
 const input=page.locator('.search-box input[name=q]'), panel=page.locator('.search-box .search-suggestions');
 await input.fill('Container');await panel.locator('.search-suggestion-item').first().waitFor();
 check('SEARCH-LIVE-01',await panel.locator('.search-suggestion-item').count()===5,'Gõ Container hiện năm bài gợi ý và liên kết xem tất cả');
 const expected=await panel.locator('.search-suggestion-item').first().getAttribute('href');
 await page.screenshot({path:'.playwright-mcp/search-container-desktop.png'});
 await input.press('ArrowDown');check('SEARCH-KBD-01',await input.getAttribute('aria-activedescendant')==='search-options-0-0','Mũi tên xuống chọn kết quả đầu');
 await input.press('Enter');await page.waitForURL('**'+expected);
 check('SEARCH-KBD-02',new URL(page.url()).pathname===expected,'Enter mở bài đang chọn');
 check('ARTICLE-01',await page.locator('.article-body p').count()>=6 && (await page.locator('.article-body').innerText()).split(/\s+/).length>=260,'Bài có ít nhất sáu đoạn và nội dung dài hơn');
 await page.screenshot({path:'.playwright-mcp/article-expanded-desktop.png',fullPage:true});
 for(const q of ['contaner','cang bien','biển cảng','vận tải']){
  const r=await(await page.request.get('http://127.0.0.1:5000/api/articles/suggestions',{params:{q}})).json();
  check('SEARCH-FUZZY-'+q,r.data.total>0 && r.data.items.every(x=>x.category==='Kinh tế'),'Gần đúng: '+q);
 }
 await page.goto('http://127.0.0.1:5000/');
 await input.fill('Container');await panel.locator('.search-suggestion-item').first().waitFor();await input.press('Escape');
 check('SEARCH-CLOSE-01',await panel.isHidden() && await input.getAttribute('aria-expanded')==='false','Escape đóng danh sách');
 await input.fill('cang');await panel.locator('.search-suggestion-item').first().waitFor();await input.press('ArrowUp');
 const last=await panel.locator('.search-suggestion-item').last().getAttribute('id');
 check('SEARCH-KBD-03',await input.getAttribute('aria-activedescendant')===last,'Mũi tên lên chọn kết quả cuối khi chưa chọn');
 await page.locator('.navbar-brand').first().click();check('SEARCH-CLOSE-02',await panel.isHidden(),'Bấm ra ngoài đóng gợi ý');
 await input.fill('zzkhongcobainoqa');await page.waitForFunction(()=>document.querySelector('.search-box .search-suggestion-status').textContent.includes('Không có'));
 check('SEARCH-EMPTY-01',await panel.locator('.search-suggestion-item').count()===0,'Không có kết quả không giữ bài cũ');
 await input.fill('c');check('SEARCH-SHORT-01',await panel.isHidden(),'Một ký tự không bật danh sách');
 await input.fill('contaner');await panel.locator('.search-suggestion-item').first().waitFor();await input.press('Enter');
 await page.waitForURL('**/articles?**');
 check('SEARCH-SUBMIT-01',await page.locator('.card-news').count()>0 && (await page.locator('h1').innerText()).includes('contaner'),'Enter chưa chọn mở trang tìm kiếm gần đúng');
 const main=page.locator('main input[name=q]');
 await main.fill('cang bien');await page.locator('main .search-suggestion-item').first().waitFor();
 check('SEARCH-MAIN-01',await page.locator('main .search-suggestions').isVisible(),'Ô tìm kiếm danh sách cũng có gợi ý');
 await page.setViewportSize({width:390,height:844});await page.goto('http://127.0.0.1:5000/');
 await page.locator('.navbar-toggler').click();await input.fill('Container');await panel.locator('.search-suggestion-item').first().waitFor();
 const box=await panel.boundingBox();
 check('SEARCH-MOBILE-01',box.x>=0 && box.x+box.width<=390 && await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth),'Tìm kiếm và popup trên điện thoại không tràn màn hình');
 await page.screenshot({path:'.playwright-mcp/search-container-mobile.png'});
 return results;
}
