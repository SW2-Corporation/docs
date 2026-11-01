#import "/modello/slide.typ": presentazione, slide

#show: presentazione.with(
  evento: "Diario di bordo",
  data: "2026-11-02",
  versione: "1.0.0",
  aggiornato: "2026-11-01",
  titolo: "Da 2026-10-26 a 2026-11-01",
)

#slide(titolo: "Fatto e da fare")[
  #grid(
    columns: (1fr, 1fr),
    column-gutter: 1.5cm,
    [
      *Fatto*
      - Scelta capitolato definitiva (\#27)
      - Lettera di Presentazione (\#35)
      - Dichiarazione degli impegni (\#29)
      - Invio candidatura (\#37)
    ],
    [
      *Da fare*
      - 2026-11-02: normare miglioramento dei processi
      - 2026-11-03: incontro per decisione su come procedere (in base al risultato)
      - 2026-11-03: retrospettiva sulla prima versione del WoW
      - 2026-11-04: inizio analisi dei requisiti
    ],
  )
]

#slide(titolo: "Difficoltà e dubbi")[
  *Difficoltà*
  - Gestione delle attività bloccanti (approvazione PR).
  - Stabilire deadline ragionevoli per le varie attività.

  *Dubbi*
  - Cambio ruolo con attività in corso, come gestire il passaggio di consegne?
  - In caso di \"malattia\" di un membro, è possibile definire un piano d'emergenza?
]


#slide(titolo: "Situazione di gruppo e costi")[
  *Situazione di gruppo*
  - Lavoro asincrono che viene distribuito durante un'incontro.
  - Carico sbilanciato a favore di alcuni ruoli.

  *Costi e avanzamento sprint*
  - Al momento N/A.
]
