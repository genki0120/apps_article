from pathlib import Path
import re, json, html, os
from xml.etree import ElementTree as ET

BASE='https://god-apps-article.com'
TODAY='2026-09-12'
ROOT=Path('.')

# ---------- helpers ----------
def add_before_head_close(s, block, marker):
    if marker in s:
        return s
    return s.replace('</head>', block+'\n</head>', 1)

def add_after_header(s, block, marker):
    if marker in s:
        return s
    return re.sub(r'</header>\s*<main>', '</header>'+block+'<main>', s, count=1)

def breadcrumb_html(items, cls='breadcrumb-wrap'):
    links=[]
    for i,(name,url) in enumerate(items):
        if i==len(items)-1 or not url:
            links.append(f'<span aria-current="page">{html.escape(name)}</span>')
        else:
            links.append(f'<a href="{url}">{html.escape(name)}</a>')
    return f'<div class="container {cls}"><nav class="breadcrumb" aria-label="パンくず">'+ '<span class="breadcrumb-home">TENKI</span><span class="breadcrumb-sep">/</span>'.join([]) + ('<span class="breadcrumb-sep"> / </span>'.join(links)) + '</nav></div>'

def breadcrumb_schema(items):
    els=[]
    for i,(name,url) in enumerate(items,1):
        el={'@type':'ListItem','position':i,'name':name}
        if url: el['item']=BASE+url if url.startswith('/') else url
        els.append(el)
    return {'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':els}

def walk_schema(obj, fn):
    if isinstance(obj, dict):
        fn(obj)
        for v in obj.values(): walk_schema(v, fn)
    elif isinstance(obj, list):
        for v in obj: walk_schema(v, fn)

def patch_jsonld(s, mutator):
    pat=re.compile(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', re.S)
    changed=False
    def repl(m):
        nonlocal changed
        raw=m.group(1)
        try:
            obj=json.loads(raw)
        except Exception:
            return m.group(0)
        before=json.dumps(obj,ensure_ascii=False,sort_keys=True)
        walk_schema(obj, mutator)
        after=json.dumps(obj,ensure_ascii=False,sort_keys=True)
        if before!=after: changed=True
        return '<script type="application/ld+json">'+json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'</script>'
    return pat.sub(repl,s),changed

def seo_head_block(og_path, lang='ja_JP'):
    return f'''<!-- TENKI A SEO -->
<link rel="icon" href="/assets/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="/assets/tenki-logo.png">
<meta property="og:image" content="{BASE}{og_path}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{BASE}{og_path}">
<!-- /TENKI A SEO -->'''

def append_schema(s,obj,marker):
    if marker in s: return s
    block=f'\n<!-- {marker} --><script type="application/ld+json">'+json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'</script>'
    return s.replace('</head>',block+'\n</head>',1)

def replace_twitter_card(s):
    return re.sub(r'<meta name="twitter:card" content="[^"]+">','<meta name="twitter:card" content="summary_large_image">',s)

# ---------- shared styles ----------
guide=Path('guide.css')
gcss=guide.read_text()
extra='''
/* A-tier SEO / navigation polish */
.breadcrumb-wrap{padding-top:15px}.breadcrumb{display:flex;align-items:center;flex-wrap:wrap;gap:8px;font-size:10px;font-weight:850;color:var(--muted);letter-spacing:.04em}.breadcrumb a{transition:.2s}.breadcrumb a:hover{color:var(--ink)}.breadcrumb-sep{opacity:.45}.article-meta{display:flex;gap:10px 18px;flex-wrap:wrap;align-items:center;margin:-18px 0 34px;padding:13px 16px;border:1px solid var(--line);border-radius:16px;background:rgba(255,255,255,.35);font-size:11px;color:var(--muted)}.article-meta a{font-weight:950;color:var(--ink)}.article-meta time{margin-left:auto}.author-note{margin-top:54px;padding:22px 24px;border:1px solid var(--line);border-radius:20px;background:var(--paper);display:grid;grid-template-columns:54px 1fr;gap:16px;align-items:center}.author-mark{width:54px;height:54px;border-radius:16px;background:var(--dark);color:var(--lime);display:grid;place-items:center;font-weight:950;font-size:20px}.author-note b{display:block;margin-bottom:4px}.author-note p{margin:0;color:var(--muted);font-size:12px}.article-list{display:grid;gap:12px}.article-link{display:grid;grid-template-columns:110px 1fr 30px;gap:16px;align-items:center;padding:20px;border:1px solid var(--line);border-radius:20px;background:var(--paper);transition:.2s}.article-link:hover{transform:translateY(-2px);box-shadow:var(--shadow)}.article-link small{font-size:9px;font-weight:950;color:var(--muted);letter-spacing:.1em}.article-link b{font-size:18px}.article-link i{font-style:normal;font-size:22px}.checklist{display:grid;gap:10px}.checkitem{padding:18px 20px 18px 52px;border:1px solid var(--line);border-radius:18px;background:var(--paper);position:relative}.checkitem:before{content:"✓";position:absolute;left:19px;top:16px;width:24px;height:24px;border-radius:50%;background:var(--lime);display:grid;place-items:center;font-size:12px;font-weight:950}.checkitem b{display:block;margin-bottom:4px}.checkitem p{margin:0;color:var(--muted);font-size:13px}.cost-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}.cost-item{padding:23px;border:1px solid var(--line);border-radius:22px;background:var(--paper)}.cost-item small{font-size:9px;font-weight:950;color:var(--muted)}.cost-item h3{margin:12px 0 7px;font-size:21px}.cost-item p{margin:0;color:var(--muted);font-size:13px}@media(max-width:700px){.article-meta time{margin-left:0}.author-note{grid-template-columns:1fr}.article-link{grid-template-columns:1fr 26px}.article-link small{grid-column:1/-1}.cost-grid{grid-template-columns:1fr}}
'''
if 'A-tier SEO / navigation polish' not in gcss:
    guide.write_text(gcss+extra)

# localized product CSS
Path('localized-product.css').write_text(''':root{--bg:#f4f1ea;--paper:#fbfaf6;--ink:#101416;--muted:#5f6668;--line:rgba(16,20,22,.14);--dark:#0a0d0f;--lime:#c8ff36;--accent:#6ce5e8;--max:1080px}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:Inter,"Noto Sans",Arial,sans-serif;line-height:1.75}a{color:inherit;text-decoration:none}.wrap{width:min(calc(100% - 38px),var(--max));margin:auto}.top{border-bottom:1px solid var(--line);background:rgba(244,241,234,.92);position:sticky;top:0;z-index:20;backdrop-filter:blur(14px)}.nav{height:70px;display:flex;align-items:center;justify-content:space-between}.brand{font-weight:950}.back{font-size:12px;font-weight:900}.crumb{padding:16px 0;font-size:11px;color:var(--muted)}.hero{padding:70px 0 80px;position:relative;overflow:hidden}.hero:before{content:"";position:absolute;width:380px;height:380px;border-radius:50%;background:var(--accent);opacity:.16;right:-150px;top:-170px}.eyebrow{font-size:11px;font-weight:950;letter-spacing:.14em;text-transform:uppercase}.hero h1{font-size:clamp(52px,8vw,94px);line-height:.95;letter-spacing:-.06em;margin:18px 0 22px;max-width:820px}.hero p{max-width:700px;font-size:18px;color:#343b3d}.buttons{display:flex;gap:10px;flex-wrap:wrap;margin-top:26px}.btn{padding:12px 17px;border:1px solid var(--ink);border-radius:999px;font-size:12px;font-weight:950}.btn.primary{background:var(--dark);color:#fff}.section{padding:72px 0}.head{display:grid;grid-template-columns:.8fr 1.2fr;gap:34px;align-items:end;margin-bottom:26px}.head h2{font-size:clamp(34px,5vw,54px);line-height:1.05;letter-spacing:-.04em;margin:0}.head p{color:var(--muted);margin:0}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:13px}.card{padding:25px;border:1px solid var(--line);border-radius:24px;background:var(--paper);min-height:220px}.card span{font-size:10px;font-weight:950;color:var(--muted)}.card h3{font-size:23px;margin:30px 0 8px}.card p{font-size:13px;color:var(--muted);margin:0}.cta{margin:60px auto 90px;padding:38px;background:var(--dark);color:#fff;border-radius:30px}.cta h2{font-size:40px;line-height:1.05;margin:0 0 10px}.cta p{color:#adb6b7}.cta a{display:inline-flex;margin-top:12px;padding:12px 16px;border-radius:999px;background:var(--lime);color:#0a0d0f;font-weight:950}.langs{display:flex;gap:8px;font-size:11px;font-weight:900}.langs a{padding:6px 9px;border-radius:99px;border:1px solid var(--line)}.langs .on{background:var(--dark);color:#fff}.jor{--accent:#e9b948}.sake{--accent:#d8ad55;background:#11110f;color:#f4f0e4}.sake .top{background:rgba(13,13,11,.92);border-color:rgba(244,240,228,.14)}.sake .crumb,.sake .head p,.sake .card p{color:#aaa492}.sake .card{background:#181713;border-color:rgba(244,240,228,.14)}.sake .btn{border-color:#d8ad55}.sake .btn.primary{background:#d8ad55;color:#17140e}.sake .cta{background:#1b1a16}.cal{--accent:#ff8a4c}@media(max-width:760px){.head,.cards{grid-template-columns:1fr}.hero{padding-top:50px}}
''')

# ---------- assets placeholders (PNGs generated later in workflow) ----------
assets=Path('assets'); assets.mkdir(exist_ok=True)
Path('assets/tenki-logo.svg').write_text('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><rect width="512" height="512" rx="128" fill="#0a0d0f"/><circle cx="384" cy="126" r="46" fill="#c8ff36"/><path d="M112 150h288v42H112zm38 82h212v42H150zm48 82h116v42H198z" fill="#f4f1ea"/></svg>''')

# ---------- patch index ----------
p=Path('index.html'); s=p.read_text()
s=replace_twitter_card(s)
s=add_before_head_close(s, seo_head_block('/assets/og/tenki.png'), 'TENKI A SEO')
def org_mut(d):
    t=d.get('@type')
    if t=='Organization' and d.get('name')=='テンキ':
        d['logo']=BASE+'/assets/tenki-logo.png'
        d['contactPoint']={'@type':'ContactPoint','contactType':'business inquiries','email':'igagenki@outlook.com','availableLanguage':['ja','en']}
s,_=patch_jsonld(s,org_mut)
# minimal extra links under knowledge cards
if 'guide-extra-links' not in s:
    start=s.find('<section class="section" id="guide">')
    if start!=-1:
        end=s.find('</section>',start)
        seg=s[start:end]
        pos=seg.rfind('</div>')
        if pos!=-1:
            insert='''\n    <div class="guide-extra-links"><span>導入ガイド</span><a href="/ai-agent-cost.html">費用の考え方 ↗</a><a href="/ai-agent-implementation.html">導入の進め方 ↗</a><a href="/ai-agent-failure.html">失敗を防ぐ ↗</a><a href="/generative-ai-business-efficiency.html">業務効率化 ↗</a><a href="/ai-agent-security-governance.html">セキュリティと運用 ↗</a></div>\n'''
            seg=seg[:pos]+insert+seg[pos:]
            s=s[:start]+seg+s[end:]
p.write_text(s)

# tenki CSS homepage strip
p=Path('tenki.css'); css=p.read_text()
if '.guide-extra-links' not in css:
    css+='''\n.guide-extra-links{margin-top:16px;padding:16px 18px;border:1px solid var(--line);border-radius:18px;background:rgba(255,255,255,.34);display:flex;align-items:center;gap:10px 16px;flex-wrap:wrap}.guide-extra-links>span{font-size:10px;font-weight:950;letter-spacing:.12em;color:var(--muted);margin-right:4px}.guide-extra-links a{font-size:12px;font-weight:900;text-decoration:underline;text-decoration-color:rgba(16,20,22,.22);text-underline-offset:4px}.guide-extra-links a:hover{text-decoration-color:var(--ink)}\n'''
    p.write_text(css)

# ---------- patch existing article pages ----------
article_pages={
'ai-agent.html':('AI Agentとは','/assets/og/ai-agent.png'),
'copilot-studio.html':('Copilot Studioとは','/assets/og/copilot-studio.png'),
'dify.html':('Difyとは','/assets/og/dify.png'),
'copilot-studio-vs-dify.html':('Copilot StudioとDifyの比較','/assets/og/copilot-vs-dify.png'),
'rag.html':('RAGとは','/assets/og/rag.png'),
'ai-agent-poc.html':('AI Agent PoCの進め方','/assets/og/ai-agent-poc.png'),
}
for filename,(crumb,og) in article_pages.items():
    p=Path(filename); s=p.read_text(); s=replace_twitter_card(s)
    s=add_before_head_close(s,seo_head_block(og),'TENKI A SEO')
    bc=breadcrumb_html([('Home','/'),('Knowledge','/#guide'),(crumb,None)])
    s=add_after_header(s,bc,'breadcrumb-wrap')
    if 'class="article-meta"' not in s:
        meta=f'<div class="article-meta"><span>執筆：<a href="/about.html">テンキ</a></span><span>AI Agent導入・業務AI化支援</span><time datetime="{TODAY}">更新 {TODAY.replace("-",".")}</time></div>'
        s=s.replace('<article class="container article">','<article class="container article">'+meta,1)
    if 'class="author-note"' not in s:
        author='''<div class="author-note"><div class="author-mark">天</div><div><b>執筆：テンキ</b><p>AI Agentを実際の企業業務へ組み込むための業務整理・試作・評価・運用改善を支援しています。<a href="/about.html"><strong>テンキについて ↗</strong></a></p></div></div>'''
        s=s.replace('<section class="cta">',author+'<section class="cta">',1)
    def art_mut(d,og=og):
        if d.get('@type') in ('Article','BlogPosting','NewsArticle'):
            d['image']=[BASE+og]
            d['dateModified']=TODAY
            d.setdefault('datePublished',TODAY)
            d['author']={'@type':'Organization','name':'テンキ','url':BASE+'/about.html'}
            d['publisher']={'@type':'Organization','name':'テンキ','url':BASE+'/','logo':{'@type':'ImageObject','url':BASE+'/assets/tenki-logo.png'}}
    s,_=patch_jsonld(s,art_mut)
    s=append_schema(s,breadcrumb_schema([('Home','/'),('Knowledge','/#guide'),(crumb,None)]),'TENKI BREADCRUMB')
    p.write_text(s)

# about and case studies: breadcrumb + social images + logo schema
for filename,crumb,og in [('about.html','テンキについて','/assets/og/about.png'),('case-studies.html','企業向け支援実績','/assets/og/case-studies.png')]:
    p=Path(filename); s=p.read_text(); s=replace_twitter_card(s)
    s=add_before_head_close(s,seo_head_block(og),'TENKI A SEO')
    s=add_after_header(s,breadcrumb_html([('Home','/'),(crumb,None)]),'breadcrumb-wrap')
    s=append_schema(s,breadcrumb_schema([('Home','/'),(crumb,None)]),'TENKI BREADCRUMB')
    if filename=='about.html':
        s,_=patch_jsonld(s,org_mut)
    p.write_text(s)

# ---------- patch original product pages ----------
products={
'jor':{'file':'products/jor.html','ja_title':'JOR｜手元の食材から日本の家庭料理を提案するAIレシピアプリ','ja_desc':'JORは、手元の食材から日本の家庭料理を見つけ、作るまでを支えるレシピプロダクトです。食材の認識、料理候補、調理の流れを一つにつなぎます。','og':'/products/assets/og-jor.png','cat':'LifestyleApplication'},
'sakepicks':{'file':'products/sakepicks.html','ja_title':'Sake Picks｜日本酒を知る・投票する・追う参加型アプリ','ja_desc':'Sake Picksは、日本酒を知り、Electionで投票し、結果やDrop、レビューまで追える参加型の日本酒発見プロダクトです。','og':'/products/assets/og-sakepicks.png','cat':'LifestyleApplication'},
'calcal':{'file':'products/calcal.html','ja_title':'Cal×Cal｜食事写真からカロリーとPFCを解析するAI栄養管理アプリ','ja_desc':'Cal×Calは、食事写真からカロリーとPFCを解析し、日々の栄養バランスを確認できるAI栄養管理プロダクトです。','og':'/products/assets/og-calcal.png','cat':'HealthApplication'},
}
for slug,d in products.items():
    p=Path(d['file']); s=p.read_text()
    s=re.sub(r'<title>.*?</title>',f'<title>{d["ja_title"]}</title>',s,count=1,flags=re.S)
    s=re.sub(r'<meta name="description" content="[^"]*">',f'<meta name="description" content="{d["ja_desc"]}">',s,count=1)
    s=replace_twitter_card(s)
    # add favicon/social image if not present
    s=add_before_head_close(s,seo_head_block(d['og']),'TENKI A SEO')
    # hreflang
    if 'hreflang="en"' not in s:
        hre=f'''<link rel="alternate" hreflang="ja" href="{BASE}/products/{slug}.html">\n<link rel="alternate" hreflang="en" href="{BASE}/en/products/{slug}.html">\n<link rel="alternate" hreflang="es" href="{BASE}/es/products/{slug}.html">\n<link rel="alternate" hreflang="x-default" href="{BASE}/products/{slug}.html">'''
        s=s.replace('</head>',hre+'\n</head>',1)
    # update existing og description/title/image
    s=re.sub(r'<meta property="og:title" content="[^"]*">',f'<meta property="og:title" content="{d["ja_title"]}">',s,count=1)
    s=re.sub(r'<meta property="og:description" content="[^"]*">',f'<meta property="og:description" content="{d["ja_desc"]}">',s,count=1)
    # visible breadcrumb
    crumb=breadcrumb_html([('Home','/'),('Product','/#product'),(slug.upper() if slug!='sakepicks' else 'Sake Picks',None)],'product-breadcrumb-wrap')
    s=add_after_header(s,crumb,'product-breadcrumb-wrap')
    # local product breadcrumb styles inside inline css
    if '.product-breadcrumb-wrap' not in s:
        pass
    style='''<style>.product-breadcrumb-wrap{width:min(calc(100% - 40px),1160px);margin:0 auto;padding-top:91px;margin-bottom:-66px;position:relative;z-index:4}.product-breadcrumb-wrap .breadcrumb{display:flex;gap:8px;flex-wrap:wrap;font-size:10px;font-weight:850;opacity:.68}.product-breadcrumb-wrap .breadcrumb-sep{opacity:.5}@media(max-width:560px){.product-breadcrumb-wrap{width:min(calc(100% - 26px),1160px);padding-top:88px;margin-bottom:-60px}}</style>'''
    if 'padding-top:91px' not in s: s=s.replace('</head>',style+'\n</head>',1)
    s=append_schema(s,breadcrumb_schema([('Home','/'),('Product','/#product'),(slug.upper() if slug!='sakepicks' else 'Sake Picks',None)]),'TENKI BREADCRUMB')
    # enrich app publisher logo and description
    def app_mut(x,d=d):
        if x.get('@type') in ('MobileApplication','SoftwareApplication'):
            x['description']=d['ja_desc']; x['image']=BASE+d['og']
            if isinstance(x.get('publisher'),dict): x['publisher']['logo']=BASE+'/assets/tenki-logo.png'
    s,_=patch_jsonld(s,app_mut)
    p.write_text(s)

# ---------- localized product pages ----------
loc_copy={
'jor':{
'en':{'name':'JOR','title':'JOR | Turn Ingredients into Japanese Home Cooking','desc':'JOR helps you turn ingredients you already have into Japanese home-cooking ideas and a simple cooking flow.','eyebrow':'Japanese Home Cooking','h1':'From what you have to what you can cook','lead':'JOR helps you discover approachable Japanese home-cooking ideas from ingredients already in your kitchen.','cards':[('01 / SEE','Start with what you have','Use the ingredients already available instead of starting from a long recipe search.'),('02 / CHOOSE','Compare a few ideas','See several Japanese home-cooking directions and choose what fits your mood and time.'),('03 / COOK','Move into cooking','Follow a clear path from ingredients to a dish you can actually make.')],'cta':'Explore the original JOR product page'},
'es':{'name':'JOR','title':'JOR | Convierte tus ingredientes en cocina casera japonesa','desc':'JOR te ayuda a convertir los ingredientes que ya tienes en ideas de cocina casera japonesa y un flujo sencillo para cocinar.','eyebrow':'Cocina casera japonesa','h1':'De lo que tienes a lo que puedes cocinar','lead':'JOR propone ideas accesibles de cocina casera japonesa a partir de los ingredientes que ya tienes en casa.','cards':[('01 / VER','Empieza con lo que tienes','Parte de los ingredientes disponibles sin tener que buscar entre muchas recetas.'),('02 / ELEGIR','Compara varias ideas','Mira varias opciones de cocina japonesa y elige la que encaje con tu tiempo y preferencias.'),('03 / COCINAR','Pasa a cocinar','Sigue un camino claro desde los ingredientes hasta un plato que realmente puedas preparar.')],'cta':'Ver la página original de JOR'}},
'sakepicks':{
'en':{'name':'Sake Picks','title':'Sake Picks | Discover, Vote and Follow Japanese Sake','desc':'Sake Picks is a participatory way to discover Japanese sake, vote in Elections and follow results, drops and reviews.','eyebrow':'Sake Election / Discovery','h1':'Discover · Vote · Follow','lead':'Sake Picks turns sake discovery into a participatory experience: learn about selections, vote, and keep following what happens next.','cards':[('01 / DISCOVER','Discover selections','Start from curated sake selections and learn what makes each bottle interesting.'),('02 / VOTE','Cast your vote','Take part in Elections instead of only reading someone else’s ranking.'),('03 / FOLLOW','Follow what happens next','Continue from the result into drops, reviews and community activity.')],'cta':'Explore the original Sake Picks page'},
'es':{'name':'Sake Picks','title':'Sake Picks | Descubre, vota y sigue el sake japonés','desc':'Sake Picks es una forma participativa de descubrir sake japonés, votar en Elections y seguir resultados, drops y reseñas.','eyebrow':'Elección / Descubrimiento de sake','h1':'Descubrir · Votar · Seguir','lead':'Sake Picks convierte el descubrimiento del sake en una experiencia participativa: conoce opciones, vota y sigue lo que ocurre después.','cards':[('01 / DESCUBRIR','Descubre opciones','Empieza por selecciones de sake y conoce qué hace interesante a cada botella.'),('02 / VOTAR','Emite tu voto','Participa en Elections en lugar de limitarte a leer el ranking de otra persona.'),('03 / SEGUIR','Sigue lo que ocurre','Continúa desde el resultado hacia drops, reseñas y actividad de la comunidad.')],'cta':'Ver la página original de Sake Picks'}},
'calcal':{
'en':{'name':'Cal×Cal','title':'Cal×Cal | Understand Calories and Macros from a Meal Photo','desc':'Cal×Cal turns a meal photo into an easy view of calories, protein, fat and carbohydrates for everyday nutrition tracking.','eyebrow':'AI Nutrition','h1':'Snap · Understand · Adjust','lead':'Cal×Cal helps you understand a meal at a glance and compare it with your daily nutrition goals.','cards':[('01 / SNAP','Start with a meal photo','Use a meal photo as the starting point instead of entering every food by hand.'),('02 / UNDERSTAND','See the nutrition picture','Review calories and the balance of protein, fat and carbohydrates in one place.'),('03 / ADJUST','Adjust the rest of the day','Use the result as a guide for later meals rather than treating one meal in isolation.')],'cta':'Explore the original Cal×Cal page'},
'es':{'name':'Cal×Cal','title':'Cal×Cal | Entiende calorías y macros desde una foto de comida','desc':'Cal×Cal convierte una foto de comida en una vista sencilla de calorías, proteínas, grasas y carbohidratos para el seguimiento diario.','eyebrow':'Nutrición con IA','h1':'Foto · Entender · Ajustar','lead':'Cal×Cal te ayuda a entender una comida de un vistazo y compararla con tus objetivos diarios de nutrición.','cards':[('01 / FOTO','Empieza con una foto','Usa una foto de la comida en lugar de introducir cada alimento manualmente.'),('02 / ENTENDER','Mira el equilibrio nutricional','Consulta calorías y el balance de proteínas, grasas y carbohidratos en un solo lugar.'),('03 / AJUSTAR','Ajusta el resto del día','Usa el resultado como guía para las siguientes comidas, no como una valoración aislada.')],'cta':'Ver la página original de Cal×Cal'}},
}

def local_product(slug,lang,c):
    bodyclass='jor' if slug=='jor' else ('sake' if slug=='sakepicks' else 'cal')
    og=products[slug]['og']
    altlinks=f'''<link rel="alternate" hreflang="ja" href="{BASE}/products/{slug}.html"><link rel="alternate" hreflang="en" href="{BASE}/en/products/{slug}.html"><link rel="alternate" hreflang="es" href="{BASE}/es/products/{slug}.html"><link rel="alternate" hreflang="x-default" href="{BASE}/products/{slug}.html">'''
    canonical=f'{BASE}/{lang}/products/{slug}.html'
    cards=''.join(f'<article class="card"><span>{a}</span><h3>{b}</h3><p>{d}</p></article>' for a,b,d in c['cards'])
    crumbs=[('Home','/'),('Product','/#product'),(c['name'],None)]
    schemas=[{'@context':'https://schema.org','@type':'WebPage','name':c['title'],'url':canonical,'inLanguage':lang},breadcrumb_schema(crumbs)]
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{c['title']}</title><meta name="description" content="{c['desc']}"><meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="{canonical}">{altlinks}<link rel="icon" href="/assets/favicon.png" type="image/png"><meta property="og:type" content="website"><meta property="og:title" content="{c['title']}"><meta property="og:description" content="{c['desc']}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{BASE}{og}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{BASE}{og}"><link rel="stylesheet" href="/localized-product.css"><script type="application/ld+json">{json.dumps(schemas,ensure_ascii=False,separators=(',',':'))}</script></head><body class="{bodyclass}"><header class="top"><div class="wrap nav"><a class="brand" href="/">TENKI</a><div class="langs"><a href="/products/{slug}.html">JA</a><a class="{'on' if lang=='en' else ''}" href="/en/products/{slug}.html">EN</a><a class="{'on' if lang=='es' else ''}" href="/es/products/{slug}.html">ES</a></div></div></header><div class="wrap crumb"><a href="/">TENKI</a> / Product / {c['name']}</div><main><section class="hero"><div class="wrap"><div class="eyebrow">{c['eyebrow']}</div><h1>{c['h1']}</h1><p>{c['lead']}</p><div class="buttons"><a class="btn primary" href="/products/{slug}.html">{c['cta']} ↗</a><a class="btn" href="/">TENKI ↗</a></div></div></section><section class="section"><div class="wrap"><div class="head"><h2>{'How it works' if lang=='en' else 'Cómo funciona'}</h2><p>{c['desc']}</p></div><div class="cards">{cards}</div></div></section><section class="wrap cta"><h2>{c['name']}</h2><p>{c['lead']}</p><a href="/products/{slug}.html">{c['cta']} ↗</a></section></main></body></html>'''

for slug,langs in loc_copy.items():
    for lang,c in langs.items():
        out=Path(lang)/'products'/f'{slug}.html'; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(local_product(slug,lang,c))

# ---------- new business/security articles ----------
def new_article(slug,title,desc,eyebrow,h1,lead,side_title,side_body,body_html,sources,related):
    og=f'/assets/og/{slug}.png'; url=f'{BASE}/{slug}.html'
    source_html=''.join(f'<a href="{u}"><span>{html.escape(n)}</span><b>↗</b></a>' for n,u in sources)
    related_html=''.join(f'<a href="{u}"><span>{tag}</span>{html.escape(n)}</a>' for tag,n,u in related)
    schema={'@context':'https://schema.org','@type':'Article','headline':title,'description':desc,'image':[BASE+og],'datePublished':TODAY,'dateModified':TODAY,'author':{'@type':'Organization','name':'テンキ','url':BASE+'/about.html'},'publisher':{'@type':'Organization','name':'テンキ','url':BASE+'/','logo':{'@type':'ImageObject','url':BASE+'/assets/tenki-logo.png'}},'mainEntityOfPage':url}
    crumbs=[('Home','/'),('Knowledge','/#guide'),(title.split('｜')[0],None)]
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><meta name="description" content="{desc}"><meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="{url}"><link rel="icon" href="/assets/favicon.png" type="image/png"><meta property="og:type" content="article"><meta property="og:locale" content="ja_JP"><meta property="og:site_name" content="テンキ"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="{url}"><meta property="og:image" content="{BASE}{og}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{BASE}{og}"><link rel="stylesheet" href="/guide.css?v=20260912-a"><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False,separators=(',',':'))}</script><script type="application/ld+json">{json.dumps(breadcrumb_schema(crumbs),ensure_ascii=False,separators=(',',':'))}</script></head><body><header class="site-header"><div class="container nav"><a class="brand" href="/"><span class="brand-mark">天</span><span class="brand-copy"><strong>テンキ</strong><span>AI AGENT / BUSINESS AI</span></span></a><nav class="nav-links"><a href="/ai-agent.html">AI Agent</a><a href="/case-studies.html">Case Study</a><a href="/about.html">About</a><a class="nav-cta" href="/contact.html">Contact ↗</a></nav></div></header>{breadcrumb_html(crumbs)}<main><section class="hero"><div class="container hero-grid"><div><div class="eyebrow">{eyebrow}</div><h1>{h1}</h1><p class="hero-lead">{lead}</p></div><aside class="hero-side"><small>POINT</small><strong>{side_title}</strong><p>{side_body}</p></aside></div></section><article class="container article"><div class="article-meta"><span>執筆：<a href="/about.html">テンキ</a></span><span>AI Agent導入・業務AI化支援</span><time datetime="{TODAY}">更新 {TODAY.replace('-','.')}</time></div>{body_html}<section class="sources"><h2>参考にした公式情報</h2><div class="source-list">{source_html}</div></section><section class="related"><h2>関連ページ</h2><div class="related-grid">{related_html}</div></section><div class="author-note"><div class="author-mark">天</div><div><b>執筆：テンキ</b><p>AI Agent導入を技術だけでなく、業務・評価・運用まで含めて支援しています。<a href="/about.html"><strong>テンキについて ↗</strong></a></p></div></div><section class="cta"><h2>自社の業務に合わせて<br>整理する</h2><p>まだ製品や要件が決まっていない段階から、対象業務・評価方法・運用条件を整理できます。</p><a href="/contact.html">相談する ↗</a></section></article></main><footer class="footer"><div class="container footer-inner"><span>© TENKI</span><span><a href="/">Home</a>　<a href="/about.html">About</a></span></div></footer></body></html>'''

security_body='''<p class="intro">AI Agentを社内で使うとき、最初に考えるべきことは「AIは安全か」という抽象的な問いではありません。誰が使うのか、どの情報まで見せるのか、どこまで操作を任せるのか、問題が起きたとき誰が止めるのかを決めることです。Microsoftの企業向けガイダンスでも、データの範囲、利用者の権限、接続先、開発・テスト・本番の分離、公開前の確認を運用ルールとして設計することが重視されています。</p><section class="section"><div class="section-head"><div><div class="eyebrow">Six decisions</div><h2>導入前に決める<br>6つのこと</h2></div><p>難しいセキュリティ用語から始めず、「人・情報・操作・公開・確認・責任」の6点に分けると、ビジネス側でも判断しやすくなります。</p></div><div class="checklist"><div class="checkitem"><b>1. 誰が使えるか</b><p>全社員、特定部署、担当者だけなど、利用者を先に決めます。業務上必要な人だけに限定するほど、管理はシンプルになります。</p></div><div class="checkitem"><b>2. どの情報を見せるか</b><p>「社内情報だから全部見せる」ではなく、用途ごとに参照してよい資料を決めます。人によって閲覧権限が違う情報は、その差をAI利用時にも維持します。</p></div><div class="checkitem"><b>3. どこまで操作を任せるか</b><p>回答だけを行うのか、申請や登録まで進めるのかでリスクは変わります。金額・契約・人事など影響の大きい処理は、人の確認を残す設計が現実的です。</p></div><div class="checkitem"><b>4. どこで試してから公開するか</b><p>作成中・テスト中・本番利用を分け、変更をそのまま全社へ出さないルールを作ります。</p></div><div class="checkitem"><b>5. 何をもって安全に使えると判断するか</b><p>正しい質問だけでなく、曖昧な依頼、情報不足、権限外の依頼も含めて試し、期待しない挙動が起きないか確認します。</p></div><div class="checkitem"><b>6. 誰が運用責任を持つか</b><p>公開後に、利用状況・誤回答・変更依頼を見る担当と、必要なら停止を判断する責任者を決めます。</p></div></div></section><section class="section plain"><h2>「AIに社内データを入れて大丈夫か」を分解して考える</h2><p>判断したいのは、単純な「大丈夫・危険」ではありません。利用するサービスの契約条件やデータの取り扱い、保存場所、アクセス権、外部サービスへの接続、利用者が入力してよい情報の範囲を確認する必要があります。MicrosoftはCopilot Studioで、データポリシー、環境、アクセス管理、地域に関する制御などを企業向けの管理手段として案内しています。</p><p>NISTの生成AI向けリスク管理資料も、生成AIを一度設定して終わりにするのではなく、利用目的・影響・監視方法を継続的に見直す考え方を示しています。</p><div class="quote">安全性は「AIの性能」だけではなく、誰に何を許し、どう監視するかで決まる。</div><h2>人の確認を残した方がよい業務</h2><p>顧客への正式回答、契約、支払い、人事評価、法務判断など、間違ったときの影響が大きい業務は、AIが下書きや情報整理を担当し、最終判断を人が行う形から始めると管理しやすくなります。逆に、社内文書の検索や定型的な問い合わせなどは、影響範囲を限定したうえで自動化しやすい領域です。</p><h2>公開後の運用で見るもの</h2><p>利用回数だけでは足りません。回答の修正が多い質問、利用者が途中で諦める場面、想定外の操作、参照情報の古さなどを定期的に見直します。Microsoftの評価ガイドでも、同じテストケースを繰り返し実行し、変更前後を比較できる評価方法が用意されています。</p></section>'''

cost_body='''<p class="intro">AI Agentの費用は「月額いくらですか」だけでは決まりません。実際には、利用するサービスの料金に加えて、対象業務の整理、社内情報の準備、既存システムとの接続、テスト、公開後の改善までを含めて考える必要があります。費用を読み違えないためには、導入前に利用量と業務効果の両方を見積もることが重要です。</p><section class="section"><div class="section-head"><div><div class="eyebrow">Cost structure</div><h2>費用を<br>5つに分ける</h2></div><p>ツール料金だけを見ると安く見えても、社内調整や運用が大きければ総額は増えます。逆に、対象業務を絞れば小さく始められます。</p></div><div class="cost-grid"><div class="cost-item"><small>01 / SERVICE</small><h3>利用サービスの料金</h3><p>月額契約や利用量に応じた料金です。Microsoft Copilot Studioでは、利用量をCopilot Creditsで管理する仕組みが案内されています。</p></div><div class="cost-item"><small>02 / PREPARATION</small><h3>業務と情報の整理</h3><p>何をAIに任せるか、どの資料を使うか、例外時にどうするかを整理する時間です。</p></div><div class="cost-item"><small>03 / CONNECTION</small><h3>既存業務との接続</h3><p>申請、台帳、社内システムなどとつなぐ場合は、その範囲に応じて作業量が変わります。</p></div><div class="cost-item"><small>04 / TEST</small><h3>利用者テスト</h3><p>実際の質問や業務ケースで試し、誤りや使いづらさを直すための費用です。</p></div><div class="cost-item"><small>05 / OPERATION</small><h3>公開後の改善</h3><p>情報更新、利用状況の確認、追加要望への対応など、継続して発生する運用です。</p></div></div></section><section class="section plain"><h2>費用対効果は「削減時間」だけで見ない</h2><p>Microsoftの企業向けガイドでは、Agentの価値を考える際に、利用されているか、利用者にとって十分に機能しているか、投資に見合う価値が出ているかを分けて確認する考え方が示されています。つまり「1回あたり何分削減」だけではなく、利用率、やり直しの減少、対応の標準化なども確認対象になります。</p><div class="quote">先に価値を決めてから作ると、必要以上に大きなAgentを作りにくくなる。</div><h2>最初の見積もりで確認したい4項目</h2><div class="steps"><div class="step"><h3>月に何回使われるか</h3><p>利用者数だけでなく、1人が何回使うかまで想定します。</p></div><div class="step"><h3>今の業務に何時間かかっているか</h3><p>導入前の状態を測っておくと、後から効果を説明できます。</p></div><div class="step"><h3>AIが失敗したとき誰が直すか</h3><p>人の確認や修正が多い業務では、その時間も費用として考えます。</p></div><div class="step"><h3>本番後に誰が面倒を見るか</h3><p>情報更新や問い合わせ対応の担当が必要かを確認します。</p></div></div></section>'''

impl_body='''<p class="intro">AI Agent導入は、製品を選んでから始めるより「どの仕事を変えるか」を決めてから始める方が進めやすくなります。Microsoftの企業向け実装ガイドでも、目的・成功基準・リスク・体制を先に定義し、その後に実装、導入、運用、改善へ進む流れが示されています。</p><section class="section"><div class="section-head"><div><div class="eyebrow">Implementation</div><h2>導入を<br>6段階で進める</h2></div><p>大規模な全社導入から始める必要はありません。価値を測りやすい1業務で試し、結果を見て広げます。</p></div><div class="steps"><div class="step"><h3>改善したい業務を1つ選ぶ</h3><p>件数が多い、待ち時間が長い、同じ質問が繰り返されるなど、課題が見えやすい業務を選びます。</p></div><div class="step"><h3>成功条件を決める</h3><p>時間削減、修正回数、回答率、利用者評価など、導入後に比較できる指標を決めます。</p></div><div class="step"><h3>AIと人の役割を分ける</h3><p>AIが案内まで行うのか、入力や実行まで行うのか、最終確認を誰が行うのかを決めます。</p></div><div class="step"><h3>小さく作って現場で試す</h3><p>実際に使う人へ触ってもらい、きれいな想定質問だけでなく日常の言い方で確認します。</p></div><div class="step"><h3>数字と感想の両方で評価する</h3><p>時間や件数だけでなく、「使いやすいか」「安心して任せられるか」も確認します。</p></div><div class="step"><h3>続ける・直す・やめるを判断する</h3><p>PoCを成功扱いにすることが目的ではありません。価値が薄ければ対象業務や設計を変えます。</p></div></div></section><section class="section plain"><h2>最初から全社向けにしない理由</h2><p>対象範囲が広がるほど、利用者、情報、例外、権限、関係部署が増えます。最初は対象業務と利用者を限定し、問題が起きたときに原因を追える状態にしておく方が改善しやすくなります。</p><h2>ビジネス側が決めるべきこと</h2><p>製品名や技術構成よりも、「何ができれば業務上成功か」「誰が責任者か」「AIに任せてよい範囲はどこまでか」を決めることが重要です。技術側はその条件を実現する手段を選びます。</p><div class="quote">導入プロジェクトの中心はAIではなく、変えたい業務と評価方法。</div></section>'''

failure_body='''<p class="intro">AI Agent導入がうまくいかない原因は、AIの回答精度だけではありません。対象業務が広すぎる、成功の定義がない、現場が使わない、参照情報が古い、公開後の担当がいない──こうした業務・運用面の問題で止まるケースがあります。企業向けガイドでも、目的、評価、導入、運用を一連のものとして設計することが重視されています。</p><section class="section"><div class="section-head"><div><div class="eyebrow">Failure patterns</div><h2>よくある<br>5つの失敗</h2></div><p>失敗を技術問題だけにしないことが重要です。多くは導入前の決め方と公開後の運用で予防できます。</p></div><div class="cards"><div class="card" data-mark="01"><span class="num">01 / TOO WIDE</span><h3>最初から何でもできるAIを目指す</h3><p>用途が広いほど正解も責任範囲も曖昧になります。</p></div><div class="card" data-mark="02"><span class="num">02 / NO BASELINE</span><h3>導入前の数字を取っていない</h3><p>改善したかどうかを後から説明できません。</p></div><div class="card" data-mark="03"><span class="num">03 / NO OWNER</span><h3>公開後の担当者がいない</h3><p>情報更新や不具合対応が止まり、徐々に使われなくなります。</p></div></div></section><section class="section plain"><h2>4つ目：現場の使い方を確認せず公開する</h2><p>作成者が想定した質問と、実際の利用者の聞き方は一致しないことがあります。Microsoftの評価機能も、テストケースを繰り返し実行して変更前後を比較する考え方を採用しています。公開前に現場の表現や情報不足の質問を含めて試すことが重要です。</p><h2>5つ目：利用率だけで成功と判断する</h2><p>使われていても、毎回答えを直しているなら業務負荷は減っていません。利用率に加えて、修正、完了、時間、満足度などを組み合わせて見ます。</p><div class="quote">「作れた」ではなく「業務が良くなった」で成功を判断する。</div><h2>失敗を防ぐ最小チェック</h2><div class="checklist"><div class="checkitem"><b>対象業務が1文で説明できる</b><p>誰のどの仕事を支援するかが明確か確認します。</p></div><div class="checkitem"><b>導入前の状態を測っている</b><p>時間、件数、修正回数など比較できる数字を残します。</p></div><div class="checkitem"><b>公開後の責任者がいる</b><p>改善・停止・情報更新を判断する人を決めます。</p></div></div></section>'''

eff_body='''<p class="intro">生成AIで業務効率化を考えるとき、「文章を作れる仕事」を片っ端からAI化する必要はありません。効果が出やすいのは、件数が多く、情報を探す・整理する・同じ説明をする・次の作業へ渡すといった繰り返しがある業務です。導入前に現在の仕事を分解すると、AIを使うべき場所が見えやすくなります。</p><section class="section"><div class="section-head"><div><div class="eyebrow">Business efficiency</div><h2>AI化しやすい<br>4つの仕事</h2></div><p>「できるか」より「改善を測れるか」で対象業務を選びます。</p></div><div class="cost-grid"><div class="cost-item"><small>01 / FIND</small><h3>探す</h3><p>社内資料、手順、FAQなどから必要な情報を探す業務。</p></div><div class="cost-item"><small>02 / ORGANIZE</small><h3>整理する</h3><p>問い合わせや文章を分類し、必要な要点をまとめる業務。</p></div><div class="cost-item"><small>03 / GUIDE</small><h3>案内する</h3><p>同じルールや手順を繰り返し説明する業務。</p></div><div class="cost-item"><small>04 / HANDOFF</small><h3>次へつなぐ</h3><p>必要情報を集めて担当者や次の処理へ渡す業務。</p></div></div></section><section class="section plain"><h2>効果が見えにくい業務から始めない</h2><p>年に数回しか発生しない業務や、毎回条件が大きく違う業務は、導入効果を確認するまで時間がかかります。MicrosoftのROIガイドでも、価値を先に定義し、利用・品質・成果を継続して測ることが重視されています。</p><h2>業務効率化の評価方法</h2><p>時間短縮だけでなく、問い合わせの往復回数、手戻り、待ち時間、担当者間のばらつきも候補になります。現場の負担を数字に変えると、AI化の優先順位を比較しやすくなります。</p><div class="quote">「AIを使う業務」を探すのではなく、「繰り返し負担が発生している業務」を探す。</div></section>'''

pages=[
('ai-agent-security-governance','AI Agentのセキュリティと運用｜導入前に決める6つのこと｜テンキ','社内でAI Agentを使う際のセキュリティと運用を、非エンジニア向けに解説。利用者、社内データ、操作範囲、人の確認、テスト、運用責任の6点を整理します。','Security / Governance','AI Agentを<br><em>安全に運用する</em>','社内データを扱うAI Agentは、製品の安全性だけでなく、誰に何を許し、どう確認し、誰が運用するかまで決めて初めて業務で使える状態になります。','技術より先に<br>運用ルールを決める','セキュリティをIT部門だけの課題にせず、業務側が決めるべき条件へ分解します。',security_body,[('Microsoft Learn｜Copilot Studio security and governance','https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-and-governance'),('Microsoft Learn｜Secure your Copilot Studio projects','https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/sec-gov-phase3'),('Microsoft Learn｜Zoned governance strategy','https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/sec-gov-phase2'),('NIST｜Generative AI Profile (AI RMF)','https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence'),('Microsoft Learn｜Agent evaluation overview','https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-agent-evaluation-overview')],[('POC','AI Agent PoCの進め方','/ai-agent-poc.html'),('COST','AI Agent導入費用','/ai-agent-cost.html'),('FAILURE','導入失敗を防ぐ','/ai-agent-failure.html')]),
('ai-agent-cost','AI Agent導入費用の考え方｜何にお金がかかる？見積もりの5項目｜テンキ','AI Agent導入費用を、サービス料金、業務整理、既存業務との接続、テスト、運用の5項目に分けて非エンジニア向けに解説します。','Cost / ROI','AI Agentの<br><em>費用を分解する</em>','ツールの月額だけでは、AI Agent導入に必要な費用は分かりません。小さく始めるための見積もり方を整理します。','費用と効果を<br>同じ表で見る','利用量だけでなく、導入前後の業務負荷と運用コストまで含めて判断します。',cost_body,[('Microsoft Learn｜Copilot Credits billing rates','https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-messages-management'),('Microsoft Learn｜Purchase and manage Copilot credits','https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/billing-manage-buy-credits'),('Microsoft Learn｜Measure ROI and business value','https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/agent-business-value-overview')],[('POC','AI Agent PoCの進め方','/ai-agent-poc.html'),('IMPLEMENT','AI Agent導入の進め方','/ai-agent-implementation.html'),('SECURITY','セキュリティと運用','/ai-agent-security-governance.html')]),
('ai-agent-implementation','AI Agent導入の進め方｜業務選定から本番判断まで6ステップ｜テンキ','AI Agent導入を、対象業務の選定、成功条件、AIと人の役割、小さな試作、評価、本番判断の6ステップで非エンジニア向けに解説します。','Implementation','AI Agent導入を<br><em>6段階で進める</em>','製品を先に決めるのではなく、変えたい業務と成功条件を決めてから小さく試す進め方を整理します。','全社導入より<br>1業務から始める','対象を限定すると、効果と問題点の両方を早く確認できます。',impl_body,[('Microsoft Learn｜Copilot Studio implementation guidance','https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/'),('Microsoft Learn｜Implementation checklist','https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/implement-checklist'),('NIST｜Generative AI Profile (AI RMF)','https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence')],[('COST','AI Agent導入費用','/ai-agent-cost.html'),('POC','AI Agent PoC','/ai-agent-poc.html'),('FAILURE','導入失敗を防ぐ','/ai-agent-failure.html')]),
('ai-agent-failure','AI Agent導入の失敗を防ぐ｜よくある5つの原因と対策｜テンキ','AI Agent導入が失敗する原因を、対象範囲、評価、現場利用、運用責任など業務側の観点から整理。非エンジニア向けに予防策を解説します。','Failure / Improvement','AI Agent導入の<br><em>失敗を防ぐ</em>','精度だけを改善しても、AI Agentが業務に定着するとは限りません。導入前後で起きやすい失敗を業務側の視点から整理します。','成功条件を<br>作る前に決める','利用・品質・成果を測る基準があれば、PoCを続けるか止めるか判断できます。',failure_body,[('Microsoft Learn｜Implementation guidance','https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/'),('Microsoft Learn｜Measure agent impact','https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/agent-business-value-measure-impact'),('Microsoft Learn｜Agent evaluation overview','https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-agent-evaluation-overview'),('NIST｜Generative AI Profile (AI RMF)','https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence')],[('IMPLEMENT','AI Agent導入の進め方','/ai-agent-implementation.html'),('POC','AI Agent PoC','/ai-agent-poc.html'),('SECURITY','セキュリティと運用','/ai-agent-security-governance.html')]),
('generative-ai-business-efficiency','生成AIで業務効率化する方法｜AI化しやすい仕事の選び方｜テンキ','生成AIで業務効率化する際に、どの仕事からAI化すべきかを「探す・整理する・案内する・次へつなぐ」の4タイプで非エンジニア向けに解説します。','Business Efficiency','生成AIで<br><em>業務を効率化する</em>','AIでできることを探すのではなく、日々繰り返している負担から対象業務を選ぶ方法を整理します。','高頻度の仕事から<br>測って改善する','件数が多く、改善前後を比較できる業務ほど導入効果を判断しやすくなります。',eff_body,[('Microsoft Learn｜Measure ROI and business value','https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/agent-business-value-overview'),('Microsoft Learn｜Measure the impact of your agents','https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/agent-business-value-measure-impact'),('Microsoft Learn｜Implementation guidance','https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/')],[('AI AGENT','AI Agentとは','/ai-agent.html'),('IMPLEMENT','AI Agent導入の進め方','/ai-agent-implementation.html'),('CASE','企業向け支援実績','/case-studies.html')]),
]
for args in pages:
    slug=args[0]; Path(slug+'.html').write_text(new_article(*args))

# ---------- sitemap ----------
sp=Path('sitemap-tenki.xml')
xml=ET.parse(sp); root=xml.getroot(); ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
existing={u.find(ns+'loc').text for u in root.findall(ns+'url')}
new_urls=[f'{BASE}/{x[0]}.html' for x in pages]
for slug in products:
    new_urls += [f'{BASE}/en/products/{slug}.html',f'{BASE}/es/products/{slug}.html']
for url in new_urls:
    if url not in existing:
        u=ET.SubElement(root,ns+'url'); ET.SubElement(u,ns+'loc').text=url; ET.SubElement(u,ns+'lastmod').text=TODAY; ET.SubElement(u,ns+'changefreq').text='monthly'; ET.SubElement(u,ns+'priority').text='0.8'
# update changed product and article dates
for u in root.findall(ns+'url'):
    loc=u.find(ns+'loc').text
    if any(loc.endswith('/'+f) for f in list(article_pages)+['about.html','case-studies.html']) or '/products/' in loc:
        lm=u.find(ns+'lastmod')
        if lm is not None: lm.text=TODAY
ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9')
xml.write(sp,encoding='utf-8',xml_declaration=True)

print('SEO A-tier text pass prepared')
