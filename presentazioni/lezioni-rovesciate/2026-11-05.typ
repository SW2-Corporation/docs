#import "/modello/slide.typ": presentazione, slide
#import "/modello/stile.typ": palette

#show: presentazione.with(
  evento: "Lezione rovesciata",
  data: "2026-11-05",
  titolo: "Documentare: cosa, da dove, come",
)

// riquadro di uno stato o di un passo, per i diagrammi a frecce
#let passo(testo, nota: none) = box(
  stroke: 1pt + palette.accento,
  radius: 4pt,
  inset: (x: 10pt, y: 8pt),
  align(center)[*#testo* #if nota != none [\ #text(size: 13pt, fill: palette.tenue, nota)]],
)
#let freccia = text(size: 22pt, fill: palette.accento)[→]
#let catena(..passi) = align(center, grid(
  columns: passi.pos().len() * 2 - 1,
  column-gutter: 8pt,
  align: horizon,
  ..passi.pos().map(p => (p, freccia)).flatten().slice(0, -1),
))

// domanda aperta da portare in aula, con il dato che la motiva
#let domanda(testo, nota: none) = block(
  width: 100%,
  stroke: (left: 3pt + palette.accento),
  inset: (left: 14pt, y: 6pt),
  below: 0.8em,
  [*#testo* #if nota != none [\ #text(size: 14pt, fill: palette.tenue, nota)]],
)

// risposta provvisoria del gruppo, in fondo alla slide
#let risposta(corpo) = block(
  width: 100%,
  fill: palette.zebra,
  radius: 4pt,
  inset: 12pt,
  [#text(size: 14pt, fill: palette.tenue)[LA NOSTRA RISPOSTA PROVVISORIA] \ #corpo],
)

#slide(titolo: "Da dove parliamo")[
  - Sei persone, tre settimane di lavoro, tutto in un repository sotto controllo di versione.
  - 12 verbali, 33 pull request integrate, Norme di Progetto modificate in 11 commit in due settimane.
  - Portiamo domande aperte. Per ognuna diciamo la risposta provvisoria che ci siamo dati facendo.
  - Seguiamo la traccia della lezione:
    + A1: cosa documentare, per obbligo o per opportunità;
    + A2: con quali contenuti, tratti da dove;
    + A3: come produrre documentazione efficace ed efficiente.
]

#slide(titolo: "Cosa documentare (A1)")[
  #set text(size: 16pt)
  #grid(
    columns: (1.2fr, 1fr),
    column-gutter: 1.2cm,
    [
      *Per obbligo* #text(size: 13pt, fill: palette.tenue)[(PD1, slide 24)]
      - Piano di Progetto, Piano di Qualifica
      - Norme di Progetto, verbali, Glossario
      - Analisi dei Requisiti, Specifica Architetturale, Manuale Utente
      - Lettera di Presentazione, diario di bordo
    ],
    [
      *Per opportunità*
      - decisioni con codice e motivazione
      - ore, ruoli e pianificazione come dati
      - regole di stile e controlli che le applicano
    ],
  )
  #v(0.3cm)
  #risposta[Si documenta ciò che qualcuno rileggerà per decidere, per verificare o per riprendere un lavoro. Se non sappiamo dire chi lo rileggerà, forse non serve.]
]

#slide(titolo: "Domande su A1")[
  #domanda(
    "Un documento obbligatorio che nessuno rilegge è un obbligo assolto o un costo senza valore?",
  )
  #domanda(
    "PD1 chiede verbali come \"breve rendiconto\": agenda, decisioni, azioni. Quanto della discussione va scritto?",
    nota: "I nostri verbali hanno una sintesi per ogni punto. Serve a chi era assente, o è un costo?",
  )
  #domanda(
    "Si norma prima di fare. Come si norma bene un'attività che non si è mai svolta?",
    nota: "Noi: quattro modifiche alle Norme di Progetto decise il 2026-11-02, tutte su lacune scoperte lavorando.",
  )
]

#slide(titolo: "Con quali contenuti, tratti da dove (A2)")[
  #grid(
    columns: (1.1fr, 1fr),
    column-gutter: 1cm,
    [
      *Fonti*
      - regolamento e lezioni
      - capitolato e incontri con il proponente
      - decisioni interne, nei verbali
      - dati misurati: ore, ruoli, costi
    ],
    [
      #set text(size: 13pt)
      ```toml
      [[decisione]]
      id = "VI-2026-10-30.2"
      testo = "Consuntivare la conclusione
        della prima versione delle Norme
        di Progetto al 2026-10-29, ..."
      motivazione = "Permette al cruscotto
        di operare senza falsi allarmi ..."
      ```
    ],
  )
  #v(0.4cm)
  #risposta[
    - Ogni dato vive in un solo posto e i documenti lo leggono: versione e data dal registro, ore e costi da `dati/`.
    - Ogni affermazione verificabile cita una fonte: è un punto della lista di verifica.
  ]
]

#slide(titolo: "Domande su A2")[
  #domanda(
    "Se lo stesso dato serve a più documenti, dove deve vivere? E chi ne risponde?",
    nota: "Le ore compaiono nel Piano di Progetto, nel cruscotto e nel diario di bordo.",
  )
  #domanda(
    "Dai gruppi degli anni scorsi si prende la struttura, non il testo. Dove passa il confine?",
  )
  #domanda(
    "Il registro delle modifiche non è la storia dei commit. Si può generare dalle pull request senza perdere senso?",
    nota: "Chi decide cosa è una modifica da registrare?",
  )
]

#slide(titolo: "Documentazione efficace ed efficiente (A3)")[
  #grid(
    columns: (1fr, 1fr),
    column-gutter: 1.5cm,
    [
      *Efficace: qualità informativa*
      - un lettore noto per ogni documento
      - frasi brevi, elenchi, lessico del corso
      - verifica di un'altra persona, con una lista di controllo
    ],
    [
      *Efficiente: impiego di risorse*
      - un modello Typst comune: copertina, registro, stile
      - 45 controlli automatici a ogni pull request
      - sito rigenerato a ogni integrazione su `main`
    ],
  )
  #v(0.4cm)
  #risposta[La macchina controlla la forma, la persona controlla il contenuto. Ogni errore di forma che sfugge diventa un nuovo controllo.]
]

#slide(titolo: "Come lavoriamo oggi")[
  #v(0.3cm)
  #catena(
    passo("Issue", nota: "criteri di accettazione"),
    passo("Branch", nota: "documento/argomento"),
    passo("Pull request", nota: "controlli automatici"),
    passo("Verifica", nota: "un altro membro"),
    passo("Merge", nota: "chiude la issue"),
  )
  #v(0.8cm)
  #catena(
    passo("Bozza", nota: "in lavorazione"),
    passo("In verifica", nota: "pull request aperta"),
    passo("Verificato", nota: "riga nel registro"),
    passo("Approvato", nota: "riga del Responsabile"),
  )
  #v(0.6cm)
  - Su `main` arriva solo lavoro verificato. Sul sito arriva solo ciò che è approvato.
]

#slide(titolo: "Domande su A3")[
  #domanda(
    "Gli strumenti costano ore, e ognuno ne ha tra 80 e 95. Quanto investire in automazione all'inizio? Come si misura se ripaga?",
  )
  #domanda(
    "Un indice di leggibilità come Gulpease misura la qualità informativa, o solo la lunghezza di frasi e parole?",
  )
  #domanda(
    "Verifica rapida o verifica leggera? Come si distinguono?",
    nota: "Il diario del 2026-11-02 segnala le approvazioni come attività bloccante. Eppure metà delle nostre pull request è integrata entro 12 minuti dall'apertura.",
  )
]

#slide(titolo: "Le nostre domande, in breve")[
  #set text(size: 16pt)
  #grid(
    columns: (auto, 1fr),
    column-gutter: 0.6cm,
    row-gutter: 0.55cm,
    [*A1*], [Documento obbligatorio che nessuno rilegge: obbligo assolto o costo? \ Quanto della discussione va nel verbale? \ Come si norma un'attività mai svolta?],
    [*A2*], [Dove vive un dato usato da più documenti? \ Dal lavoro altrui: dove passa il confine tra struttura e testo? \ Il registro si può generare dalle pull request?],
    [*A3*], [Quanto investire in automazione, e come misurare se ripaga? \ Cosa misura davvero un indice di leggibilità? \ Verifica rapida o verifica leggera?],
  )
]
