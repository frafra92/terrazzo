const CONTACT = { phone:"07 83 92 58 94", email:"", instagram:"" };
const $ = s => document.querySelector(s);
/* coordonnées affichées seulement si renseignées */
const rows = [];
if(CONTACT.phone) rows.length = 0; /* le téléphone est déjà dans la page */
if(CONTACT.email) rows.push(["E-mail",CONTACT.email]);
if(CONTACT.instagram) rows.push(["Instagram",CONTACT.instagram]);
$("#dl").insertAdjacentHTML("beforeend", rows.map(([a,b])=>`<div><dt>${a}</dt><dd>${b}</dd></div>`).join(""));

/* formulaire : prépare le message, à copier ou ouvrir */
$("#form").addEventListener("submit",e=>{
  e.preventDefault();
  const nom=$("#nom").value.trim(), coord=$("#coord").value.trim(), piece=$("#piece").value, msg=$("#msg").value.trim();
  const txt = `Bonjour François,\nJe m'intéresse à ${piece||"vos tables en terrazzo"}.\n${msg?msg+"\n":""}\n${nom||""}${coord?" · "+coord:""}`.trim();
  const out=$("#out"); out.hidden=false;
  const links=[];
  if(CONTACT.email) links.push(`<a class="btn" href="mailto:${CONTACT.email}?subject=${encodeURIComponent("Terrazzo François : "+(piece||"demande"))}&body=${encodeURIComponent(txt)}">Ouvrir dans mon e-mail</a>`);
  if(CONTACT.phone) links.push(`<a class="btn" href="sms:${CONTACT.phone.replace(/\s/g,"")}?&body=${encodeURIComponent(txt)}">Ouvrir dans mes SMS</a>`);
  out.innerHTML = `<strong>Votre message est prêt</strong><pre id="pre"></pre>
    <div class="acts"><button type="button" class="btn primary" id="copy">Copier le message</button>${links.join("")}<small id="cs"></small></div>
    <small>Rien n'est envoyé depuis cette page. Copiez le message et envoyez-le par SMS ou e-mail${" au numéro ci-contre"}.</small>`;
  $("#pre").textContent = txt;
  $("#copy").onclick = async ()=>{
    try{ await navigator.clipboard.writeText(txt); $("#cs").textContent="Copié"; }
    catch(_){ const r=document.createRange(); r.selectNodeContents($("#pre")); const s=getSelection(); s.removeAllRanges(); s.addRange(r); $("#cs").textContent="Texte sélectionné, copiez-le"; }
  };
});

/* champ d'éclats de terrazzo (hero) */
(function(){
  const cv=$("#chips"), ctx=cv.getContext("2d");
  const pal=["#2DBE78","#E2A21B","#1B1C1E","#B7BDC4","#C2492F","#D8A57C","#F1F1EE"];
  let seed=14072025; const rnd=()=>{seed=(seed*1664525+1013904223)%4294967296;return seed/4294967296};
  function draw(){
    const r=cv.parentElement.getBoundingClientRect(), d=Math.min(devicePixelRatio||1,2);
    cv.width=r.width*d; cv.height=r.height*d; ctx.setTransform(d,0,0,d,0,0);
    seed=14072025; const n=Math.round(r.width*r.height/2600);
    for(let i=0;i<n;i++){
      const x=rnd()*r.width,y=rnd()*r.height,s=5+Math.pow(rnd(),2.4)*70,k=5+Math.floor(rnd()*3),rot=rnd()*6.28;
      ctx.fillStyle=pal[Math.floor(Math.pow(rnd(),1.3)*pal.length)];
      ctx.beginPath();
      for(let j=0;j<k;j++){const a=rot+j/k*6.283,rr=s*(.55+rnd()*.5);ctx.lineTo(x+Math.cos(a)*rr,y+Math.sin(a)*rr*.8)}
      ctx.closePath();ctx.fill();
    }
  }
  draw(); let t; addEventListener("resize",()=>{clearTimeout(t);t=setTimeout(draw,150)});
})();
