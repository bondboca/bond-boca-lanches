// Folha de contato com todos os ícones em tamanho grande (para revisar o desenho).
// Uso (na raiz D:\resultados): node bond_boca/folha_icones.mjs <png de saída>
import { chromium } from "playwright";
import path from "node:path";
import { pathToFileURL } from "node:url";
const br = await chromium.launch();
const p = await br.newPage({ viewport: { width: 1400, height: 900 }, deviceScaleFactor: 1 });
const erros = []; p.on("pageerror", e => erros.push(e.message));
await p.goto(pathToFileURL(path.resolve("bond_boca/index.html")).href, { waitUntil: "networkidle" });
await p.evaluate(() => {
  const icones = [];
  CATS.forEach(c => c.itens.forEach(it => { if(!it.refri) icones.push([it.nome, iconDe(it)]); }));
  for (const m of ["Coca","Fanta","Guaraná"]) { marcaRefri = m; CATS[5].itens.forEach(it => { if(it.marcas.includes(m)) icones.push([nomeBag(it), iconDe(it)]); }); }
  icones.push(["X Burguer +bacon+ovo", iconDe(ITEM["sanduiches-2"], null, { bacon:1, ovo:1 })]);
  for (const s of ["Uva","Cajá","Goiaba","Açaí"]) icones.push(["Suco " + s, iconDe(ITEM["sucos-1"], s)]);
  icones.push(["Açaí leite cond.", iconDe(ITEM["acai-1"], "Leite condensado")]);
  document.body.innerHTML = '<div id="f" style="display:grid;grid-template-columns:repeat(8,170px);gap:6px;padding:10px;background:#fff;font:12px sans-serif"></div>';
  for (const [n, ic] of icones) {
    const d = document.createElement("div"); d.style.textAlign = "center";
    const cv = document.createElement("canvas"); cv.width = cv.height = 340; cv.style.width = cv.style.height = "160px";
    desenhar(cv, ic); d.append(cv, Object.assign(document.createElement("div"), { textContent: n })); f.append(d);
  }
});
await p.locator("#f").screenshot({ path: process.argv[2] });
console.log("erros:", erros.join("; ") || "nenhum");
await br.close();
