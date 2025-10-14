(function () {
  var PHRASE = "nie ma jeszcze żadnych ogłoszeń";
  function nuke(root){
    try{
      (root.querySelectorAll('#supa-ads-root,.supa-ads-root,[id^="supa-ads"]')||[])
        .forEach(function(el){ try{ el.remove(); }catch(e){ el.style.display='none'; }});
      var w=document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
      var n; while(n=w.nextNode()){
        var t=(n.nodeValue||"").toLowerCase();
        if(t.includes(PHRASE)) n.nodeValue="";
      }
      (root.querySelectorAll('*')||[]).forEach(function(el){ if(el.shadowRoot) nuke(el.shadowRoot);});
    }catch(_){}
  }
  function run(){ nuke(document); }
  run();
  new MutationObserver(run).observe(document.documentElement,{childList:true,subtree:true,characterData:true});
  window.addEventListener('DOMContentLoaded', run);
  window.addEventListener('load', run);
})();
