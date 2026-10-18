// Dati e funzioni condivisi da modelli e documenti.

#let gruppo = toml("/dati/gruppo.toml")
#let preventivo = toml("/dati/preventivo.toml")

#let ruoli = ("Responsabile", "Amministratore", "Analista", "Progettista", "Programmatore", "Verificatore")

#let data-it(d) = d.display("[year]-[month]-[day]")

#let slug(termine) = lower(termine).replace(" ", "-")

#let g(termine) = {
  let voce = [#termine#sub[G]]
  let sito = gruppo.gruppo.sito
  if sito == "" { voce } else { link(sito + "glossario.html#" + slug(termine), voce) }
}

#let rif-web(titolo, url, accesso) = [#titolo, #link(url) (ultimo accesso: #accesso)]

#let rif-doc(nome, versione) = [#nome v#versione]

// 12600 -> "12.600,00 €"
#let euro(x) = {
  let cent = int(calc.round(x * 100))
  let intero = str(calc.quo(cent, 100))
  let gruppi = ()
  while intero.len() > 3 {
    gruppi.insert(0, intero.slice(-3))
    intero = intero.slice(0, -3)
  }
  gruppi.insert(0, intero)
  let resto = calc.rem(cent, 100)
  gruppi.join(".") + "," + (if resto < 10 { "0" }) + str(resto) + "\u{a0}€"
}

// Preventivo: ore per membro e ruolo da dati/preventivo.toml.

#let ripartizione = preventivo.at("ripartizione", default: ())
#let ore-membro(p) = ruoli.map(r => p.at(r, default: 0)).sum()
#let ore-ruolo(r) = ripartizione.map(p => p.at(r, default: 0)).sum(default: 0)
#let costo-ruolo(r) = ore-ruolo(r) * preventivo.tariffe.at(r)
#let costo-totale = ruoli.map(costo-ruolo).sum()

// Costo consuntivo: ore reali di dati/ore.csv alle tariffe del regolamento.
#let costo-consuntivo() = (
  csv("/dati/ore.csv")
    .slice(1)
    .filter(r => r.len() == 5)
    .map(r => float(r.at(3).trim()) * preventivo.tariffe.at(r.at(2).trim(), default: 0))
    .sum(default: 0)
)

#let impegni() = {
  let consegna = gruppo.progetto.consegna_prevista
  let voci = ()
  if consegna != "" { voci.push([Scadenza ultima di consegna prevista: *#consegna*.]) }
  if costo-totale > 0 { voci.push([Costo preventivato: *#euro(costo-totale)*.]) }
  list(..voci)
}

#let tabella-ore() = figure(
  table(
    columns: (1fr,) + (auto,) * 7,
    align: (x, y) => if y == 0 { center + bottom } else if x == 0 { left } else { right },
    table.header([Membro], ..ruoli.map(r => rotate(-90deg, reflow: true, r)), [Totale]),
    ..ripartizione.map(p => (p.membro, ..ruoli.map(r => str(p.at(r, default: 0))), str(ore-membro(p)))).flatten(),
    [*Totale*], ..ruoli.map(r => [*#ore-ruolo(r)*]), [*#ripartizione.map(ore-membro).sum(default: 0)*],
  ),
  caption: [Ore preventivate per membro e ruolo],
)

#let tabella-costi() = figure(
  table(
    columns: (1fr, auto, auto, auto),
    align: (x, _) => if x == 0 { left } else { right },
    table.header([Ruolo], [Ore], [Tariffa (€/h)], [Costo]),
    ..ruoli.map(r => (r, str(ore-ruolo(r)), str(preventivo.tariffe.at(r)), euro(costo-ruolo(r)))).flatten(),
    [*Totale*], [*#ruoli.map(ore-ruolo).sum()*], [], [*#euro(costo-totale)*],
  ),
  caption: [Costo preventivato per ruolo],
)
