#import "/modello/lettera.typ": lettera
#import "/modello/comuni.typ": costo-totale, euro, gruppo, ore-membro, ripartizione

#show: lettera.with(
  data: "2026-10-29",
  oggetto: "Candidatura per l'assegnazione del capitolato d'appalto C8 (Sonar)",
  destinatari: ("Prof. Tullio Vardanega", "Prof. Riccardo Cardin"),
)

Egregi Professori Tullio Vardanega e Riccardo Cardin,

con la presente lettera il gruppo SW2 Corporation presenta formalmente la propria candidatura per l'assegnazione del capitolato d'appalto:

#align(center)[
  *C8 - Sonar: documentazione vivente di uno store Shopify* \
  _Proponente: Halue S.r.l. SB_
]

= Motivazione della candidatura

L'interesse verso il capitolato nasce dalla chiarezza dei requisiti, dallo stack tecnologico moderno, dalla richiesta di documentare l'architettura e le decisioni tecniche, e dalla disponibilità del proponente a dialogare sul perimetro del prodotto. L'analisi comparativa completa e le motivazioni di dettaglio sono consultabili nel documento #link("https://sw2-corporation.github.io/docs/Valutazione_dei_capitolati_v1.0.0.html")[Valutazione dei capitolati (versione 1.0.0)].

= Impegno contrattuale

Come esposto in dettaglio nella Dichiarazione degli impegni, il gruppo assume formalmente l'impegno a realizzare il prodotto e la documentazione associata rispettando i seguenti vincoli:

- *Costo complessivo preventivato:* #euro(costo-totale)\;
- *Scadenza ultima di consegna prevista:* #gruppo.progetto.consegna_prevista\;
- *Monte ore complessivo:* #ripartizione.map(ore-membro).sum() ore di lavoro produttivo, tra #calc.min(..ripartizione.map(ore-membro)) e #calc.max(..ripartizione.map(ore-membro)) ore per ciascuno dei sei componenti, ripartite sui sei ruoli previsti dal regolamento.

= Prodotti consegnati

La documentazione a supporto della candidatura è consultabile sul sito web del gruppo e nel repository pubblico GitHub:

- *Sito web della documentazione:* #link("https://sw2-corporation.github.io/docs/")[https://sw2-corporation.github.io/docs/]
- *Repository pubblico GitHub:* #link("https://github.com/SW2-Corporation/docs")[https://github.com/SW2-Corporation/docs]
- *Composizione e ruoli del gruppo:* #link("https://sw2-corporation.github.io/docs/ruoli.html")[https://sw2-corporation.github.io/docs/ruoli.html]

Per tenere sotto controllo il progetto, il sito pubblica anche il #link("https://sw2-corporation.github.io/docs/cruscotto.html")[cruscotto di progetto] e la #link("https://sw2-corporation.github.io/docs/pianificazione.html")[pianificazione]. Dall'avvio del conteggio, il cruscotto confronta ore, costi e tempi, previsti e consuntivi, con le soglie fissate dal gruppo. La pianificazione mostra il diagramma di Gantt di fasi, attività e milestone. Entrambe le pagine si aggiornano automaticamente dai dati del repository.

Sottoponiamo alla vostra attenzione i seguenti documenti:

- *#link("https://sw2-corporation.github.io/docs/Valutazione_dei_capitolati_v1.0.0.html")[Valutazione dei capitolati (versione 1.0.0)]:* analisi comparativa dei dieci capitolati, criteri di valutazione, analisi dei rischi e motivazione della scelta;
- *#link("https://sw2-corporation.github.io/docs/Dichiarazione_degli_impegni_v1.0.0.html")[Dichiarazione degli impegni (versione 1.0.0)]:* piano orario per membro e per ruolo, regole e matrice di rotazione per sprint, rischi attesi con misure di mitigazione e preventivo economico;
- *#link("https://sw2-corporation.github.io/docs/#verbali")[Verbali interni del gruppo]:* resoconti di tutte le riunioni interne svolte dal 2026-10-12;
- *Verbali esterni con i proponenti:* #link("https://sw2-corporation.github.io/docs/Verbale_esterno_2026-10-20-c7.html")[verbale dell'incontro esplorativo del 2026-10-20 con Ergon Informatica S.r.l.] (con approvazione firmata) e #link("https://sw2-corporation.github.io/docs/Verbale_esterno_2026-10-20-c8.html")[verbale dell'incontro esplorativo del 2026-10-20 con Halue S.r.l. SB] (con approvazione via email del 2026-10-26).

= Componenti del gruppo

#figure(
  table(
    columns: (2fr, 1.2fr),
    align: (left, center),
    table.header([*Nominativo*], [*Matricola*]),
    [Davide Baraldo], [2082847],
    [Matteo Bellato], [2172263],
    [Patrizio Eleuteri], [2150446],
    [Oussama Mahdi], [2081617],
    [Alessandro Paduret], [2150445],
    [David Sirbu], [2137981],
  ),
  caption: [Componenti del gruppo SW2 Corporation],
)

Ringraziandovi per l'attenzione e la disponibilità, restiamo a vostra disposizione per ogni chiarimento.

Cordiali saluti,

#v(0.6cm)
#align(right)[
  *Il gruppo SW2 Corporation* \
  #text(size: 9pt)[
    Matteo Bellato (Responsabile)
  ]
]
