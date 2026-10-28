# Baixa as fotos escolhidas no Commons, recorta em quadrado 360x360 e gera o bloco FOTOS/CREDITOS da página.
# Uso: python -I bond_boca/montar_fotos.py <pasta com candidatos.json>
import json, sys, os, io, base64, time, urllib.request, urllib.error
from PIL import Image, ImageFilter

UA = {"User-Agent": "BondBocaCardapio/1.0 (cardapio de lanchonete; contato via WhatsApp)"}
AQUI = os.path.dirname(os.path.abspath(__file__))
cand = json.load(open(os.path.join(sys.argv[1], "candidatos.json"), encoding="utf-8"))

# chave do item -> (folha, índice, modo, foco x, foco y). "cobrir" recorta; "conter" encaixa inteiro (garrafas e latas)
ESCOLHA = {
  "coxinhas-0": ("coxinha",0,"cobrir",.5,.55), "coxinhas-1": ("coxinha",0,"cobrir",.5,.62), "coxinhas-2": ("coxinha",9,"cobrir",.55,.6),
  "coxinhas-3": ("coxinha",9,"cobrir",.6,.55), "coxinhas-4": ("coxinha",1,"cobrir",.5,.5), "coxinhas-5": ("coxinha",8,"cobrir",.5,.5),
  "coxinhas-6": ("coxinha",1,"cobrir",.48,.55),
  "sanduiches-0": ("xsalada",4,"cobrir",.5,.5), "sanduiches-1": ("xsalada",2,"cobrir",.5,.5), "sanduiches-2": ("xbacon",4,"conter",.5,.5),
  "sanduiches-3": ("xegg",5,"cobrir",.55,.55), "sanduiches-4": ("xsalada",1,"cobrir",.5,.55), "sanduiches-5": ("xsalada",0,"cobrir",.45,.5),
  "sanduiches-6": ("xbacon",6,"cobrir",.3,.5), "sanduiches-7": ("xsalada",5,"cobrir",.35,.5), "sanduiches-8": ("xsalada",8,"cobrir",.6,.5),
  "sanduiches-9": ("xegg",0,"cobrir",.5,.5), "sanduiches-10": ("xbacon",1,"cobrir",.5,.5), "sanduiches-11": ("xsalada",9,"cobrir",.5,.5),
  "sanduiches-12": ("misto",9,"cobrir",.5,.7), "sanduiches-13": ("misto",8,"cobrir",.5,.5), "sanduiches-14": ("americano",2,"cobrir",.5,.5),
  "sanduiches-15": ("americano",3,"cobrir",.6,.4), "sanduiches-16": ("americano",7,"cobrir",.45,.55), "sanduiches-17": ("misto",2,"cobrir",.4,.5),
  "salgados-0": ("enroladinho",7,"cobrir",.5,.5), "salgados-1": ("pastel",4,"cobrir",.5,.5),
  "acai-0": ("acai",2,"cobrir",.5,.5), "acai-1": ("acai",5,"cobrir",.5,.5),
  "sucos-0": ("vitamina",0,"cobrir",.5,.4), "sucos-1": ("vitamina",1,"cobrir",.5,.35), "sucos-2": ("laranja",0,"cobrir",.5,.6),
  "refrigerantes-1|Coca": ("cocavidro",1,"conter",.5,.5), "refrigerantes-2|Coca": ("cocalata",3,"conter",.5,.5),
  "refrigerantes-3|Coca": ("cocapet",7,"conter",.5,.5), "refrigerantes-4|Coca": ("cocavidro",7,"conter",.5,.5),
  "refrigerantes-6|Coca": ("cocapet",7,"conter",.5,.5), "refrigerantes-8|Coca": ("cocapet",8,"conter",.5,.5),
  "refrigerantes-0|Fanta": ("fanta",2,"cobrir",.6,.5), "refrigerantes-2|Fanta": ("fanta",8,"cobrir",.5,.5),
  "refrigerantes-3|Fanta": ("fanta",9,"cobrir",.35,.5), "refrigerantes-4|Fanta": ("fanta",2,"cobrir",.6,.5),
  "refrigerantes-5|Fanta": ("fanta",9,"cobrir",.6,.5), "refrigerantes-7|Fanta": ("fanta",5,"cobrir",.25,.5),
  "refrigerantes-0|Guaraná": ("guarana",6,"cobrir",.7,.55), "refrigerantes-2|Guaraná": ("guarana",0,"cobrir",.5,.45),
  "refrigerantes-3|Guaraná": ("guarana",6,"cobrir",.7,.55), "refrigerantes-4|Guaraná": ("guarana",6,"cobrir",.7,.55),
  "refrigerantes-5|Guaraná": ("guarana",6,"cobrir",.7,.55), "refrigerantes-7|Guaraná": ("guarana",6,"cobrir",.7,.55),
  "bebidas-1": ("agua",7,"conter",.5,.5), "bebidas-2": ("agua",7,"conter",.5,.5), "bebidas-3": ("agua",1,"conter",.5,.5),
  "bebidas-4": ("limonada",6,"conter",.5,.5),
  "tortas-0": ("tortacake",2,"cobrir",.5,.5), "tortas-1": ("tortacake",8,"cobrir",.5,.55), "tortas-2": ("tortacake",0,"cobrir",.5,.5),
  "tortas-3": ("tortaninho",1,"cobrir",.5,.5),
}
LADO = 288

def get(url):
    for t in range(6):
        time.sleep(.7)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r: return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429 or t == 5: raise
            time.sleep(5 * (t + 1))

def quadrado(im, modo, fx, fy):
    if modo == "conter":
        # fundo: a própria foto ampliada e desfocada; por cima, o produto inteiro
        fundo = quadrado(im, "cobrir", .5, .5).filter(ImageFilter.GaussianBlur(16))
        c = im.copy(); c.thumbnail((LADO, LADO), Image.LANCZOS)
        fundo.paste(c, ((LADO - c.width) // 2, (LADO - c.height) // 2)); return fundo
    s = min(im.width, im.height)
    x = min(max(int(im.width * fx - s / 2), 0), im.width - s); y = min(max(int(im.height * fy - s / 2), 0), im.height - s)
    return im.crop((x, y, x + s, y + s)).resize((LADO, LADO), Image.LANCZOS)

cache, fotos, creditos, usados = {}, {}, [], set()
os.makedirs(os.path.join(AQUI, "fotos"), exist_ok=True)
for chave, (folha, i, modo, fx, fy) in ESCOLHA.items():
    c = cand[folha][i]
    if c["url"] not in cache:
        try: dados = get(c["thumb"].replace("/400px-", "/800px-"))
        except Exception: dados = get(c["thumb"])
        cache[c["url"]] = Image.open(io.BytesIO(dados)).convert("RGB")
    q = quadrado(cache[c["url"]], modo, fx, fy)
    buf = io.BytesIO(); q.save(buf, "JPEG", quality=70, optimize=True, progressive=True)
    q.save(os.path.join(AQUI, "fotos", chave.replace("|", "_") + ".jpg"), quality=86)
    fotos[chave] = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    if c["url"] not in usados:
        usados.add(c["url"]); creditos.append([c["titulo"].replace("File:", ""), c["autor"] or "autor desconhecido", c["licenca"], c["pagina"]])
    print(chave, len(buf.getvalue()) // 1024, "KB")

js = "// ===== FOTOS (gerado por montar_fotos.py, Wikimedia Commons) =====\nconst FOTOS = " + json.dumps(fotos) + ";\nconst CREDITOS = " + json.dumps(creditos, ensure_ascii=False) + ";\n// ===== fim FOTOS =====\n"
open(os.path.join(AQUI, "fotos.js"), "w", encoding="utf-8").write(js)
print("total", sum(len(v) for v in fotos.values()) // 1024, "KB em base64,", len(creditos), "créditos")
