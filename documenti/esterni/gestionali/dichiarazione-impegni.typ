#import "/modello/documento.typ": documento
#import "/modello/comuni.typ": (
  costo-totale, euro, g, gruppo, impegni, ore-membro, ore-ruolo, rif-web, ripartizione, tabella-costi, tabella-ore,
)

#show: documento.with(
  titolo: "Dichiarazione degli impegni",
  sottotitolo: "Pianificazione preventiva delle risorse orarie ed economiche per la candidatura",
  uso: "esterno",
  destinatari: ("Prof. Tullio Vardanega", "Prof. Riccardo Cardin"),
  registro: csv("dichiarazione-impegni.registro.csv"),
)

#let ore-totali = ripartizione.map(ore-membro).sum()
#let ore-min = calc.min(..ripartizione.map(ore-membro))
#let ore-max = calc.max(..ripartizione.map(ore-membro))
#let perc(ore) = str(calc.round(ore / ore-totali * 100, digits: 1)).replace(".", ",") + "%"

= Introduzione

== Scopo del documento
Questo documento formalizza l'assunzione degli impegni economici, temporali e organizzativi del gruppo SW2 Corporation nei confronti del committente per la realizzazione del progetto didattico associato al capitolato d'appalto C8 (Sonar: documentazione vivente di uno store Shopify), proposto da Halue S.r.l. SB.

Vengono definiti la data di consegna prevista e la relativa motivazione, il calendario di massima con l'intensità dell'impegno, i rischi attesi con le relative misure di mitigazione, il monte ore complessivo, la ripartizione del lavoro tra i componenti e i ruoli, le regole vincolanti di rotazione con la matrice di rotazione e il preventivo economico dettagliato.

== Glossario
I termini tecnici o con significato specifico nel contesto del progetto sono raccolti nel glossario del gruppo. Alla loro prima occorrenza nel testo sono contrassegnati con una G a pedice e rimandano alla voce del glossario pubblicato sul sito del gruppo. I titoli delle sezioni non contengono marcature.

== Riferimenti

=== Riferimenti normativi
- #rif-web("Regolamento del progetto didattico di Ingegneria del Software 2026/27 (PD1)", "https://www.math.unipd.it/~tullio/IS-1/2026/Dispense/PD1.pdf", "2026-10-29").
- Verbale interno 2026-10-16, con le decisioni sugli sprint e sulla rotazione dei ruoli (VI-2026-10-16.3 e VI-2026-10-16.4).
- Verbale interno 2026-10-26, con la scelta del capitolato e l'organizzazione delle riunioni (VI-2026-10-26.1 e VI-2026-10-26.2).

=== Riferimenti informativi
- #rif-web("Capitolato C8 - Sonar: documentazione vivente di uno store Shopify (Halue)", "https://www.math.unipd.it/~tullio/IS-1/2026/Progetto/C8.pdf", "2026-10-29").

= Impegni assunti

#impegni()

Il gruppo assume l'impegno contrattuale a completare le attività e consegnare i prodotti attesi entro la scadenza indicata, rispettando il vincolo economico stabilito. Il costo preventivato costituisce il limite massimo invalicabile dell'appalto.

L'impegno orario complessivo ammonta a #ore-totali ore di lavoro produttivo, tra #ore-min e #ore-max ore per ciascuno dei sei componenti del gruppo.

== Scadenza di consegna e motivazione

La data di consegna finale per la revisione di #g("Product Baseline") (PB) è fissata per il *#gruppo.progetto.consegna_prevista*, giorno del colloquio di PB.

Tale scadenza è stata motivata e dimensionata considerando i seguenti fattori:
- *Articolazione a sprint:* lo sviluppo è pianificato su dieci sprint di due settimane, dal martedì al lunedì, a partire dall'aggiudicazione del 2026-11-03 (VI-2026-10-16.3), garantendo un ciclo di vita incrementale con avanzamento misurabile; la consegna cade nel decimo sprint, dal 2027-03-09 al 2027-03-22;
- *Traguardo intermedio:* la revisione di #g("Requirements and Technology Baseline") (RTB) è prevista con il colloquio del 2027-01-08, dopo la candidatura del 2026-12-11. In questo periodo il gruppo consolida l'Analisi dei Requisiti e verifica la fattibilità tecnica con un #g("Proof of Concept") (PoC);
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

Il monte ore complessivo di #ore-totali ore (in media circa #calc.round(ore-totali / ripartizione.len()) ore a persona) si distribuisce sulle circa 20 settimane che separano l'aggiudicazione dalla consegna, con una media di circa *4,6 ore settimanali a componente*.

Per armonizzare l'impegno progettuale con il calendario accademico, l'intensità lavorativa è articolata in tre profili, espressi come media del gruppo:
- *Intensità ordinaria (sprint 1 -- 4, 2026-11-03 -- 2026-12-28):* circa *5 ore settimanali a persona* (circa 10 ore a componente per sprint), finalizzate a raffinare l'ambiente di lavoro e le norme di processo già predisposti, completando l'Analisi dei Requisiti e il PoC;
- *Intensità modulata (sprint 5 -- 7, 2026-12-29 -- 2027-02-08):* circa *3 ore settimanali a persona* (circa 6 ore a componente per sprint), per conciliare il colloquio RTB, l'avvio della progettazione e il consolidamento documentale con lo studio per la sessione invernale d'esami;
- *Intensità sostenuta (sprint 8 -- 10, dal 2027-02-09 alla consegna del 2027-03-19):* circa *6 ore settimanali a persona* (da 10 a 13 ore a componente per sprint), dedicate al completamento dello sviluppo, alla suite di test, all'integrazione e alla verifica rigorosa dei prodotti da consegnare per la PB.

= Rischi attesi e misure di mitigazione

Il gruppo ha individuato quattro fattori principali di rischio:

- *Sessione d'esami accademici (gennaio -- febbraio 2027):* gli esami universitari invernali possono ridurre temporaneamente la disponibilità dei componenti. Per mitigare il problema, l'intensità oraria programmata scende a circa 3 ore settimanali a persona negli sprint 5 -- 7. L'Analisi dei Requisiti e il PoC vengono completati in anticipo, entro la candidatura RTB del 2026-12-11. Il Responsabile assegna compiti indipendenti e asincroni;
- *Festività natalizie (fine dicembre 2026 -- inizio gennaio 2027):* le festività possono rallentare le comunicazioni interne e rendere temporaneamente non reperibile il proponente. Le consegne principali vengono verificate prima della pausa. GitHub, Telegram e Discord rimangono operativi per brevi allineamenti periodici;
- *Disponibilità dei componenti e gestione degli imprevisti:* cause personali o impegni didattici imprevisti possono generare squilibri temporanei nella suddivisione del lavoro. Il gruppo mitiga la criticità mediante due riunioni interne a settimana su Discord, come previsto dalle Norme di Progetto (VI-2026-10-26.2). In caso di necessità, il Responsabile riassegna prontamente i task tra i membri, nel rispetto del monte ore complessivo e del limite di 95 ore a persona. La rotazione dei ruoli garantisce competenze diffuse tra tutti i membri;
- *Curva di apprendimento dello stack tecnologico:* lo stack indicato dal capitolato è in gran parte nuovo per il gruppo, in particolare le tecnologie di Shopify e del suo ecosistema. Lo studio può richiedere più tempo del previsto e ritardare l'Analisi dei Requisiti e il PoC. Come mitigazione, il gruppo divide lo studio delle tecnologie tra i membri: ciascuno approfondisce una parte prima di usarla e la presenta agli altri. Per dubbi specifici su Shopify, il gruppo può chiedere un confronto con gli ingegneri di Halue.

#figure(
  table(
    columns: (1.1fr, 1.1fr, 1.8fr),
    align: (left, left, left),
    table.header([*Fattore di rischio*], [*Impatto potenziale*], [*Misure di mitigazione*]),
    [Sessione d'esami (gennaio -- febbraio 2027)],
    [Riduzione del tempo disponibile e discontinuità operativa.],
    [Intensità a circa 3 h settimanali a persona; Analisi dei Requisiti e PoC completati entro il 2026-12-11; task asincroni.],

    [Festività natalizie (fine dicembre 2026 -- inizio gennaio 2027)],
    [Rallentamento dei contatti interni e assenza temporanea del proponente.],
    [Sprint 4 orientato a compiti autonomi; chiusura anticipata dei deliverable; coordinamento asincrono.],

    [Disponibilità dei componenti e imprevisti],
    [Squilibri individuali di carico e ritardi su task critici.],
    [Due riunioni interne a settimana; riassegnazione dei task da parte del Responsabile; competenze diffuse.],

    [Curva di apprendimento tecnologico],
    [Studio più lungo del previsto; ritardi su Analisi dei Requisiti e PoC.],
    [Parti più incerte affrontate per prime; PoC entro la RTB; studio prima dell'uso e presentazioni interne; confronto con gli ingegneri di Halue.],
  ),
  caption: [Sintesi dei rischi attesi e delle misure di mitigazione],
)

= Ripartizione oraria

La distribuzione delle ore tra i ruoli segue i principi di equilibrio e completezza formativa richiesti dal regolamento: ciascun componente del gruppo ricopre tutti e sei i ruoli previsti, garantendo una partecipazione attiva a tutte le attività di processo previste per lo sviluppo del software.

La tabella deriva dalla matrice di rotazione riportata più avanti: per ogni componente somma le ore degli sprint in cui ricopre ciascun ruolo. I totali individuali, tra #ore-min e #ore-max ore, variano con gli sprint in cui ciascuno ricopre i diversi ruoli e restano sotto il limite di 95 ore, con un margine per gli imprevisti.

#block(breakable: false, tabella-ore())

La pianificazione attribuisce priorità alle attività di analisi e progettazione (complessivamente #(ore-ruolo("Analista") + ore-ruolo("Progettista")) ore, pari al #perc(ore-ruolo("Analista") + ore-ruolo("Progettista")) del totale) e alla verifica continua (#ore-ruolo("Verificatore") ore, pari al #perc(ore-ruolo("Verificatore"))), allo scopo di prevenire difetti architetturali e contenere il debito tecnico. Le ore riservate al ruolo di Programmatore (#ore-ruolo("Programmatore") ore, pari al #perc(ore-ruolo("Programmatore"))) consentono la realizzazione del PoC e dell'MVP nei tempi concordati. I ruoli di coordinamento e servizio, Responsabile e Amministratore, pesano per il #perc(ore-ruolo("Responsabile") + ore-ruolo("Amministratore")).

= Regole di rotazione dei ruoli

Il gruppo adotta le seguenti regole vincolanti di rotazione:

+ *Turni:* il gruppo lavora per sprint di due settimane, dal martedì al lunedì di due settimane dopo; il primo va dal 2026-11-03 al 2026-11-16. I ruoli cambiano a turni e all'inizio un turno dura uno sprint, secondo la matrice riportata più avanti;
+ *Turni più brevi:* in seguito i turni possono durare meno di uno sprint, per esempio una settimana, per distribuire meglio le ore per ruolo. La durata cambia con una decisione a verbale e vale dall'apertura dello sprint successivo;
+ *Unicità del ruolo:* ogni componente ha un solo ruolo per turno;
+ *Indipendenza della verifica:* nessun componente verifica un proprio prodotto. Documenti e verbali li verifica un Verificatore; sito e strumenti un Verificatore o l'Amministratore;
+ *Alternanza della gestione:* nessun componente è Responsabile per due turni di fila, compreso il passaggio dalla candidatura al primo sprint;
+ *Copertura completa:* entro la consegna ogni componente copre ciascuno dei sei ruoli per almeno un turno;
+ *Passaggio di consegne:* le consegne di ruolo si passano all'inizio del turno. Ogni turno è registrato in `dati/ruoli.csv`, con inizio, fine, componente e ruolo.

== Matrice di rotazione

La seguente tabella fissa i turni dei dieci sprint, dall'aggiudicazione del 2026-11-03 alla consegna del 2027-03-19. Vale finché un turno dura uno sprint: se i turni si accorciano, il gruppo la aggiorna con la stessa decisione a verbale. La copertura segue le fasi: due Analisti nei primi due sprint, Progettisti e Programmatori in crescita dopo la RTB, due Verificatori a ridosso delle revisioni. In ogni sprint c'è un solo Responsabile e almeno un Verificatore; negli sprint 4 e 7, di festività e di esami, non è previsto l'Amministratore.

#figure(
  table(
    columns: (1.5fr,) + (auto,) * 10,
    align: (x, _) => if x == 0 { left } else { center },
    table.header([Membro], [S1], [S2], [S3], [S4], [S5], [S6], [S7], [S8], [S9], [S10]),
    [Davide Baraldo], [AN], [VE], [PO], [RE], [AN], [AM], [PR], [VE], [PO], [AM],
    [Matteo Bellato], [AM], [AN], [PR], [VE], [PO], [VE], [AN], [PO], [AM], [RE],
    [Patrizio Eleuteri], [RE], [AN], [VE], [PO], [PR], [RE], [PO], [AM], [VE], [PO],
    [Oussama Mahdi], [AN], [RE], [AN], [VE], [AM], [PR], [RE], [PO], [VE], [PR],
    [Alessandro Paduret], [PR], [AM], [RE], [AN], [VE], [PO], [PO], [RE], [PO], [VE],
    [David Sirbu], [VE], [PO], [AM], [PR], [RE], [AN], [VE], [PR], [RE], [VE],
  ),
  caption: [Matrice di rotazione dei ruoli nei dieci sprint],
)

_Legenda ruoli:_ *RE*: Responsabile; *AM*: Amministratore; *AN*: Analista; *PR*: Progettista; *PO*: Programmatore; *VE*: Verificatore.

In ogni sprint il Responsabile e l'Amministratore, ruoli di coordinamento e servizio, registrano circa il 60% delle ore medie dello sprint; chi ricopre gli altri ruoli registra la parte restante. La tabella di ripartizione oraria somma queste ore per componente e per ruolo.

= Preventivo economico

#tabella-costi()

Il costo complessivo preventivato ammonta a #euro(costo-totale), determinato moltiplicando le ore preventivate per ciascun ruolo per le relative tariffe orarie fissate dal committente nel Regolamento PD1.
