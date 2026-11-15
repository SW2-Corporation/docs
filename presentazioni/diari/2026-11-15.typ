#import "/modello/slide.typ": presentazione, slide

#show: presentazione.with(
  evento: "Diario di bordo",
  data: "2026-11-15",
  versione: "1.0.0",
  aggiornato: "2026-11-15",
  titolo: "Da 2026-11-08 a 2026-11-15",
)

#slide(titolo: "Fatto e da fare")[
  #grid(
    columns: (1fr, 1fr),
    column-gutter: 1.5cm,
    [
      *Fatto*
      - Impostate le milestone su GitHub
      - Preparazione domande per incontro kick-off con il proponente del C8
      - Scoperto che il proponente C8 ha deciso di seguire solo un gruppo
      - Organizzato incontro per martedì 17 novembre con nuova proponente C9
    ],
    [
      *Da fare*
      - Studio capitolato
      - Finire la preparazione delle domande per l'incontro con C9
      - Ripianificare il progetto
    ],
  )
]

#slide(titolo: "Difficoltà e dubbi")[
  *Difficoltà*
  - Cominciare un nuovo capitolato dopo aver passato 2 settimane a lavorare al C8

  *Dubbi*
  - Come delineare efficacemente il nuovo perimetro per C9  
]
