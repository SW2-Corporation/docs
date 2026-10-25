// Modello del diario di bordo: copialo in presentazioni/diari/AAAA-MM-GG.typ
// e sostituisci ogni voce con i fatti della settimana. Al massimo 3 slide, 4 minuti.
// Il diario nasce alla 1.0.0; ogni modifica verificata aggiorna `aggiornato` e fa crescere
// Y se cambia il contenuto, Z negli altri casi.
#import "/modello/slide.typ": presentazione, slide
#import "/modello/comuni.typ": costo-consuntivo, costo-totale, euro

#show: presentazione.with(
  evento: "Diario di bordo",
  data: "AAAA-MM-GG",
  versione: "1.0.0",
  aggiornato: "AAAA-MM-GG",
  titolo: "Da AAAA-MM-GG a AAAA-MM-GG",
)

#slide(titolo: "Fatto e da fare")[
  #grid(
    columns: (1fr, 1fr),
    column-gutter: 1.5cm,
    [
      *Fatto*
      - Attività concluse, con il numero della issue
    ],
    [
      *Da fare*
      - Attività della prossima settimana, con la data
      - Prossima scadenza di lungo periodo, con la data
    ],
  )
]

#slide(titolo: "Difficoltà e dubbi")[
  *Difficoltà*
  - Problema incontrato e come lo state affrontando

  *Dubbi*
  - Domanda precisa a cui il docente può rispondere
]

#slide(titolo: "Situazione di gruppo e costi")[
  *Situazione di gruppo*
  - Come sta lavorando il gruppo: carico, collaborazione, assenze

  *Costi e avanzamento*
  - Costo consumato: #euro(costo-consuntivo()) su #euro(costo-totale) preventivati
  - Avanzamento rispetto al piano dello sprint
]
