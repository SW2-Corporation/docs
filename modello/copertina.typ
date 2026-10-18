// Copertina dei documenti con registro, senza intestazione né piè di pagina.
// In testa la fascia scura con logo, nome, contatti e membri del gruppo; in fondo la scheda del documento.
// `voci` è un array di coppie (etichetta, valore): quelle senza valore non compaiono.
#import "stile.typ": fascia, occhiello, palette, riquadro

#let copertina(tipo: "", titolo: "", sottotitolo: none, voci: ()) = page(header: none, footer: none)[
  #fascia(altezza: 9.6cm, membri: true)

  #v(1fr)
  #occhiello(tipo, size: 11pt)
  #v(0.4cm)
  #block(width: 100%)[
    #set par(justify: false, leading: 0.55em)
    #text(size: 32pt, weight: "bold", titolo)
  ]
  #if sottotitolo != none [
    #v(0.3cm)
    #text(size: 14pt, fill: palette.tenue, sottotitolo)
  ]
  #v(2fr)

  #let presenti = voci.filter(((_, valore)) => valore not in (none, ""))
  #riquadro[
    #set text(size: 10.5pt)
    #set par(justify: false)
    #grid(
      columns: (auto, 1fr, auto, 1fr),
      column-gutter: 1.2em,
      row-gutter: 0.75em,
      align: (left + top, left + top, left + top, left + top),
      ..presenti.map(((voce, valore)) => (text(fill: palette.tenue, voce), valore)).flatten(),
    )
  ]
]
