#import "comuni.typ": *
#import "stile.typ": info, stile
#import "copertina.typ": copertina
#import "registro.typ": approvazione, righe-registro, tabella-registro

#let documento(
  titolo: "",
  sottotitolo: none,
  uso: "esterno",
  destinatari: (),
  registro: (),
  corpo,
) = {
  let righe = righe-registro(registro)
  let ultima = righe.at(0, default: none)
  let versione = if ultima != none { ultima.at(0) }
  let aggiornato = if ultima != none { ultima.at(1) }
  let approvato = ultima != none and approvazione(ultima)
  // chi ha scritto e chi ha verificato, in ordine di prima comparsa
  let modifiche = righe.filter(r => not approvazione(r)).rev()
  let persone(colonna) = modifiche.map(r => r.at(colonna)).filter(n => n != "").dedup()

  set document(
    title: titolo + if versione != none { " v" + versione } else { " (bozza)" },
    author: persone(2),
  )
  show: stile.with(
    titolo: titolo,
    etichetta: info.nome + " · " + if versione != none { "v" + versione + " · aggiornato il " + aggiornato } else { "bozza" },
  )

  copertina(
    tipo: "Documento " + uso,
    titolo: titolo,
    sottotitolo: sottotitolo,
    voci: (
      ("Versione", versione),
      ("Ultimo aggiornamento", aggiornato),
      ("Stato", if ultima == none { "Bozza" } else if approvato { "Approvato" } else { "In verifica" }),
      ("Uso", (esterno: "Esterno", interno: "Interno").at(uso, default: uso)),
      ("Destinatari", destinatari.join(linebreak())),
      ("Redattori", persone(2).join(", ")),
      ("Verificatori", persone(3).join(", ")),
      ("Approvazione", if approvato { ultima.at(2) }),
      ("Capitolato", gruppo.progetto.capitolato),
      ("Proponente", gruppo.progetto.proponente),
    ),
  )

  heading(numbering: none, outlined: false, bookmarked: true)[Registro delle modifiche]
  tabella-registro(righe)

  outline(title: [Indice], depth: 3)
  context {
    if query(figure.where(kind: image)).len() > 0 {
      outline(title: [Elenco delle figure], target: figure.where(kind: image))
    }
    if query(figure.where(kind: table)).len() > 0 {
      outline(title: [Elenco delle tabelle], target: figure.where(kind: table))
    }
  }
  pagebreak()

  corpo
}
