// Testa a página da Bond Boca no celular: erros de console, fluxo de pedido e link do WhatsApp.
// Uso: node bond_boca/testar.mjs <pasta-de-saida>
import { chromium } from "playwright";
import path from "node:path";
import { pathToFileURL } from "node:url";

const saida = process.argv[2] || ".";
const pagina = pathToFileURL(path.resolve("bond_boca/index.html")).href;
const shot = (p, nome, opts = {}) => p.screenshot({ path: path.join(saida, nome), ...opts });

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
const p = await ctx.newPage();
const erros = [];
p.on("pageerror", e => erros.push("pageerror: " + e.message));
p.on("console", m => { if (m.type() === "error") erros.push("console: " + m.text()); });

await p.goto(pagina, { waitUntil: "networkidle" });
await p.waitForTimeout(900);
await shot(p, "01_topo.png");

// rola por todas as seções para disparar as animações e tirar folha de cada uma
for (const id of ["coxinhas", "sanduiches", "salgados", "acai", "sucos", "refrigerantes", "bebidas", "tortas"]) {
  await p.click(`#tab-${id}`);
  await p.waitForTimeout(900);
  await shot(p, `02_${id}.png`);
}
await p.click('#marcas [data-marca="Guaraná"]');
await p.waitForTimeout(700);
await shot(p, "03_refri_guarana.png");

// item simples
await p.click("#tab-coxinhas"); await p.waitForTimeout(700);
await p.click('[data-add="coxinhas-1"]'); await p.waitForTimeout(900);
// sanduíche com adicionais
await p.click("#tab-sanduiches"); await p.waitForTimeout(700);
await p.click('[data-add="sanduiches-7"]'); await p.waitForTimeout(500);
await p.click('[data-ad="bacon"][data-d="1"]');
await p.click('[data-ad="ovo"][data-d="1"]');
await p.click('[data-ad="ovo"][data-d="1"]');
await p.waitForTimeout(300);
await shot(p, "04_adicionais.png");
await p.click("#op-ok"); await p.waitForTimeout(900);
// suco com sabor
await p.click("#tab-sucos"); await p.waitForTimeout(700);
await p.click('[data-add="sucos-0"]'); await p.waitForTimeout(400);
console.log("botão sem sabor:", await p.textContent("#op-ok"), "disabled=", await p.isDisabled("#op-ok"));
await p.click('label:has(input[value="Cajá"])'); await p.waitForTimeout(300);
await shot(p, "05_suco.png");
await p.click("#op-ok"); await p.waitForTimeout(900);
// açaí
await p.click("#tab-acai"); await p.waitForTimeout(700);
await p.click('[data-add="acai-1"]'); await p.waitForTimeout(300);
await p.click('label:has(input[value="Mel"])'); await p.click("#op-ok"); await p.waitForTimeout(900);
// refri
await p.click("#tab-refrigerantes"); await p.waitForTimeout(700);
await p.click('[data-add="refrigerantes-2"]'); await p.waitForTimeout(900);

await p.click("#bag-toggle"); await p.waitForTimeout(500);
await shot(p, "06_sacola.png");

// finalizar: tenta enviar vazio
await p.click("#bag-send"); await p.waitForTimeout(600);
await p.evaluate(() => document.getElementById("co-send").addEventListener("click", e => e.preventDefault()));
await p.click("#co-send"); await p.waitForTimeout(200);
console.log("erro sem dados:", await p.textContent("#co-err"));
await p.fill("#co-nome", "Maria Souza");
await p.fill("#co-rua", "Rua Rui Barbosa"); await p.dispatchEvent("#co-rua", "change");
await p.fill("#co-num", "120");
await p.fill("#co-bairro", "Centro");
await p.click("#co-mapa-btn"); await p.waitForTimeout(2500);
await p.click('label:has(#pag-din)'); await p.fill("#co-troco", "50");
await shot(p, "07_finalizar.png", { fullPage: false });
await p.locator("#co .co").evaluate(el => el.scrollTop = 0);
await p.locator("#map-box").screenshot({ path: path.join(saida, "08_mapa.png") });
await p.click("#co-send"); await p.waitForTimeout(200);
const href = await p.getAttribute("#co-send", "href");
console.log("\nMENSAGEM:\n" + decodeURIComponent(href.split("?text=")[1]));
console.log("\nlocalStorage:", await p.evaluate(() => localStorage.getItem("bondboca_cliente")));

// retirada: valida só o nome
await p.click('label:has(input[value="Retirada"])'); await p.waitForTimeout(200);
console.log("endereço oculto na retirada:", await p.isHidden("#fs-end"));

// volta: recarrega e abre de novo
await p.reload({ waitUntil: "networkidle" }); await p.waitForTimeout(600);
await p.click('[data-add="tortas-2"]').catch(async () => { await p.click("#tab-tortas"); await p.waitForTimeout(700); await p.click('[data-add="tortas-2"]'); });
await p.waitForTimeout(900);
await p.click("#bag-send"); await p.waitForTimeout(600);
console.log("volta:", await p.textContent("#co-ola"));
await shot(p, "09_volta.png");

// desktop
await p.setViewportSize({ width: 1280, height: 860 });
await p.click("#co-close"); await p.evaluate(() => scrollTo(0, 0)); await p.waitForTimeout(600);
await shot(p, "10_desktop.png");

console.log("\nERROS:", erros.length ? erros.join("\n") : "nenhum");
await browser.close();
