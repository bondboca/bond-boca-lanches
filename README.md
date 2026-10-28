# Bond Boca Lanches · cardápio com pedido pelo WhatsApp

Cardápio da **Bond Boca Lanches** (@bond.bocalanches) com coxinhas, sanduíches, salgados, açaí, sucos, refrigerantes, bebidas e tortas. O cliente monta o pedido, escolhe entrega ou retirada e envia tudo pronto pelo WhatsApp.

A página inteira é um arquivo só, o `index.html`, com o CSS, o JS e as fotos embutidos. Funciona em qualquer hospedagem.

## Editar os dados

No começo do `<script>` do `index.html` fica o bloco `CONFIG`:

```js
const CONFIG = {
  whatsapp: "5587998038645",
  telefoneExibido: "(87) 99803-8645",
  endereco: "PREENCHER",
  taxaEntrega: 0,
  logo: "",          // "logo.png" ao lado do HTML, ou data:image/...;base64
  horarios: [...]    // 0 = domingo ... 6 = sábado, horário de Brasília
};
```

Os preços e itens ficam na lista `CATS`, logo abaixo.

## O que a página faz

- Selo "Aberto agora" ou "Fechado" pelo horário de Brasília.
- Abas de categoria que ficam fixas no topo ao rolar.
- Opções antes de adicionar: sabor do suco e do pastel, cobertura do açaí, marca do refrigerante e adicionais dos sanduíches com + e −.
- Sacola fixa e tela de finalizar, com mapa das ruas de Lajedo (Leaflet + OpenStreetMap) e GPS.
- Os dados do cliente ficam salvos no aparelho. Na volta aparece "Bem-vindo de volta, Nome! Este será seu Nº pedido".
- Sons de clique gerados no navegador e animações que respeitam o `prefers-reduced-motion`.

## Fotos

As fotos são **ilustrativas**, do [Wikimedia Commons](https://commons.wikimedia.org), com licença livre. Os créditos de cada uma ficam no rodapé da página.

- `buscar_fotos.py` busca candidatas e monta folhas de contato.
- `montar_fotos.py` baixa as escolhidas, recorta em 288×288 e gera o bloco `FOTOS`/`CREDITOS`.

O ideal é trocar pelas fotos da própria lanchonete.

## Testes

```
node bond_boca/testar.mjs <pasta-de-saída>        # pedido completo no Chromium (Playwright)
node bond_boca/folha_icones.mjs <png-de-saída>    # folha com os desenhos em canvas
```
