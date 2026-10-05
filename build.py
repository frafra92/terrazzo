#!/usr/bin/env python3
"""Régénère index.html, les pages de chaque table, sitemap.xml et robots.txt
à partir de tables.json. Utilisation : python3 build.py
Pour changer un prix, un texte ou une adresse : modifier tables.json, relancer, puis envoyer sur GitHub."""
import json, html, datetime, pathlib

ROOT = pathlib.Path(__file__).parent
D = json.loads((ROOT / "tables.json").read_text(encoding="utf-8"))
S = D["site"]; DIM = D["dimensions"]; TABLES = D["tables"]
BASE = S["base_url"].rstrip("/") + "/"
esc = html.escape
fr = lambda x: str(x).replace(".", ",")
TODAY = datetime.date.today().isoformat()

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
 '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
 '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500..800&family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500&family=Noto+Sans+JP:wght@600&text=%E3%83%86%E3%83%BC%E3%83%96%E3%83%AB&display=swap">')

def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace("</", "<\\/") + "</script>"

def head(title, desc, url, pfx, extra="", og_type="website", og_img="img/groupe.jpg"):
    gsc = f'<meta name="google-site-verification" content="{esc(S["search_console_token"])}">\n' if S.get("search_console_token") else ""
    return f'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
{gsc}<meta property="og:site_name" content="{S["name"]}">
<meta property="og:locale" content="fr_FR">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}{og_img}">
<meta name="twitter:card" content="summary_large_image">
{FONTS}
<link rel="stylesheet" href="{pfx}style.css">
{extra}
</head>
<body>
'''

def header(pfx):
    return f'''<header class="top">
  <div class="wrap">
    <a class="brand" href="{pfx or "./"}"><i aria-hidden="true"></i>{S["name"]}</a>
    <nav aria-label="Navigation principale">
      <a href="{pfx}#pieces">Les tables</a>
      <a href="{pfx}#sur-mesure">Sur mesure</a>
      <a href="{pfx}#contact">Contact</a>
    </nav>
  </div>
</header>
'''

FOOTER = f'''<footer><div class="wrap"><span>{S["name"]} · {S["city"]} ({S["postal_code"][:2]})</span><span>Pièces uniques, coulées et signées à la main</span></div></footer>
'''

def pied_label(t, short=False):
    base = f"pied {t['pied']}"
    return base

def pied_spec(t):
    typ = t.get("pied_type")
    return f"Pied de bistrot {typ} repeint en {t['pied']}" if typ else f"Pied de bistrot repeint en {t['pied']}"

def lang(t):
    return ' lang="ja"' if t["id"] == "teburu" else ""

def card(t):
    return f'''
  <a class="card" href="tables/{t["id"]}/" aria-label="Voir la table en terrazzo {esc(t["name"])}">
    <div class="ph"><img src="img/{t["img"]}-1.jpg" alt="{esc(t["alts"][0])}" loading="lazy" width="975" height="1300">
      <span class="tag"><i class="dot"></i>1/1 · Disponible</span></div>
    <div class="row"><h3{lang(t)}>{esc(t["name"])}</h3>
      <span class="sw"><i style="background:{t["pied_hex"]}"></i>Pied {t["pied"]}</span></div>
    <p>{esc(t["short"])}</p>
    <span class="more">Voir la pièce</span>
  </a>'''

def price_txt(t):
    return f'{t["price"]} €' if t.get("price") else "Sur demande"

def meta_desc(t):
    return (f"Table en terrazzo {t['name']}, œuvre unique coulée main à {S['city']}. Plateau Ø {fr(DIM['diametre_cm'])} cm, "
            f"pied {t['pied']}, {DIM['hauteur_cm']} cm de haut. Gravée, signée et datée.")

FAQ = [
 ("Quelles sont les dimensions des tables ?",
  f"Chaque table mesure {DIM['hauteur_cm']} cm de haut. Le plateau rond en terrazzo fait {fr(DIM['diametre_cm'])} cm de diamètre et {fr(DIM['epaisseur_cm'])} cm d'épaisseur."),
 ("Chaque table est-elle vraiment unique ?",
  "Oui. Les plateaux sont coulés à la main, avec des éclats de marbre placés pour chaque pièce. Aucun plateau n'est reproduit. Le nom, la signature et la date sont gravés au dos."),
 ("Peut-on commander une table en terrazzo sur mesure ?",
  "Oui. La couleur du plateau, les éclats de marbre, le pied, la gravure et la taille se choisissent avec vous. Appelez ou envoyez un SMS pour décrire votre projet."),
 ("Est-ce un investissement ?",
  "Chaque table est une œuvre signée, datée et en un seul exemplaire, ce qui la distingue d'un meuble de série. Je ne promets aucune plus-value : une œuvre s'achète d'abord pour la vivre chez soi."),
 ("Où est l'atelier ?",
  f"À {S['city']} ({S['postal_code']}), en Île-de-France, sur rendez-vous. Le retrait et la livraison se discutent à la commande."),
 ("Quel est le prix d'une table ?",
  "Le prix est communiqué sur demande, par téléphone ou SMS, car chaque pièce est unique."),
]

def build_home():
    body = (ROOT / "templates" / "home_body.html").read_text(encoding="utf-8")
    options = '<option value="">Choisir…</option>' + "".join(
        f'<option value="{esc(t["name"])}">{esc(t["name"])} (pied {t["pied"]})</option>' for t in TABLES
    ) + '<option value="une création sur mesure">Une création sur mesure</option>'
    faq_html = '<section class="section" id="questions"><div class="wrap"><div class="head"><p class="eyebrow">Questions</p><h2>Ce qu\'on me demande souvent</h2></div><div class="faq">' + "".join(
        f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in FAQ) + "</div></div></section>\n\n  "
    body = body.replace('<section class="section contact" id="contact">', faq_html + '<section class="section contact" id="contact">')
    body = (body.replace("{{CARDS}}", "".join(card(t) for t in TABLES))
                .replace("{{OPTIONS}}", options).replace("{{COUNT}}", str(len(TABLES))))
    phone_row = f'<div><dt>Téléphone</dt><dd><a class="num" href="tel:{S["phone_tel"]}">{S["phone_display"]}</a></dd></div>'
    body = body.replace('<dd>Orly (94), sur rendez-vous</dd></div>', '<dd>Orly (94), sur rendez-vous</dd></div>\n          ' + phone_row)
    biz = {"@context": "https://schema.org", "@type": "LocalBusiness", "name": S["name"],
           "description": "Œuvres en terrazzo coulées main : tables d'art fonctionnel, exemplaires uniques signés et datés, et créations sur mesure.",
           "url": BASE, "telephone": S["phone_tel"], "image": BASE + "img/groupe.jpg",
           "address": {"@type": "PostalAddress", "addressLocality": S["city"], "postalCode": S["postal_code"], "addressCountry": "FR"},
           "areaServed": {"@type": "AdministrativeArea", "name": "Île-de-France"}}
    if S.get("same_as"): biz["sameAs"] = S["same_as"]
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    h = head("Table terrazzo faite main, œuvre unique signée | Terrazzo François",
             "Œuvres en terrazzo coulées main à Orly : des tables d'art fonctionnel, chacune en un seul exemplaire, gravée, signée et datée. Création sur mesure.",
             BASE, "", ld(biz) + "\n" + ld(faq_ld))
    html_out = h + body.strip() + '\n\n<script src="home.js"></script>\n</body>\n</html>\n'
    (ROOT / "index.html").write_text(html_out, encoding="utf-8")

def build_table(t):
    url = f"{BASE}tables/{t['id']}/"
    pfx = "../../"
    imgs = [f"{pfx}img/{t['img']}-{i}.jpg" for i in range(1, 5)]
    title = f"Table terrazzo {t['name']}, œuvre unique pied {t['pied']} | {S['name']}"
    desc = meta_desc(t)
    prod = {"@context": "https://schema.org", "@type": "Product", "name": f"Table en terrazzo {t['name']}",
            "description": t["desc"], "image": [f"{BASE}img/{t['img']}-{i}.jpg" for i in range(1, 5)],
            "brand": {"@type": "Brand", "name": S["name"]}, "category": "Table", "material": "Terrazzo",
            "color": t["pied"], "height": {"@type": "QuantitativeValue", "value": DIM["hauteur_cm"], "unitCode": "CMT"},
            "width": {"@type": "QuantitativeValue", "value": DIM["diametre_cm"], "unitCode": "CMT"},
            "depth": {"@type": "QuantitativeValue", "value": DIM["diametre_cm"], "unitCode": "CMT"},
            "productionDate": D["date_gravure"], "url": url}
    if t.get("price"):
        prod["offers"] = {"@type": "Offer", "priceCurrency": "EUR", "price": str(t["price"]), "url": url,
                          "availability": "https://schema.org/InStock", "itemCondition": "https://schema.org/NewCondition"}
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Accueil", "item": BASE},
        {"@type": "ListItem", "position": 2, "name": "Les tables", "item": BASE + "#pieces"},
        {"@type": "ListItem", "position": 3, "name": t["name"], "item": url}]}
    spec = [("Plateau", f"Terrazzo rond coulé main. {t['plateau']}"),
            ("Dimensions", f"Ø {fr(DIM['diametre_cm'])} cm · épaisseur {fr(DIM['epaisseur_cm'])} cm · hauteur totale {DIM['hauteur_cm']} cm"),
            ("Pied", pied_spec(t)), ("Fixation", "Vissé sur une cale en bois de parquet"),
            ("Gravure", "Nom" + (f" ({t['latin']})" if t.get("latin") else "") + ", signature et date au dos"),
            ("Prix", price_txt(t)), ("Édition", "Exemplaire unique, première série"), ("Statut", "Disponible")]
    spec_html = "".join(f"<div><dt>{a}</dt><dd>{esc(b)}</dd></div>" for a, b in spec)
    part = ""
    if t.get("particularites"):
        part = '<div><p class="eyebrow">Particularités</p><ul class="part">' + "".join(f"<li>{esc(x)}</li>" for x in t["particularites"]) + "</ul></div>"
    thumbs = "".join(f'<a href="{src}" data-i="{i}" aria-label="Photo {i+1}"{" aria-current=\"true\"" if i == 0 else ""}><img src="{src}" alt="" loading="lazy" width="150" height="150"></a>' for i, src in enumerate(imgs))
    sms_body = f"Bonjour, la table terrazzo {t['name']} est-elle toujours disponible ?".replace(" ", "%20").replace(",", "%2C").replace("?", "%3F")
    others = "".join(card(o).replace('href="tables/', 'href="../').replace('src="img/', f'src="{pfx}img/') for o in TABLES if o["id"] != t["id"])
    page = head(title, desc, url, pfx, ld(prod) + "\n" + ld(crumbs), og_type="product", og_img=f"img/{t['img']}-1.jpg") + header(pfx) + f'''
<main>
  <div class="wrap">
    <nav class="crumbs" aria-label="Fil d'Ariane"><a href="{pfx}">Accueil</a> › <a href="{pfx}#pieces">Les tables</a> › {esc(t["name"])}</nav>
    <article class="tpage">
      <div class="gal">
        <img class="big" id="big" src="{imgs[0]}" alt="{esc(t["alts"][0])}" width="975" height="1300" fetchpriority="high">
        <div class="thumbs" id="thumbs">{thumbs}</div>
      </div>
      <div class="info">
        <p class="insc">ŒUVRE UNIQUE 1/1 · SIGNÉE ET DATÉE 14/07/2025</p>
        <h1{lang(t)}><span class="pre">Table en terrazzo</span>{esc(t["name"])}</h1>
        <p>{esc(t["desc"])}</p>
        <p class="artline">Art fonctionnel : elle se pose comme une table et se regarde comme une sculpture. Exemplaire unique, première série.</p>
        <dl class="spec">{spec_html}</dl>
        {part}
        <div class="ctas">
          <a class="btn primary" href="tel:{S["phone_tel"]}">Appeler</a>
          <a class="btn" href="sms:{S["phone_tel"]}?&body={sms_body}">Envoyer un SMS</a>
        </div>
        <p class="note">Ou au <span class="num">{S["phone_display"]}</span>. Atelier à {S["city"]} ({S["postal_code"][:2]}), sur rendez-vous.</p>
      </div>
    </article>
  </div>
  <section class="section">
    <div class="wrap">
      <div class="head"><p class="eyebrow">À voir aussi</p><h2>Les autres tables</h2>
        <p>Chaque table est un exemplaire unique. <a href="{pfx}#sur-mesure">Une création sur mesure</a> est aussi possible.</p></div>
      <div class="grid">{others}</div>
    </div>
  </section>
</main>
{FOOTER}
<script>
(function(){{var big=document.getElementById("big"),th=document.getElementById("thumbs");
th.addEventListener("click",function(e){{var a=e.target.closest("a");if(!a)return;e.preventDefault();
big.src=a.href;[].forEach.call(th.children,function(x){{x.removeAttribute("aria-current")}});a.setAttribute("aria-current","true");}});}})();
</script>
</body>
</html>
'''
    out = ROOT / "tables" / t["id"]; out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page, encoding="utf-8")

def build_misc():
    urls = [BASE] + [f"{BASE}tables/{t['id']}/" for t in TABLES]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
        f"  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in urls) + "</urlset>\n"
    (ROOT / "sitemap.xml").write_text(sm, encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}sitemap.xml\n", encoding="utf-8")

if __name__ == "__main__":
    build_home()
    for t in TABLES: build_table(t)
    build_misc()
    print("OK :", 1 + len(TABLES), "pages, sitemap.xml, robots.txt")
