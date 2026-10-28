# Busca fotos de licença livre no Wikimedia Commons e monta folhas de contato para escolher.
# Uso: python -I bond_boca/buscar_fotos.py <pasta-saida> "rotulo=consulta" ...
import json, sys, os, urllib.request, urllib.parse, urllib.error, io, re, time
from PIL import Image, ImageDraw

UA = {"User-Agent": "BondBocaCardapio/1.0 (cardapio de lanchonete; contato via WhatsApp)"}
API = "https://commons.wikimedia.org/w/api.php?"
LIVRES = re.compile(r"^(CC0|CC BY|CC-BY|Public domain|PD)", re.I)

def get(url, tentativas=5):
    # o Commons limita a taxa: espaça os pedidos e repete com espera crescente no 429
    for t in range(tentativas):
        time.sleep(0.6)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429 or t == tentativas - 1: raise
            time.sleep(4 * (t + 1))

def buscar(q, n=12):
    p = {"action": "query", "generator": "search", "gsrsearch": q + " filetype:bitmap", "gsrnamespace": 6, "gsrlimit": n,
         "prop": "imageinfo", "iiprop": "url|extmetadata|size", "iiurlwidth": 400, "format": "json"}
    d = json.loads(get(API + urllib.parse.urlencode(p)))
    out = []
    for pg in sorted(d.get("query", {}).get("pages", {}).values(), key=lambda x: x.get("index", 0)):
        ii = pg["imageinfo"][0]; m = ii.get("extmetadata", {})
        lic = m.get("LicenseShortName", {}).get("value", "")
        if not LIVRES.match(lic): continue
        autor = re.sub("<[^>]+>", "", m.get("Artist", {}).get("value", "")).strip()
        out.append({"titulo": pg["title"], "thumb": ii["thumburl"], "url": ii["url"], "pagina": ii["descriptionurl"], "licenca": lic, "autor": autor, "w": ii["width"], "h": ii["height"]})
    return out

saida = sys.argv[1]; os.makedirs(saida, exist_ok=True)
todos = {}
for arg in sys.argv[2:]:
    rot, q = arg.split("=", 1)
    res = buscar(q)[:10]
    todos[rot] = res
    W = 200; folha = Image.new("RGB", (W * 5, (W + 30) * 2), "white"); dr = ImageDraw.Draw(folha)
    for i, r in enumerate(res):
        try:
            im = Image.open(io.BytesIO(get(r["thumb"]))).convert("RGB"); im.thumbnail((W, W))
        except Exception as e:
            continue
        x, y = (i % 5) * W, (i // 5) * (W + 30)
        folha.paste(im, (x + (W - im.width) // 2, y + (W - im.height) // 2))
        dr.text((x + 4, y + W + 4), f"{i} {r['licenca'][:14]}", fill="black")
    folha.save(os.path.join(saida, f"{rot}.jpg"), quality=80)
    print(rot, len(res))
old = {}
f = os.path.join(saida, "candidatos.json")
if os.path.exists(f): old = json.load(open(f, encoding="utf-8"))
old.update(todos)
json.dump(old, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
