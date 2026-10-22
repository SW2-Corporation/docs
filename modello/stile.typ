// Aspetto comune di documenti, lettere, verbali e presentazioni.
// Colore d'accento e logo si impostano in dati/gruppo.toml, tutto il resto qui.
#import "comuni.typ": gruppo

#let info = gruppo.gruppo
#let colore = info.at("colore", default: "")

// Margini della pagina A4: servono anche alle fasce a tutta larghezza.
#let margini = (x: 2.5cm, top: 3cm, bottom: 2.8cm)
#let larghezza-pagina = 21cm

// Palette derivata dal colore del gruppo.
#let accento = if colore == "" { black } else { rgb(colore) }
#let palette = (
  accento: accento,
  // variante schiarita per i testi sugli sfondi scuri: contrasto sopra 4,5:1
  accento-chiaro: if colore == "" { luma(230) } else { color.mix((accento, 72%), (white, 28%)) },
  scuro: rgb("#0e0e10"),
  su-scuro: luma(242),
  su-scuro-tenue: luma(190),
  inchiostro: luma(25),
  tenue: luma(110),
  filetto: luma(205),
  zebra: luma(246),
)

// Nessun logo se in dati/gruppo.toml il percorso è vuoto.
#let logo(..dimensioni) = if info.logo != "" { image("/" + info.logo, ..dimensioni) }

// Nome del gruppo, email cliccabile e università.
#let mittente = {
  text(size: 15pt, weight: "bold", info.nome)
  if info.email != "" {
    linebreak()
    text(size: 9.5pt, link("mailto:" + info.email, info.email))
  }
  linebreak()
  text(size: 9pt, fill: palette.tenue)[Università degli Studi di Padova \ Corso di Ingegneria del Software]
}

// Prima pagina delle lettere: logo e mittente a sinistra, `destra` a destra.
#let carta-intestata(destra) = {
  grid(
    columns: (auto, 1fr, auto),
    column-gutter: 1em,
    align: (left + horizon, left + horizon, right + horizon),
    logo(height: 1.8cm), mittente, destra,
  )
  v(0.3cm)
  line(length: 100%, stroke: 0.8pt + palette.accento)
}

// Occhiello sopra il titolo: tipo di documento in maiuscolo spaziato, nel colore d'accento.
#let occhiello(testo, size: 10pt, fill: palette.accento) = text(size: size, weight: "bold", tracking: 0.18em, fill: fill, hyphenate: false, upper(testo))

// "https://gruppo.github.io/docs/" -> "gruppo.github.io/docs": l'indirizzo resta cliccabile ma non si spezza
#let sito-breve = info.sito.replace("https://", "").replace("http://", "").trim("/")

// Fascia scura a tutta larghezza in testa alla prima pagina di copertine e verbali:
// logo, nome del gruppo, contatti, eventuale elenco dei membri e un blocco `destra`.
// Va chiamata all'inizio della pagina: sposta il contenuto che segue sotto la fascia.
#let fascia(altezza: 5.6cm, destra: none, membri: false) = {
  let nomi = gruppo.at("membro", default: ()).map(m => m.nome + " " + m.cognome)
  place(top + left, dx: -margini.x, dy: -margini.top, block(
    width: larghezza-pagina,
    height: altezza,
    fill: palette.scuro,
    inset: (x: margini.x, y: 0pt),
  )[
    #set text(fill: palette.su-scuro)
    #show link: set text(fill: palette.su-scuro)
    #align(horizon, grid(
      columns: (auto, 1fr, auto),
      column-gutter: 1cm,
      align: (left + horizon, left + horizon, right + horizon),
      logo(height: calc.min(altezza - 2.6cm, 4.6cm)),
      [
        #set par(justify: false)
        // a capo tra università e corso; nelle colonne strette "di Padova" va a capo intero
        #occhiello([Università degli Studi #box[di Padova] \ Ingegneria del Software], size: 7.5pt, fill: palette.accento-chiaro)
        #v(0.1cm)
        #text(size: if membri { 26pt } else { 18pt }, weight: "bold", hyphenate: false, info.nome)
        #v(0.1cm)
        #text(size: 9.5pt, fill: palette.su-scuro-tenue)[
          #if info.email != "" [#link("mailto:" + info.email, info.email)]
          // accanto al blocco `destra` la colonna è stretta: un contatto per riga
          #if info.email != "" and info.sito != "" { if destra != none { linebreak() } else [ · ] }
          #if info.sito != "" [#box(link(info.sito, sito-breve))]
        ]
        #if membri and nomi.len() > 0 [
          #v(0.25cm)
          #text(size: 9pt, fill: palette.su-scuro-tenue, nomi.map(box).join[~· ])
        ]
      ],
      if destra != none { destra } else { [] },
    ))
  ])
  place(top + left, dx: -margini.x, dy: -margini.top + altezza, rect(width: larghezza-pagina, height: 3pt, fill: palette.accento))
  v(altezza - margini.top + 0.9cm)
}

// Riquadro con filetto d'accento a sinistra: scheda dei dati di copertina e verbali.
#let riquadro(corpo) = block(
  width: 100%,
  fill: palette.zebra,
  radius: 4pt,
  inset: (x: 1.1em, y: 0.9em),
  stroke: (left: 3pt + palette.accento),
  corpo,
)

// Regole comuni a pagine e slide: testo, tabelle, liste, link e codice.
#let base(corpo) = {
  let accento = palette.accento
  set text(font: "New Computer Modern", size: 11pt, lang: "it", region: "IT", fill: palette.inchiostro)
  set par(justify: true, leading: 0.7em, spacing: 1em)

  // tabelle: intestazione colorata, righe alternate, solo filetti orizzontali
  set table(
    stroke: (_, _) => (bottom: 0.5pt + palette.filetto),
    inset: (x: 8pt, y: 7pt),
    align: (_, y) => if y == 0 { center + horizon } else { left + horizon },
    fill: (_, y) => if y == 0 { accento } else if calc.even(y) { palette.zebra },
  )
  show table: set text(size: 10pt)
  show table: set par(justify: false)
  show table.cell.where(y: 0): set text(fill: white, weight: "bold")
  // didascalia sopra le tabelle, sotto le figure
  show figure.where(kind: table): set figure.caption(position: top)
  show figure.where(kind: table): set block(breakable: true)
  // la didascalia non resta da sola in fondo alla pagina
  show figure.caption.where(position: top): it => block(sticky: true, it)
  show figure.caption: set text(size: 9.5pt, fill: palette.tenue)

  set list(marker: ([•], [–]), indent: 0.6em, body-indent: 0.8em)
  set enum(
    numbering: n => text(fill: accento, weight: "bold", str(n) + "."),
    indent: 0.6em,
    body-indent: 0.8em,
    spacing: 0.8em,
  )

  show link: set text(fill: accento)
  show raw: set text(size: 9.5pt)
  show raw.where(block: true): it => block(
    width: 100%,
    fill: palette.zebra,
    stroke: 0.5pt + palette.filetto,
    radius: 3pt,
    inset: 10pt,
    it,
  )
  corpo
}

// Pagina A4: intestazione con titolo e logo (dalla seconda pagina), piè di pagina con
// etichetta e "Pagina X di Y". Uso: #show: stile.with(titolo: "...", etichetta: "...")
#let stile(corpo, titolo: none, etichetta: none) = {
  let accento = palette.accento
  let filetto = line(length: 100%, stroke: 0.5pt + palette.filetto)

  set page(
    paper: "a4",
    margin: margini,
    // la prima pagina è la copertina o la carta intestata
    header: context if counter(page).get().first() > 1 {
      set text(size: 9pt, fill: palette.tenue)
      stack(
        dir: ttb,
        spacing: 6pt,
        grid(columns: (1fr, auto), align: (left + horizon, right + horizon), titolo, logo(height: 0.8cm)),
        filetto,
      )
    },
    footer: context {
      set text(size: 9pt, fill: palette.tenue)
      stack(
        dir: ttb,
        spacing: 6pt,
        filetto,
        grid(
          columns: (1fr, auto),
          etichetta, [Pagina #counter(page).display() di #counter(page).final().first()],
        ),
      )
    },
  )

  // al massimo quattro livelli numerati
  set heading(numbering: (..n) => if n.pos().len() <= 4 { numbering("1.1", ..n) })
  let numero(it) = if it.numbering != none {
    counter(heading).display(it.numbering)
    h(0.6em)
  }
  show heading.where(level: 1): it => {
    set text(size: 16pt, weight: "bold", fill: accento)
    block(width: 100%, above: 2em, below: 1em, sticky: true, stack(
      dir: ttb,
      spacing: 0.45em,
      { numero(it); it.body },
      line(length: 100%, stroke: 0.8pt + accento),
    ))
  }
  show heading.where(level: 2): it => {
    set text(size: 13pt, weight: "bold", fill: accento)
    block(above: 1.6em, below: 0.8em, sticky: true, { numero(it); it.body })
  }
  show heading.where(level: 3): it => {
    set text(size: 11.5pt, weight: "bold", style: "italic", fill: accento)
    block(above: 1.3em, below: 0.6em, sticky: true, { numero(it); it.body })
  }
  show outline: set heading(numbering: none)
  show outline.entry.where(level: 1): set text(weight: "bold")

  show: base
  corpo
}
