#import "comuni.typ": *
#import "stile.typ": carta-intestata, info, occhiello, stile

// Lettera di Presentazione: ha la data, non la versione, e nessun registro.
#let lettera(
  data: "",
  oggetto: "",
  destinatari: ("Prof. Tullio Vardanega", "Prof. Riccardo Cardin"),
  corpo,
) = {
  let titolo = "Lettera di Presentazione " + data
  set document(title: titolo)
  show: stile.with(titolo: titolo, etichetta: info.nome)

  carta-intestata[
    #occhiello("Lettera di Presentazione") \
    #text(size: 14pt, weight: "bold", data)
  ]
  v(1cm)
  block[
    #set par(justify: false)
    #destinatari.join(linebreak()) \
    Università degli Studi di Padova
  ]
  v(0.8cm)
  [*Oggetto:* #oggetto]
  v(0.4cm)
  corpo
}
