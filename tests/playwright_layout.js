async(page)=>{
 const results=[];
 for(const width of [390,1440]){
  await page.setViewportSize({width,height:844});
  await page.goto('http://127.0.0.1:5000/logout');
  for(const path of ['/','/articles','/login','/register']){
   const response=await page.goto('http://127.0.0.1:5000'+path);
   results.push({id:'LAYOUT-'+width+'-'+path,path,width,pass:response.status()===200 && new URL(page.url()).pathname===path && await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth)});
  }
  await page.goto('http://127.0.0.1:5000/login');
  await page.locator('#identifier').fill('admin');await page.locator('#password').fill('123456');await page.locator('main button[type=submit]').click();
  for(const path of ['/admin/','/admin/articles','/admin/articles/create','/admin/cache','/admin/users']){
   const response=await page.goto('http://127.0.0.1:5000'+path);
   results.push({id:'LAYOUT-'+width+'-'+path,path,width,pass:response.status()===200 && new URL(page.url()).pathname===path && await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth)});
  }
 }
 await page.goto('http://127.0.0.1:5000/logout');return results;
}
