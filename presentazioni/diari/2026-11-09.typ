#import "/modello/slide.typ": presentazione, slide

#show: presentazione.with(
  evento: "Diario di bordo",
  data: "2026-11-09",
  versione: "1.0.0",
  aggiornato: "2026-11-08",
  titolo: "Da 2026-11-01 a 2026-11-08",
)

#slide(titolo: "Fatto e da fare")[
  #grid(
    columns: (1fr, 1fr),
    column-gutter: 1.5cm,
    [
      *Fatto*
      - Aggiornato le Norme di Progetto (#104)(#105)(#106)
      - Introdotta la tracciabilità delle modifiche e versionamento Glossario (#117)
      - Aggiornamento ruoli.csv per ruoli correnti (#110)
      - Verbali interni (#108)(#115)
    ],
    [
      *Da fare*
      - 2026-11-10: Redigere bozza iniziale Analisi Requisiti per C8 e lista quesiti tecnici per incontro di kick-off con Halue
      - 2026-11-11: Impostare struttura del Piano di Qualifica
      - 2026-11-12: Definire architettura preliminare del PoC
      - 2026-11-13: Redigere prima bozza del Piano di Progetto
      - Introdurre maggior flessibilità nei ruoli
    ],
  )
]

#slide(titolo: "Difficoltà e dubbi")[
  *Difficoltà*
  -Formalizzazione di requisiti e vincoli architetturali in attesa del primo incontro operativo post-aggiudicazione con Halue.

  *Dubbi*
  - Come formalizzare correttamente nell'AdR le assunzioni tecniche provvisorie non ancora confermate a verbale dal proponente.
]
