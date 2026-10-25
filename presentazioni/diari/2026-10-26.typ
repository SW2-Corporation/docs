#import "/modello/slide.typ": presentazione, slide
#import "/modello/comuni.typ": costo-consuntivo, costo-totale, euro

#show: presentazione.with(
  evento: "Diario di bordo",
  data: "2026-10-26",
  versione: "1.0.0",
  aggiornato: "2026-10-24",
  titolo: "Da 2026-10-19 a 2026-10-25",
)

#slide(titolo: "Fatto e da fare")[
  #grid(
    columns: (1fr, 1fr),
    column-gutter: 1.5cm,
    [
      *Fatto*
      - Valutazione dei capitolati
      - Incontri con i proponenti + verbali
      - Prima iterazione del WoW con template per documenti
      - Suddivisione dei ruoli per fare pratica
      - Prima versione di Gantt, cruscotto, diari
      - Verbali interni pubblicati
    ],
    [
      *Da fare*
      - 2026-10-27: scelta definitiva del capitolato
      - 2026-10-29: documenti per la candidatura
      - 2026-10-30: invio candidatura
    ],
  )
]

#slide(titolo: "Difficoltà e dubbi")[
  *Difficoltà*
  - Incontri col team al completo per discussioni più importanti
  - Lavoro asincrono con revisione PR bloccante
  - Suddivisione delle attività in issue _ragionevolmente_ atomiche
  - Gestione carico di lavoro dei diversi ruoli

  *Dubbi*
  - Come stabilire il _ragionevolmente_ atomico?
  - Come suddividere i ruoli in modo da avere lavoro settimanale omogeneo per ciascun membro?
]
