// Presentazioni 16:9: diario di bordo e colloqui di revisione.
// Ogni slide riporta evento, data, logo e numero "n/N", più la versione se c'è. Uso:
//   #show: presentazione.with(evento: "Diario di bordo", data: "AAAA-MM-GG", versione: "1.0.0", aggiornato: "AAAA-MM-GG", titolo: "...")
//   #slide(titolo: "...")[...]
#import "stile.typ": base, info, logo, occhiello, palette, sito-breve

// `aggiornato` non va sulle slide, che mostrano solo la versione: lo legge il sito
#let presentazione(evento: "", data: "", versione: none, aggiornato: none, titolo: "", corpo) = {
  let filetto = line(length: 100%, stroke: 0.5pt + palette.filetto)
  set document(title: evento + " " + data)
  set page(
    paper: "presentation-16-9",
    margin: (x: 1.8cm, top: 2.6cm, bottom: 2cm),
    header: context {
      set text(size: 12pt, fill: palette.tenue)
      stack(
        dir: ttb,
        spacing: 6pt,
        grid(
          columns: (1fr, auto),
          align: (left + horizon, right + horizon),
          [#evento · #data], if here().page() > 1 { logo(height: 1.1cm) } else { box(height: 1.1cm) },
        ),
        filetto,
      )
    },
    footer: context {
      set text(size: 12pt, fill: palette.tenue)
      stack(
        dir: ttb,
        spacing: 6pt,
        filetto,
        grid(
          columns: (1fr, auto),
          if versione != none [#info.nome · v#versione] else { info.nome },
          [#counter(page).display()/#counter(page).final().first()],
        ),
      )
    },
  )
  show: base
  set text(size: 18pt)
  set par(justify: false, spacing: 1.2em)
  show heading: it => block(width: 100%, below: 0.9em, stack(
    dir: ttb,
    spacing: 0.4em,
    text(size: 26pt, weight: "bold", fill: palette.accento, it.body),
    line(length: 100%, stroke: 0.8pt + palette.accento),
  ))

  // slide del titolo
  let contatti = (
    if info.email != "" { link("mailto:" + info.email, info.email) },
    if info.sito != "" { link(info.sito, sito-breve) },
  ).filter(c => c != none)
  v(1fr)
  grid(
    columns: (1fr, auto),
    column-gutter: 1.5cm,
    align: (left + horizon, right + horizon),
    {
      line(length: 3cm, stroke: 3pt + palette.accento)
      v(0.6cm)
      occhiello(evento, size: 14pt)
      v(0.2cm)
      block(text(size: 34pt, weight: "bold", titolo))
      text(size: 18pt, fill: palette.tenue)[#info.nome · #data]
      if contatti.len() > 0 {
        v(0.3cm)
        text(size: 14pt, fill: palette.tenue, contatti.join[ · ])
      }
    },
    logo(height: 5cm),
  )
  v(1.5fr)

  corpo
}

#let slide(titolo: "", corpo) = {
  pagebreak(weak: true)
  heading(titolo)
  corpo
}
