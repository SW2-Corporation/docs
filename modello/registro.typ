// Registro delle modifiche letto da X.registro.csv (versione,data,autore,verificatore,descrizione).
// Le righe restano in ordine LIFO, come nel file: la prima è la più recente.
#import "stile.typ": palette

// csv() restituisce anche l'intestazione: le righe dati partono dalla seconda
#let righe-registro(registro) = (
  registro.slice(calc.min(1, registro.len())).filter(r => r.len() == 5).map(r => r.map(campo => campo.trim()))
)

// L'approvazione del Responsabile non ha verificatore e la descrizione inizia con "Approvazione".
#let approvazione(riga) = riga.at(3) == "" and riga.at(4).starts-with("Approvazione")

#let tabella-registro(righe) = {
  show table: set text(size: 8.5pt)
  table(
    columns: (auto, auto, 1fr, auto, auto),
    inset: (x: 5pt, y: 5pt),
    align: (x, y) => if y == 0 or x < 2 { center + horizon } else { left + horizon },
    table.header([Versione], [Data], [Descrizione], [Autore], [Verificatore]),
    ..righe
      .map(((versione, data, autore, verificatore, descrizione)) => (
        text(fill: palette.accento, weight: "bold", versione),
        data,
        descrizione,
        autore,
        if verificatore == "" [—] else { verificatore },
      ))
      .flatten(),
    ..if righe.len() == 0 { (table.cell(colspan: 5, align: center)[Nessuna modifica ancora verificata.],) },
  )
}
