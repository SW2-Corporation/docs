// Tabella delle persone presenti a una riunione. Ogni persona è un dizionario
// (nome:, azienda:, ruolo:, presenza:); una colonna compare solo se qualcuno la valorizza.
#let tabella-persone(persone) = {
  let colonne = (nome: [Nome], azienda: [Azienda], ruolo: [Ruolo], presenza: [Presenza])
  let campi = colonne.keys().filter(c => persone.any(p => p.at(c, default: "") != ""))
  table(
    columns: (1fr,) * campi.len(),
    table.header(..campi.map(c => colonne.at(c))),
    ..persone.map(p => campi.map(c => p.at(c, default: ""))).flatten(),
  )
}
