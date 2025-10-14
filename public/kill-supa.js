(function(){
  var TEXT = "nie ma jeszcze żadnych ogłoszeń";
  function nuke(){
    // usuń wstrzyknięty element (różne warianty selektorów)
    document.querySelectorAll('#supa-ads-root,.supa-ads-root,[id^="supa-ads"]').forEach(function(el){
      try{ el.remove(); }catch(e){ el.style.display = 'none'; }
    });
    // usuń ewentualny „goły” textNode
    try{
      var w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      var n; while(n = w.nextNode()){
        if(n.nodeValue && n.nodeValue.trim() === TEXT){ n.nodeValue = ''; }
      }
    }catch(_){}
  }
  nuke();
  new MutationObserver(nuke).observe(document.documentElement,{childList:true,subtree:true});
})();
