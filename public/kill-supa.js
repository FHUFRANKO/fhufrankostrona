(function () {
  var PHRASE = "nie ma jeszcze żadnych ogłoszeń";
  function killIn(root) {
    try {
      // 1) Usuń elementy z identyfikatorami/klasami typowymi dla wtrąconych boxów
      root.querySelectorAll('#supa-ads-root,.supa-ads-root,[id^="supa-ads"]').forEach(function(el){
        try{ el.remove(); }catch(_){ el.style.display='none'; }
      });
      // 2) Usuń każdy węzeł tekstowy zawierający frazę (bez względu na białe znaki / wielkość)
      var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
      var n; while (n = walker.nextNode()) {
        var t = (n.nodeValue||"").toLowerCase().replace(/\s+/g," ").trim();
        if (!t) continue;
        if (t.includes(PHRASE)) {
          var el = n.parentElement || n;
          // jeśli to "zbłąkany" tekst w lewym górnym rogu — usuń cały kontener,
          // w innym przypadku wyczyść sam tekst (żeby nie zniknął legit komunikat w sekcji listy)
          try {
            var r = el.getBoundingClientRect ? el.getBoundingClientRect() : {top:9999,left:9999};
            if (r.top < 160 && r.left < 160) { el.remove(); }
            else { n.nodeValue = ""; }
          } catch(_) { n.nodeValue = ""; }
        }
      }
      // 3) Shadow DOM (gdyby ktoś wstrzyknął w shadow-root)
      (root.querySelectorAll('*')||[]).forEach(function(el){
        if (el.shadowRoot) killIn(el.shadowRoot);
      });
    } catch (_){}
  }
  function run(){ killIn(document); }
  // start bardzo wcześnie i re-reakcja na mutacje
  run();
  new MutationObserver(run).observe(document.documentElement, {childList:true, subtree:true, characterData:true});
  window.addEventListener('DOMContentLoaded', run, {once:false});
  window.addEventListener('load', run, {once:false});
})();
