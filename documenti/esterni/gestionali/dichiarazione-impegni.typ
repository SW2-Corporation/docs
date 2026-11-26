#import "/modello/documento.typ": documento
#import "/modello/comuni.typ": (
  costo-totale, euro, g, gruppo, impegni, ore-membro, ore-ruolo, rif-web, ripartizione, tabella-costi, tabella-ore,
)

#show: documento.with(
  titolo: "Dichiarazione degli impegni",
  sottotitolo: "Rideterminazione delle risorse orarie ed economiche a seguito del passaggio al capitolato C9",
  uso: "esterno",
  destinatari: ("Prof. Tullio Vardanega", "Prof. Riccardo Cardin"),
  registro: csv("dichiarazione-impegni.registro.csv"),
)

// Le righe delle tabelle non si spezzano tra due pagine.
#set table.cell(breakable: false)

#let ore-totali = ripartizione.map(ore-membro).sum()
#let ore-min = calc.min(..ripartizione.map(ore-membro))
#let ore-max = calc.max(..ripartizione.map(ore-membro))
#let perc(ore) = str(calc.round(ore / ore-totali * 100, digits: 1)).replace(".", ",") + "%"
#let num(x, cifre: 1) = str(calc.round(x, digits: cifre)).replace(".", ",")

// Turni e ore preventivate sprint per sprint: per ogni membro, ruolo e ore di ciascuno dei dieci sprint.
// Le ore per C9 si contano dal 2026-11-24: lo sprint 1 non ne ha e lo sprint 2 conta una sola settimana.
// dati/preventivo.toml riporta le somme per membro e ruolo: se non coincidono, la compilazione si ferma.
#let turni = (
  "Davide Baraldo": (("AN", 0), ("VE", 9), ("PO", 17), ("RE", 7), ("AN", 7), ("AM", 4), ("PR", 5), ("VE", 16), ("PO", 16), ("AM", 6)),
  "Matteo Bellato": (("AM", 0), ("AN", 8), ("PR", 16), ("VE", 13), ("PO", 8), ("VE", 7), ("AN", 6), ("PO", 15), ("AM", 8), ("RE", 6)),
  "Patrizio Eleuteri": (("RE", 0), ("AN", 8), ("VE", 18), ("PO", 12), ("PR", 5), ("RE", 4), ("PO", 6), ("AM", 8), ("VE", 15), ("PO", 11)),
  "Oussama Mahdi": (("AN", 0), ("RE", 4), ("AN", 17), ("VE", 11), ("AM", 4), ("PR", 6), ("RE", 4), ("PO", 15), ("VE", 15), ("PR", 11)),
  "Alessandro Paduret": (("PR", 0), ("AM", 4), ("RE", 8), ("AN", 15), ("VE", 8), ("PO", 8), ("PR", 7), ("RE", 8), ("PO", 17), ("VE", 13)),
  "David Sirbu": (("VE", 0), ("PO", 9), ("AM", 8), ("PR", 14), ("RE", 4), ("AN", 7), ("VE", 8), ("PR", 16), ("RE", 8), ("VE", 13)),
)
// Settimane contabilizzate per C9 in ogni sprint: dal 2026-11-24 alla consegna del 2027-03-19.
#let settimane = (0, 1, 2, 2, 2, 2, 2, 2, 2, 11 / 7)
#let sigle = (
  RE: "Responsabile", AM: "Amministratore", AN: "Analista", PR: "Progettista", PO: "Programmatore", VE: "Verificatore",
)

#let controllo-preventivo = for p in ripartizione {
  for (sigla, ruolo) in sigle {
    let somma = turni.at(p.membro).filter(c => c.at(0) == sigla).map(c => c.at(1)).sum(default: 0)
    assert.eq(somma, p.at(ruolo, default: 0), message: p.membro + ", " + ruolo + ": le ore per sprint non coincidono con dati/preventivo.toml")
  }
}

#let membri = turni.keys()
#let ore-sprint(s) = turni.values().map(t => t.at(s).at(1)).sum()
#let media(s) = ore-sprint(s) / membri.len()
// Ore settimanali a persona negli sprint da "da" ad "a", numerati da 1.
#let intensita(da, a) = {
  let s = range(da - 1, a)
  num(s.map(ore-sprint).sum() / membri.len() / s.map(i => settimane.at(i)).sum())
}

#let tabella-turni = block(breakable: false, figure(
  table(
    columns: (1.5fr,) + (auto,) * 10,
    align: (x, _) => if x == 0 { left } else { center },
    table.header([Membro], ..range(1, 11).map(i => [S#i])),
    ..turni.pairs().map(((membro, t)) => (membro, ..t.map(c => c.at(0)))).flatten(),
  ),
  caption: [Matrice di rotazione dei ruoli nei dieci sprint],
))

#let tabella-ore-sprint = block(breakable: false)[#figure(
  table(
    columns: (1.5fr,) + (auto,) * 11,
    align: (x, _) => if x == 0 { left } else { right },
    table.header([Membro], ..range(1, 11).map(i => [S#i]), [Totale]),
    ..turni
      .pairs()
      .map(((membro, t)) => (
        membro,
        ..t.map(c => if c.at(1) == 0 { [--] } else { str(c.at(1)) }),
        str(t.map(c => c.at(1)).sum()),
      ))
      .flatten(),
    [*Media*],
    ..range(10).map(s => if ore-sprint(s) == 0 { [--] } else { [*#num(media(s))*] }),
    [*#num(ore-totali / membri.len())*],
  ),
  caption: [Ore preventivate per membro e sprint],
) <ore-sprint>]

= Introduzione

== Scopo del documento
Questo documento formalizza l'assunzione degli impegni economici, temporali e organizzativi del gruppo SW2 Corporation nei confronti del committente per la realizzazione del progetto didattico associato al capitolato d'appalto C9 (SpecCheck: tracciabilità casi d'uso, requisiti e codice sorgente), proposto da Zucchetti S.p.A.

Vengono definiti la data di consegna prevista e la relativa motivazione, il calendario di massima con l'intensità dell'impegno, i rischi attesi con le relative misure di mitigazione, il monte ore complessivo, la ripartizione del lavoro tra i componenti e i ruoli, le regole vincolanti di rotazione con la matrice di rotazione e il preventivo economico dettagliato.

== Glossario
I termini tecnici o con significato specifico nel contesto del progetto sono raccolti nel glossario del gruppo. Alla loro prima occorrenza nel testo sono contrassegnati con una G a pedice e rimandano alla voce del glossario pubblicato sul sito del gruppo. I titoli delle sezioni non contengono marcature.

== Riferimenti

=== Riferimenti normativi
- #rif-web("Regolamento del progetto didattico di Ingegneria del Software 2026/27 (PD1)", "https://www.math.unipd.it/~tullio/IS-1/2026/Dispense/PD1.pdf", "2026-10-29").
- Verbale interno 2026-10-16, con le decisioni sugli sprint e sulla rotazione dei ruoli (VI-2026-10-16.3 e VI-2026-10-16.4).
- Verbale interno 2026-10-26, con la scelta iniziale del capitolato e l'organizzazione delle riunioni (VI-2026-10-26.1 e VI-2026-10-26.2).
- Verbale interno 2026-11-13, con il riorientamento sul capitolato C9 e la rideterminazione di preventivo e impegni (VI-2026-11-13.1, VI-2026-11-13.2 e VI-2026-11-13.3).
- Verbale esterno 2026-11-17, approvato con firma da Zucchetti il 2026-11-19, con l'interpretazione del capitolato C9 concordata con il proponente (VE-2026-11-17.1, VE-2026-11-17.2, VE-2026-11-17.3, VE-2026-11-17.4 e VE-2026-11-17.7).

=== Riferimenti informativi
- #rif-web("Capitolato C9: SpecCheck – Sviluppo di Skills per OpenCode per la verifica della tracciabilità end-to-end da casi d’uso a requisiti e codice sorgente", "https://www.math.unipd.it/~tullio/IS-1/2026/Progetto/C9-SpecCheck.pdf", "2026-11-25").

= Impegni assunti

#impegni()

Il gruppo assume l'impegno contrattuale a completare le attività e consegnare i prodotti attesi entro la scadenza indicata, rispettando il vincolo economico stabilito. Il costo preventivato costituisce il limite massimo invalicabile dell'appalto.

L'impegno orario complessivo ammonta a #ore-totali ore di lavoro produttivo, tra #ore-min e #ore-max ore per ciascuno dei sei componenti del gruppo.

A seguito dell'indisponibilità del capitolato C8 e del riorientamento concordato sul capitolato C9 (VI-2026-11-13.1, VI-2026-11-13.2 e VI-2026-11-13.3), il gruppo ha rideterminato gli impegni temporali ed economici:
- il tempo utile per il nuovo capitolato si riduce di circa tre settimane rispetto alla pianificazione originaria;
- il monte ore complessivo viene ricalibrato a #ore-totali ore (rispetto alle 544 ore iniziali) per un importo preventivato di #euro(costo-totale) (rispetto ai 10.920,00\u{a0}€ iniziali), garantendo la permanenza sopra la soglia minima di 80 ore a componente e sopra il costo minimo per sei componenti stabilito dal regolamento;
- le ore per C9 si contano dal 2026-11-24, come proposto con la decisione VI-2026-11-13.2;
- le ore svolte dal 2026-11-03 al 2026-11-23 saranno riportate a parte nel Piano di Progetto e non concorrono al computo a carico del committente per il capitolato C9. Fino al 2026-11-13 riguardano il capitolato C8: bozza di Analisi dei Requisiti, quesiti tecnici per Halue e perimetro preliminare del #g("Proof of Concept") (PoC). Dal 2026-11-16 riguardano la ripartenza su C9: contatto con Zucchetti, incontro di avvio, studio del capitolato e nuova pianificazione;
- la scadenza finale di consegna rimane invariata al *#gruppo.progetto.consegna_prevista*.

== Scadenza di consegna e motivazione

La data di consegna finale per la revisione di #g("Product Baseline") (PB) è fissata per il *#gruppo.progetto.consegna_prevista*, giorno del colloquio di PB.

Tale scadenza è stata motivata e dimensionata considerando i seguenti fattori:
- *Articolazione a sprint:* lo sviluppo è pianificato su dieci sprint di due settimane, dal martedì al lunedì, a partire dall'aggiudicazione del 2026-11-03 (VI-2026-10-16.3), garantendo un ciclo di vita incrementale con avanzamento misurabile; la consegna cade nel decimo sprint, dal 2027-03-09 al 2027-03-22;
- *Traguardo intermedio:* la revisione di #g("Requirements and Technology Baseline") (RTB) è prevista con il colloquio del 2027-01-08, dopo la candidatura del 2026-12-11. In questo periodo il gruppo consolida l'Analisi dei Requisiti e verifica la fattibilità tecnica con il PoC;
- *Sessione ordinaria d'esami:* tiene conto del periodo d'esami universitari (gennaio -- febbraio 2027), con una riduzione sostenibile delle ore settimanali che evita interruzioni nel flusso di lavoro;
- *Sviluppo del prodotto:* dopo la RTB restano circa otto settimane (2027-01-11 -- 2027-03-05) per la progettazione di dettaglio, l'implementazione del #g("Minimum Viable Product") (MVP) e la verifica continua;
- *Completamento del ciclo di qualifica:* le ultime due settimane servono a validare l'MVP con il proponente (2027-03-03), a presentare la candidatura alla PB (2027-03-08) e a correggere i prodotti prima del colloquio.

== Calendario di massima

L'avanzamento del progetto si articola nei seguenti macro-periodi operativi:

#figure(
  table(
    columns: (auto, 1.2fr, 1.1fr, 1.4fr),
    align: (center, left, left, left),
    table.header([*Periodo*], [*Arco temporale*], [*Milestone di riferimento*], [*Principali prodotti attesi*]),
    [Candidatura],
    [2026-10-12 -- 2026-10-30],
    [Invio della candidatura (2026-10-30)],
    [Valutazione dei capitolati, Dichiarazione degli impegni, Lettera di Presentazione, verbali],

    [RTB],
    [2026-11-03 -- 2027-01-08],
    [Candidatura RTB (2026-12-11) e colloquio RTB (2027-01-08)],
    [Norme di Progetto, Analisi dei Requisiti, Piano di Progetto, Piano di Qualifica, PoC],

    [PB],
    [2027-01-11 -- 2027-03-19],
    [Candidatura PB (2027-03-08) e colloquio PB (2027-03-19)],
    [Specifica Tecnica, MVP validato, Manuale Utente, collaudo],
  ),
  caption: [Calendario di massima del progetto],
)

== Intensità dell'impegno

Le ore per C9 si contano dal 2026-11-24 alla consegna del #gruppo.progetto.consegna_prevista: circa #num(settimane.sum()) settimane. Il monte ore complessivo di #ore-totali ore, in media circa #calc.round(ore-totali / ripartizione.len()) ore a persona, dà quindi una media di circa *#num(ore-totali / membri.len() / settimane.sum()) ore settimanali a componente*. L'intensità cresce rispetto alla pianificazione originaria: il monte ore cala di #(544 - ore-totali) ore, mentre il tempo utile si riduce di circa tre settimane.

Per armonizzare l'impegno progettuale con il calendario accademico, l'intensità lavorativa è articolata in tre profili, uno per fase, espressi come media del gruppo. La @ore-sprint riporta le ore di ogni componente, sprint per sprint.
- *Verso la RTB (sprint 2 -- 4, 2026-11-24 -- 2026-12-28):* circa *#intensita(2, 4) ore settimanali a persona*: #num(media(1)) ore nella settimana contabilizzata dello sprint 2, poi #num(media(2)) e #num(media(3)) ore a componente negli sprint 3 e 4. Le ore servono a raffinare l'ambiente di lavoro e le norme di processo già predisposti, completando l'Analisi dei Requisiti e il PoC entro la candidatura RTB;
- *Sessione d'esami (sprint 5 -- 7, 2026-12-29 -- 2027-02-08):* circa *#intensita(5, 7) ore settimanali a persona* (circa #num(media(4)) ore a componente per sprint), per conciliare il colloquio RTB, l'avvio della progettazione e il consolidamento documentale con lo studio per la sessione invernale d'esami;
- *Verso la PB (sprint 8 -- 10, dal 2027-02-09 alla consegna del 2027-03-19):* circa *#intensita(8, 10) ore settimanali a persona* (da #num(calc.min(..range(7, 10).map(media)), cifre: 0) a #num(calc.max(..range(7, 10).map(media)), cifre: 0) ore a componente per sprint), dedicate al completamento dello sviluppo, alla suite di test, all'integrazione e alla verifica rigorosa dei prodotti da consegnare per la PB.

= Rischi attesi e misure di mitigazione

Il gruppo ha individuato cinque fattori principali di rischio:

- *Sessione d'esami accademici (gennaio -- febbraio 2027):* gli esami universitari invernali possono ridurre temporaneamente la disponibilità dei componenti. Per mitigare il problema, l'intensità oraria programmata scende a circa #intensita(5, 7) ore settimanali a persona negli sprint 5 -- 7. L'Analisi dei Requisiti e il PoC vengono completati in anticipo, entro la candidatura RTB del 2026-12-11. Il Responsabile assegna compiti indipendenti e asincroni;
- *Festività natalizie (fine dicembre 2026 -- inizio gennaio 2027):* le festività possono rallentare le comunicazioni interne e rendere temporaneamente non reperibile il proponente. Le consegne principali vengono verificate prima della pausa. GitHub, Telegram e Discord rimangono operativi per brevi allineamenti periodici;
- *Disponibilità dei componenti e gestione degli imprevisti:* cause personali o impegni didattici imprevisti possono generare squilibri temporanei nella suddivisione del lavoro. Il gruppo mitiga la criticità mediante due riunioni interne a settimana su Discord, come previsto dalle Norme di Progetto (VI-2026-10-26.2). In caso di necessità, il Responsabile riassegna prontamente i task tra i membri, nel rispetto del monte ore complessivo e del limite di 95 ore a persona. La rotazione dei ruoli garantisce competenze diffuse tra tutti i membri;
- *Curva di apprendimento dello stack tecnologico:* le tecnologie del capitolato C9 (OpenCode e i suoi plugin, OpenSpec, Markdown con diagrammi Mermaid o PlantUML, TypeScript) sono in larga misura nuove per i componenti. Lo studio iniziale può richiedere più tempo del previsto e ritardare l'Analisi dei Requisiti e il PoC. Per mitigare il rischio, il gruppo ripartisce lo studio preliminare delle tecnologie tra i membri; attiva un ambiente di lavoro condiviso nello sprint 2 (\#140); sviluppa prove tecniche comparative (\#141) e mantiene un canale continuo di confronto con i referenti di Zucchetti;
- *Perimetro aperto e verifiche non deterministiche:* la natura aperta del capitolato C9 e l'uso di #g("Large Language Model") (LLM) per verificare la conformità tra requisiti, casi d'uso e codice sorgente comportano due rischi: confini sfumati e risposte probabilistiche, difficili da valutare in modo deterministico. Per mitigarli, il gruppo adotta specifiche misure ingegneristiche nel rispetto di quanto concordato con Zucchetti nel verbale esterno del 2026-11-17:
  - istruzioni vincolanti e schemi strutturati per le risposte (JSON Schema) per guidare e rendere controllabili e analizzabili le valutazioni dell'LLM;
  - controlli sintattici deterministici sul formato dei casi d'uso in Markdown con diagrammi Mermaid o PlantUML (VE-2026-11-17.3), affiancati a una skill con il modello dedicata a riscontrare la presenza dei casi d'uso in `proposal.md` e `design.md` (VE-2026-11-17.4);
  - banco di prova con un progetto inventato contenente discrepanze note (VE-2026-11-17.7), su cui eseguire prove ripetute per misurare l'accuratezza e verificare la stabilità dei risultati;
  - SpecCheck si concentra esclusivamente sulla verifica della coerenza, mentre la scrittura del codice rimane all'agente OpenCode (VE-2026-11-17.1).

#figure(
  table(
    columns: (1.1fr, 1.1fr, 1.8fr),
    align: (left, left, left),
    table.header([*Fattore di rischio*], [*Impatto potenziale*], [*Misure di mitigazione*]),
    [Sessione d'esami accademici (gennaio -- febbraio 2027)],
    [Riduzione del tempo disponibile e discontinuità operativa.],
    [Intensità a circa #intensita(5, 7) h settimanali a persona; Analisi dei Requisiti e PoC completati entro il 2026-12-11; task asincroni.],

    [Festività natalizie (fine dicembre 2026 -- inizio gennaio 2027)],
    [Rallentamento dei contatti interni e assenza temporanea del proponente.],
    [Sprint 4 orientato a compiti autonomi; chiusura anticipata dei deliverable; coordinamento asincrono.],

    [Disponibilità dei componenti e gestione degli imprevisti],
    [Squilibri individuali di carico e ritardi su task critici.],
    [Due riunioni interne a settimana; riassegnazione dei task da parte del Responsabile; competenze diffuse.],

    [Curva di apprendimento dello stack tecnologico],
    [Tempi di apprendimento elevati e possibili ritardi su requisiti e PoC.],
    [Ripartizione dello studio preliminare; allestimento ambiente nello sprint 2 (\#140); prove tecniche comparative (\#141); confronto continuo con Zucchetti.],

    [Perimetro aperto e verifiche non deterministiche],
    [Confini applicativi aperti, variabilità delle risposte ed errori semantici dell'LLM.],
    [Schemi strutturati in JSON per le risposte con istruzioni vincolanti per renderle controllabili; controlli sintattici (VE-2026-11-17.3) affiancati a skill con il modello (VE-2026-11-17.4); progetto inventato con discrepanze note (VE-2026-11-17.7) e prove ripetute.],
  ),
  caption: [Sintesi dei rischi attesi e delle misure di mitigazione],
)

= Ripartizione oraria

La distribuzione delle ore tra i ruoli segue i principi di equilibrio e completezza formativa richiesti dal regolamento: ciascun componente del gruppo ricopre tutti e sei i ruoli previsti, garantendo una partecipazione attiva a tutte le attività di processo previste per lo sviluppo del software.

La tabella deriva dalla matrice di rotazione e dalle ore per sprint riportate più avanti (@ore-sprint): per ogni componente somma le ore degli sprint in cui ricopre ciascun ruolo, a partire dal 2026-11-24. I totali individuali, tra #ore-min e #ore-max ore, variano con gli sprint in cui ciascuno ricopre i diversi ruoli e restano sotto il limite di 95 ore, con un margine per gli imprevisti.

#block(breakable: false, tabella-ore())

La pianificazione attribuisce priorità alle attività di analisi e progettazione (complessivamente #(ore-ruolo("Analista") + ore-ruolo("Progettista")) ore, pari al #perc(ore-ruolo("Analista") + ore-ruolo("Progettista")) del totale) e alla verifica continua (#ore-ruolo("Verificatore") ore, pari al #perc(ore-ruolo("Verificatore"))), allo scopo di prevenire difetti architetturali e contenere il debito tecnico. Le ore riservate al ruolo di Programmatore (#ore-ruolo("Programmatore") ore, pari al #perc(ore-ruolo("Programmatore"))) consentono la realizzazione del PoC e dell'MVP nei tempi concordati. I ruoli di coordinamento e servizio, Responsabile e Amministratore, pesano per il #perc(ore-ruolo("Responsabile") + ore-ruolo("Amministratore")).

= Regole di rotazione dei ruoli

Il gruppo adotta le seguenti regole vincolanti di rotazione:

+ *Turni:* il gruppo lavora per sprint di due settimane, dal martedì al lunedì di due settimane dopo; il primo va dal 2026-11-03 al 2026-11-16. I ruoli cambiano a turni e all'inizio un turno dura uno sprint, secondo la matrice riportata più avanti;
+ *Turni più brevi:* in seguito i turni possono durare meno di uno sprint, per esempio una settimana, per distribuire meglio le ore per ruolo. La durata cambia con una decisione a verbale e vale dall'apertura dello sprint successivo;
+ *Unicità del ruolo:* ogni componente ha un solo ruolo per turno;
+ *Indipendenza della verifica:* nessun componente verifica un proprio prodotto. Documenti e verbali li verifica un Verificatore; sito e strumenti un Verificatore o l'Amministratore;
+ *Alternanza della gestione:* nessun componente è Responsabile per due turni di fila, compreso il passaggio dalla candidatura al primo sprint;
+ *Copertura completa:* entro la consegna ogni componente copre ciascuno dei sei ruoli per almeno un turno con ore contabilizzate per C9, cioè dallo sprint 2 in poi (VI-2026-11-13.3);
+ *Passaggio di consegne:* le consegne di ruolo si passano all'inizio del turno. Ogni turno è registrato in `dati/ruoli.csv`, con inizio, fine, componente e ruolo.

== Matrice di rotazione

La seguente tabella fissa i turni dei dieci sprint, dall'aggiudicazione del 2026-11-03 alla consegna del 2027-03-19. Vale finché un turno dura uno sprint: se i turni si accorciano, il gruppo la aggiorna con la stessa decisione a verbale. Lo sprint 1 e la prima settimana dello sprint 2 precedono la contabilizzazione per C9: i loro turni restano nella matrice, ma non hanno ore nel preventivo. Per questo nello sprint 7 Alessandro Paduret è Progettista invece che Programmatore (VI-2026-11-13.3): il suo unico turno da Progettista cadeva nello sprint 1. La copertura segue le fasi: due Analisti nei primi due sprint, Progettisti e Programmatori in crescita dopo la RTB, due Verificatori dopo la candidatura RTB (sprint 4) e a ridosso della PB (sprint 9 e 10). In ogni sprint c'è un solo Responsabile e almeno un Verificatore; negli sprint 4 e 7, di festività e di esami, non è previsto l'Amministratore.

#tabella-turni

_Legenda ruoli:_ *RE*: Responsabile; *AM*: Amministratore; *AN*: Analista; *PR*: Progettista; *PO*: Programmatore; *VE*: Verificatore.

In ogni sprint il Responsabile e l'Amministratore, ruoli di coordinamento e servizio, registrano circa il 60% delle ore medie dello sprint; chi ricopre gli altri ruoli registra la parte restante. La @ore-sprint riporta queste ore; nello sprint 2 coprono solo la settimana dal 2026-11-24. La tabella di ripartizione oraria le somma per componente e per ruolo.

#tabella-ore-sprint

= Preventivo economico

#tabella-costi()

Il costo complessivo preventivato ammonta a #euro(costo-totale), determinato moltiplicando le ore preventivate per ciascun ruolo per le relative tariffe orarie fissate dal committente nel Regolamento PD1.
