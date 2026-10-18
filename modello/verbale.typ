// Si compila indicando il verbale da rendere:
// typst compile --root . modello/verbale.typ out.pdf --input dati=/documenti/verbali/interni/AAAA-MM-GG.toml
// Niente copertina, versione o registro: un verbale non ha storia di revisione.
#import "comuni.typ": *
#import "stile.typ": carta-intestata, info, occhiello, palette, stile
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
#let titolo = "Verbale " + verbale.tipo + " " + data

#set document(title: titolo, author: campo("redattore"))
#show: stile.with(titolo: titolo, etichetta: info.nome)
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

#carta-intestata[
  #occhiello("Verbale " + verbale.tipo) \
  #text(size: 14pt, weight: "bold", data)
]
#v(0.3cm)

#let durata-riunione = durata(campo("inizio"), campo("fine"))
#let assenti = elenco("assenti")
#let interno = verbale.tipo == "interno"
#let voce(etichetta, valore) = (text(fill: palette.tenue, etichetta), grid.cell(colspan: 3, valore))
#grid(
  columns: (auto, 1fr, auto, 1fr),
  column-gutter: 1em,
  row-gutter: 0.7em,
  text(fill: palette.tenue)[Orario],
  [#campo("inizio")–#campo("fine") #if durata-riunione != none [(#durata-riunione)]],
  text(fill: palette.tenue)[Redattore], campo("redattore"),
  text(fill: palette.tenue)[Luogo], campo("luogo"),
  text(fill: palette.tenue)[Verificatore], campo("verificatore"),
  // un verbale interno ha solo membri del gruppo: basta una riga, la tabella serve con gli esterni
  ..if interno { voce[Partecipanti][#elenco("partecipanti").join(", ")] },
  ..if interno and assenti.len() > 0 { voce[Assenti][#assenti.join(", ")] },
)
#if verbale.tipo == "esterno" {
  let approvazione = campo("approvazione_esterna")
  v(0.2cm)
  [#text(fill: palette.tenue)[Approvazione del proponente:] #if approvazione == "" [in attesa] else [#approvazione]]
}

#if not interno {
  // la colonna Presenza serve solo se qualcuno manca
  let presente = if assenti.len() > 0 { "Presente" } else { "" }
  let persone = (
    ..elenco("partecipanti").map(nome => (nome: nome, azienda: info.nome, presenza: presente)),
    ..elenco("esterni").map(e => (nome: e.nome, azienda: e.azienda, ruolo: e.ruolo, presenza: presente)),
    ..assenti.map(nome => (nome: nome, azienda: info.nome, presenza: "Assente")),
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
      // basta il numero: verifica.py accetta solo decisioni di questo verbale
      ..elenco("azione")
        .map(a => (a.decisione.split(".").last(), a.descrizione, a.assegnatario, data-it(a.scadenza), issue(a.at("issue", default: ""))))
        .flatten(),
    ),
    caption: [Azioni assegnate],
  )
}
