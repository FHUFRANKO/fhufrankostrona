(()=>{ if(!location.pathname.toLowerCase().includes("ogloszenia")) return;
 const main=document.querySelector("main")||document.body; main.innerHTML="";
 const mount=document.createElement("section"); mount.id="ogloszenia-root"; main.appendChild(mount);
 const empty="nie ma jeszcze żadnych ogłoszeń";
 const isMock=x=>{ const yes=v=>v===true||v==="true"; const t=String((x&& (x.title||x.tytul)||"")).toLowerCase();
   return yes(x&&x.mock)||yes(x&&x.isMock)||yes(x&&x.fake)||yes(x&&x.test)||t.includes("mock"); };
 const render=a=>{ if(!a.length){ mount.textContent=empty; return; }
   mount.innerHTML=a.map(it=>{ const t=(it.title||it.tytul||"Ogłoszenie"); const d=(it.description||it.opis||"");
     const p=(it.price||it.cena||""); const img=(it.image||it.zdjecie);
     return "<article style="border:1px solid #eee;border-radius:12px;padding:12px;margin:8px 0;display:flex;gap:12px;align-items:flex-start">"
       +(img?("<img src=""+img+"" alt="" style="width:140px;height:100px;object-fit:cover;border-radius:8px">"):"")
       +"<div><h3 style="margin:0 0 6px 0;font-size:1.05rem">"+t+"</h3>"
       +(d?("<p style="margin:0 0 6px 0">"+d+"</p>"):"")
       +(p?("<div style="font-weight:600">"+p+"</div>"):"")
       +"</div></article>"; }).join(""); };
 fetch("ogloszenia.json?ts="+Date.now(),{cache:"no-store"})
  .then(r=>r.ok?r.json():[])
  .then(d=>{ const a=Array.isArray(d)?d:(d&&Array.isArray(d.items)?d.items:[]); render(a.filter(x=>!isMock(x))); })
  .catch(()=>render([]));
})();