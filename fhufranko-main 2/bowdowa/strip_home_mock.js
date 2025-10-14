(function(){
  function kill(){
    var heads=[...document.querySelectorAll('h1,h2,h3')];
    var h=heads.find(x=>/Wyróżnione busy i najnowsze oferty/i.test((x.textContent||'').trim()));
    if(!h) return;
    // znajdź najbliższy <section> lub większy kontener i usuń
    var sec=h.closest('section');
    if(!sec){
      var p=h; for(let i=0;i<6 && p;i++){ if(p.tagName==='SECTION') {sec=p;break;} p=p.parentElement; }
    }
    (sec||h.parentElement)?.remove();
  }
  kill();
  new MutationObserver(kill).observe(document.documentElement,{childList:true,subtree:true});
})();
