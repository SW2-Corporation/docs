#import "/modello/slide.typ": presentazione, slide
#import "/modello/stile.typ": palette

#show: presentazione.with(
  evento: "Lezione rovesciata",
  data: "2026-11-05",
  titolo: "Come facciamo documentazione",
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

#slide(titolo: "Il percorso")[
  #grid(
    columns: (1fr, 1fr),
    column-gutter: 1.5cm,
    [
      *Teoria*
      - La documentazione è un processo
      - Cosa chiede il regolamento
      - Versione, verifica, approvazione
      - Qualità di un documento
    ],
    [
      *Pratica*
      - Documenti come codice
      - Ciclo di vita e flusso di lavoro
      - Controlli automatici e verifica
      - Pubblicazione e cosa miglioriamo
    ],
  )
]

#slide(titolo: "La documentazione è un processo")[
  - Processo: attività correlate che trasformano ingressi in uscite, secondo regole date, consumando risorse.
  - ISO/IEC 12207 la mette tra i *processi di supporto*: serve i processi primari, non vive da sola.
  - Attività del processo:
    + pianificare: quali documenti, per chi, quando;
    + progettare: struttura e modelli;
    + produrre: scrivere, verificare, rilasciare;
    + mantenere: aggiornare con versioni tracciate.
  - Si norma prima di fare: ogni attività ha una procedura nelle Norme di Progetto.
]

#slide(titolo: "Cosa chiede il regolamento")[
  - Il gruppo si dota di un _way of working_: le Norme di Progetto sono un documento *esecutivo*, non narrativo.
  - Verbali: breve rendiconto delle riunioni, con ordine del giorno, decisioni e azioni.
  - Glossario: spiega ogni termine specializzato.
  - Tutti i documenti stanno in un repository, *sotto controllo di versione*.
  - Ogni documento ha il proprio registro delle modifiche.
]

#slide(titolo: "Versione, verifica, approvazione")[
  - *Versione*: identifica uno stato del documento. Non cambia mai senza una verifica.
  - *Verifica*: "ho fatto bene il prodotto?". La fa una persona diversa dall'autore.
  - *Approvazione*: autorizza il rilascio. Non è una verifica.
  - *Baseline*: versione approvata, modificabile solo con procedure formali.
  - *Registro delle modifiche*: modifiche logiche verificate, non il log dei commit.
]

#slide(titolo: "Qualità di un documento")[
  #grid(
    columns: (1fr, 1fr),
    column-gutter: 1.5cm,
    [
      *Cosa deve essere*
      - leggibile, per un lettore noto
      - coerente con verbali e regolamento
      - tracciabile: ogni affermazione ha una fonte
      - verificabile con una lista di controllo
    ],
    [
      *Come si scrive*
      - frasi brevi su un solo tema
      - verbi attivi
      - elenchi invece di narrazione
      - lessico del corso: "Lettera di Presentazione", "decisioni prese", "lo sprint"
    ],
  )
]

#slide(titolo: "Documenti come codice")[
  #grid(
    columns: (1.1fr, 1fr),
    column-gutter: 1cm,
    [
      - Un repository `docs`, pubblico, su GitHub.
      - Documenti in *Typst*, verbali in *TOML*, registri e dati in *CSV* e TOML.
      - Un modello comune: copertina, registro, stile, slide.
      - Ogni modifica passa da issue, branch e pull request.
    ],
    [
      #set text(size: 14pt)
      ```
      dati/          gruppo, ruoli, ore
      documenti/
        esterni/     con registro
        interni/     Norme di Progetto
        lettere/     AAAA-MM-GG.typ
        verbali/     AAAA-MM-GG.toml
      presentazioni/ diari di bordo
      modello/       modello Typst
      strumenti/     controlli e sito
      ```
    ],
  )
]

#slide(titolo: "Tipi di documento")[
  #set text(size: 16pt)
  #table(
    columns: (auto, auto, auto, 1fr),
    align: left + horizon,
    inset: 8pt,
    table.header([*Tipo*], [*Versione*], [*Registro*], [*Note*]),
    [Documenti con registro], [sì], [sì], [copertina, registro, indice, introduzione],
    [Lettera di Presentazione], [no, solo data], [no], [una per consegna, in cima al sito],
    [Verbali], [sì, da 1.0.0], [no], [TOML impaginato dal modello],
    [Diari di bordo], [sì, da 1.0.0], [no], [slide settimanali per i docenti],
  )
]

#slide(titolo: "Ciclo di vita di un documento")[
  #v(0.5cm)
  #catena(
    passo("Bozza", nota: "in lavorazione"),
    passo("In verifica", nota: "pull request aperta"),
    passo("Verificato", nota: "riga nel registro"),
    passo("Approvato", nota: "riga del Responsabile"),
  )
  #v(0.8cm)
  - Versioni X.Y.Z: Z per una modifica minore, Y per una sostanziale, X solo con l'approvazione.
  - Solo la riga di approvazione porta il documento sul sito: le bozze non si pubblicano.
]

#slide(titolo: "Dal lavoro a main")[
  #v(0.3cm)
  #catena(
    passo("Issue", nota: "criteri di accettazione"),
    passo("Branch", nota: "documento/argomento"),
    passo("Pull request", nota: "Closes #N"),
    passo("Verifica", nota: "un altro membro"),
    passo("Merge", nota: "chiude la issue"),
  )
  #v(0.6cm)
  - Nessuno scrive direttamente su `main`: contiene solo lavoro verificato.
  - Commit in italiano, con nome e cognome, che citano la issue: "Rif. \#12".
  - `main` è protetto: serve il controllo `verifica` verde e l'approvazione di un altro membro.
]

#slide(titolo: "Registro e verbali sono dati")[
  #grid(
    columns: (1fr, 1fr),
    column-gutter: 1cm,
    [
      *Registro delle modifiche (CSV)*
      #set text(size: 13pt)
      ```
      versione,data,autore,verificatore,descrizione
      0.1.0,2026-11-01,Matteo Bellato,
        Alessandro Paduret,Prima versione
        registrata e orari fissi ...
      ```
      #set text(size: 18pt)
      Copertina e piè di pagina leggono la versione dalla prima riga.
    ],
    [
      *Verbale (TOML)*
      #set text(size: 13pt)
      ```toml
      tipo = "interno"
      data = 2026-10-15
      versione = "1.0.0"
      redattore = "Matteo Bellato"
      verificatore = "Alessandro Paduret"
      ordine_del_giorno = [...]
      [[punto]]
      titolo = "Prima rotazione dei ruoli"
      ```
      #set text(size: 18pt)
      Il modello lo impagina: stessa struttura per tutti.
    ],
  )
]

#slide(titolo: "Controlli automatici")[
  - `strumenti/verifica.py` controlla tutto il repository; il workflow `Verifica` lo esegue a ogni pull request.
  - Ogni problema è una riga: percorso, riga, codice, messaggio.
    - *E*: errore, ferma la pull request.
    - *W*: avviso, da risolvere prima del rilascio.
  - Cosa controlla: registro, versioni e persone diverse; date AAAA-MM-GG; titoli e lessico; schema dei verbali; diari.
  - Leggibilità: indice Gulpease sopra la soglia del gruppo (40).
]

#slide(titolo: "Verifica umana")[
  La macchina controlla la forma, il verificatore controlla il contenuto.
  + La struttura segue le norme.
  + Il contenuto risponde allo scopo ed è coerente con verbali e regolamento.
  + Ogni affermazione verificabile ha una fonte.
  + Le convenzioni sono rispettate.
  + I controlli automatici sono verdi.
  + Versione e registro sono coerenti con la modifica.

  L'esito va nella pull request, punto per punto.
]

#slide(titolo: "Pubblicazione")[
  - A ogni merge su `main` il sito si rigenera da solo.
  - Mostra solo ciò che è rilasciato: documenti approvati, Lettere di Presentazione, verbali, diari.
  - Ordine dal più recente, con la Lettera di Presentazione in cima.
  - Ogni documento mostra versione e data dell'ultimo aggiornamento.
  - Il cruscotto legge ore e costi da `dati/` e li confronta con le soglie.
]

#slide(titolo: "Cosa abbiamo imparato")[
  #grid(
    columns: (1fr, 1fr),
    column-gutter: 1.5cm,
    [
      *Funziona*
      - Gli errori di forma non arrivano più ai verificatori.
      - Versione e data non vanno più aggiornate a mano.
      - La storia di ogni modifica è tracciata.
    ],
    [
      *Da migliorare*
      - Le pull request in attesa di verifica bloccano il lavoro.
      - Mancano norme per alcuni casi, per esempio le presentazioni.
      - Ogni lacuna diventa una modifica alle Norme di Progetto.
    ],
  )
]

#slide(titolo: "Domande")[
  #v(1fr)
  #align(center)[
    #text(size: 30pt, weight: "bold")[Grazie]
    #v(0.4cm)
    Repository: `github.com/SW2-Corporation/docs`
  ]
  #v(1fr)
]
