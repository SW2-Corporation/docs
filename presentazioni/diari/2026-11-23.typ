#import "/modello/slide.typ": presentazione, slide

#show: presentazione.with(
  evento: "Diario di bordo",
  data: "2026-11-23",
  versione: "1.0.0",
  aggiornato: "2026-11-22",
  titolo: "Da 2026-11-15 a 2026-11-22",
)

#slide(titolo: "Fatto e da fare")[
  #grid(
    columns: (1fr, 1fr),
    column-gutter: 1.5cm,
    [
      *Fatto*
      - Incontro kick-off con Zucchetti e verbale approvato (\#147, \#148)
      - Apertura Sprint 2 e rotazione ruoli (\#137)
      - Ripartenza C9: consuntivo 0 € (ore C8 isolate a carico nostro, \#131, \#132)
      - Apertura issue operative per PoC e requisiti (\#138--\#146)
    ],
    [
      *Da fare*
      - 2026-11-23: proposta date a Zucchetti e norme per PoC
      - 2026-11-25: setup ambiente PoC (OpenCode e OpenSpec)
      - 2026-11-29: testbed a difetti noti per validazione
      - 2026-11-30: chiusura Sprint 2 e prototipo di verifica
    ],
  )
]

#slide(titolo: "Difficoltà e dubbi")[
  *Difficoltà*
  - Coordinamento disponibilità per il secondo incontro con il proponente (Dott. Piccoli)
  - Recupero dei tempi di pianificazione verso la scadenza RTB dell'11 dicembre
  - Delimitazione del PoC: isolare la fattibilità tecnologica critica per la RTB senza anticipare l'MVP

  *Dubbi*
  - Rendicontazione C8: conferma sull'isolamento a costo zero nel Piano di Progetto per non alterare i consuntivi di C9
  - Transizione ruoli su task aperti: modalità formale raccomandata per passaggio di consegne e riassegnazione issue su GitHub
]
