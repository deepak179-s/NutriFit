const CACHE_NAME='nutrifit-cache-v3';
const APP_SHELL=['/','/index.html','/nutrifit_icon.png'];

self.addEventListener('install',event=>{
  event.waitUntil(caches.open(CACHE_NAME).then(cache=>cache.addAll(APP_SHELL)));
  self.skipWaiting();
});

self.addEventListener('activate',event=>{
  event.waitUntil(
    caches.keys().then(keys=>Promise.all(keys.filter(key=>key!==CACHE_NAME).map(key=>caches.delete(key))))
  );
  self.clients.claim();
});

async function networkFirst(request){
  try{
    const response=await fetch(request);
    if(response&&response.ok&&response.type==='basic'){
      const cache=await caches.open(CACHE_NAME);
      cache.put(request,response.clone());
    }
    return response;
  }catch{
    return (await caches.match(request))||caches.match('/index.html');
  }
}

self.addEventListener('fetch',event=>{
  const request=event.request;
  if(request.method!=='GET')return;
  const url=new URL(request.url);
  if(url.origin!==self.location.origin)return;

  if(request.mode==='navigate'){
    event.respondWith(networkFirst(request));
    return;
  }

  event.respondWith(
    caches.match(request).then(cached=>cached||networkFirst(request))
  );
});
