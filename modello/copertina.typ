// Copertina dei documenti con registro, senza intestazione né piè di pagina.
// `voci` è un array di coppie (etichetta, valore): quelle senza valore non compaiono.
#import "stile.typ": logo, mittente, occhiello, palette

#let copertina(tipo: "", titolo: "", sottotitolo: none, voci: ()) = page(header: none, footer: none)[
  #place(top + right, dx: 1.5cm, dy: -2cm, logo(width: 4.9cm))
  #mittente

  #v(1fr)
  #line(length: 3.5cm, stroke: 3pt + palette.accento)
  #v(0.8cm)
  #occhiello(tipo, size: 11pt)
  #v(0.4cm)
  #block(width: 100%)[
    #set par(justify: false, leading: 0.55em)
    #text(size: 30pt, weight: "bold", titolo)
  ]
  #if sottotitolo != none [
    #v(0.3cm)
    #text(size: 14pt, fill: palette.tenue, sottotitolo)
  ]

  #v(2fr)
  #block(width: 100%, stroke: (top: 0.5pt + palette.filetto), inset: (top: 1em))[
    #grid(
      columns: (auto, 1fr),
      column-gutter: 1.5em,
      row-gutter: 0.8em,
      ..voci.filter(((_, valore)) => valore not in (none, "")).map(((voce, valore)) => (
        text(fill: palette.tenue, voce), valore,
      )).flatten(),
    )
  ]
]
