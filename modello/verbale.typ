// Si compila indicando il verbale da rendere:
// typst compile --root . modello/verbale.typ out.pdf --input dati=/documenti/verbali/interni/AAAA-MM-GG.toml
// Niente copertina, versione o registro: un verbale non ha storia di revisione.
#import "comuni.typ": *
#import "stile.typ": fascia, info, occhiello, palette, riquadro, stile
#import "persone.typ": tabella-persone

#let percorso = sys.inputs.at("dati", default: none)
#if percorso == none {
  panic("indicare il verbale con --input dati=/documenti/verbali/<tipo>/AAAA-MM-GG.toml")
}
// anche senza "/" iniziale: Git Bash su Windows riscrive i percorsi che iniziano con "/"
#let verbale = toml(if percorso.starts-with("/") { percorso } else { "/" + percorso })
#let campo(chiave) = verbale.at(chiave, default: "")
#let elenco(chiave) = verbale.at(chiave, default: ())
#let data = data-it(verbale.data)
// con più verbali dello stesso tipo in un giorno il file ha un suffisso: AAAA-MM-GG-c7.toml
#let suffisso = percorso.match(regex("\d{4}-\d{2}-\d{2}-([a-z0-9]+)\.toml$"))
#let codice = if suffisso != none { upper(suffisso.captures.first()) }
#let titolo = "Verbale " + verbale.tipo + " " + data
#if codice != none { titolo += " " + codice }

#set document(title: titolo, author: campo("redattore"))
#show: stile.with(titolo: titolo, etichetta: info.nome)
// i testi del TOML non passano dal markup: apostrofi e virgolette tipografici come nei documenti
#show "'": smartquote(double: false)
#show "\"": smartquote()
// codici come R-MF-01 o RFO-19 non vanno a capo sul trattino
#show regex("\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+\b"): it => box(it)
// una riga di tabella non si spezza tra due pagine
#set table.cell(breakable: false)

// "18:00", "19:30" -> "1 h 30 min"; niente se gli orari non sono HH:MM
#let durata(inizio, fine) = {
  let orario = regex("^\d{2}:\d{2}$")
  if inizio.match(orario) == none or fine.match(orario) == none { return none }
  let minuti(t) = int(t.slice(0, 2)) * 60 + int(t.slice(3))
  let d = minuti(fine) - minuti(inizio)
  if d <= 0 { return none }
  (
    if d >= 60 { str(calc.quo(d, 60)) + " h" },
    if calc.rem(d, 60) > 0 { str(calc.rem(d, 60)) + " min" },
  ).filter(x => x != none).join(" ")
}

#let issue(url) = if url == "" [--] else {
  let numero = url.split("/").last()
  link(url, if numero.match(regex("^\d+$")) != none { "#" + numero } else { url })
}

#fascia(destra: align(right)[
  #occhiello("Verbale " + verbale.tipo, fill: palette.accento-chiaro) \
  #text(size: 22pt, weight: "bold", data)
  #if codice != none [\ #text(size: 22pt, weight: "bold", fill: palette.accento-chiaro, codice)]
])

#let durata-riunione = durata(campo("inizio"), campo("fine"))
#let assenti = elenco("assenti")
#let interno = verbale.tipo == "interno"
#let voce(etichetta, valore) = (text(fill: palette.tenue, etichetta), grid.cell(colspan: 3, valore))
#riquadro[
  #set text(size: 10.5pt)
  #set par(justify: false)
  #grid(
    columns: (auto, 1fr, auto, 1fr),
    column-gutter: 1.2em,
    row-gutter: 0.75em,
    ..if campo("titolo") != "" { voce[Oggetto][#campo("titolo")] },
    text(fill: palette.tenue)[Orario],
    [#campo("inizio")–#campo("fine") #if durata-riunione != none [(#durata-riunione)]],
    text(fill: palette.tenue)[Redattore], campo("redattore"),
    text(fill: palette.tenue)[Luogo], campo("luogo"),
    text(fill: palette.tenue)[Verificatore], campo("verificatore"),
    // un verbale interno ha solo membri del gruppo: basta una riga, la tabella serve con gli esterni
    ..if interno { voce[Partecipanti][#elenco("partecipanti").join(", ")] },
    ..if interno and assenti.len() > 0 { voce[Assenti][#assenti.join(", ")] },
    ..if not interno {
      let approvazione = campo("approvazione_esterna")
      voce[Approvazione del proponente][#if approvazione == "" [in attesa] else [#approvazione]]
    },
  )
]

#if not interno {
  // la colonna Presenza serve solo se qualcuno manca
  let presente = if assenti.len() > 0 { "Presente" } else { "" }
  // ruolo di progetto di ogni membro il giorno della riunione, da dati/ruoli.csv
  let periodi = csv("/dati/ruoli.csv").slice(1).filter(r => r.len() == 4).map(r => r.map(c => c.trim()))
  let ruolo(nome) = {
    let periodo = periodi.find(p => p.at(2) == nome and p.at(0) <= data and data <= p.at(1))
    if periodo == none { "" } else { periodo.at(3) }
  }
  let persone = (
    ..elenco("partecipanti").map(nome => (nome: nome, azienda: info.nome, ruolo: ruolo(nome), presenza: presente)),
    ..elenco("esterni").map(e => (nome: e.nome, azienda: e.azienda, ruolo: e.ruolo, presenza: presente)),
    ..assenti.map(nome => (nome: nome, azienda: info.nome, ruolo: ruolo(nome), presenza: "Assente")),
  )
  if persone.len() > 0 {
    v(0.3cm)
    figure(tabella-persone(persone), caption: [Partecipanti])
  }
}

= Ordine del giorno
#enum(..elenco("ordine_del_giorno"))

// la sintesi è facoltativa: un verbale è agenda, decisioni e azioni (PD1)
#if elenco("punto").len() > 0 [
  = Sintesi della riunione
  #for p in elenco("punto") [
    == #p.titolo
    #p.sintesi.trim().split(regex("\n\s*\n")).map(s => s.replace("\n", " ")).join(parbreak())
  ]
]

= Decisioni
#if elenco("decisione").len() == 0 [Nessuna decisione presa.] else {
  figure(
    table(
      columns: (auto, 3fr, 2fr),
      table.header([ID], [Decisione], [Motivazione]),
      ..elenco("decisione").map(d => (d.id, d.testo, d.motivazione)).flatten(),
    ),
    caption: [Decisioni prese],
  )
}

= Azioni
#if elenco("azione").len() == 0 [Nessuna azione assegnata.] else {
  figure(
    table(
      columns: (auto, 1fr, auto, auto, auto),
      table.header([Decisione], [Azione], [Assegnatario], [Scadenza], [Issue]),
      // ID completo della decisione per massima tracciabilità
      ..elenco("azione")
        .map(a => (a.decisione, a.descrizione, a.assegnatario, data-it(a.scadenza), issue(a.at("issue", default: ""))))
        .flatten(),
    ),
    caption: [Azioni assegnate],
  )
}
