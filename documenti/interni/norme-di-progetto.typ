#import "/modello/documento.typ": documento
#import "/modello/comuni.typ": g, rif-doc, rif-web

#show: documento.with(
  titolo: "Norme di Progetto",
  sottotitolo: "Processi, procedure, strumenti e metriche del gruppo",
  uso: "interno",
  destinatari: ("Membri del gruppo SW2 Corporation",),
  registro: csv("norme-di-progetto.registro.csv"),
)

= Introduzione

== Scopo del documento
Questo documento fissa il modo di lavorare del gruppo SW2 Corporation. Descrive i processi che il gruppo svolge, le attività di ogni processo, le procedure da seguire passo per passo, gli strumenti da usare e le metriche con cui il gruppo si misura.

Le norme sono esecutive: dicono cosa fare, quando e come, senza lasciare spazio all'arbitrio. Ogni altro documento del gruppo le cita come riferimento normativo.

Le norme si scrivono prima di svolgere un'attività. Il documento cresce quindi nel tempo: la sezione di un'attività non ancora normata dice entro quando lo sarà.

== Scopo del prodotto
Il prodotto è l'oggetto del capitolato che il gruppo si aggiudica il 2026-11-03. Fino a quella data il gruppo prepara la candidatura: valuta i capitolati, incontra i proponenti e dichiara i propri impegni.

== Glossario
I termini con un significato specifico per il progetto stanno nel glossario del gruppo, pubblicato sul sito della documentazione. Nei documenti ogni termine del glossario porta il pedice G alla prima occorrenza. I titoli non marcano termini.

== Riferimenti

=== Riferimenti normativi
- #rif-web("Regolamento del progetto didattico di Ingegneria del Software 2026/27 (PD1)", "https://www.math.unipd.it/~tullio/IS-1/2026/Dispense/PD1.pdf", "2026-10-18").
- Verbale interno 2026-10-16, con le decisioni sul modo di lavorare del gruppo.

=== Riferimenti informativi
- ISO/IEC 12207:1995, Information technology, Software life cycle processes: la tassonomia dei processi usata in questo documento.
- #rif-web("Capitolati d'appalto 2026/27", "https://www.math.unipd.it/~tullio/IS-1/2026/Progetto/Capitolati.html", "2026-10-18").
- #rif-web("K. Schwaber, J. Sutherland, The Scrum Guide, novembre 2020", "https://scrumguides.org/scrum-guide.html", "2026-10-20").

== Struttura del documento
I processi seguono la tassonomia di ISO/IEC 12207:1995, adattata al progetto. Un processo è un insieme di attività, mai un documento o un prodotto. Ogni processo ha:
- uno scopo;
- le aspettative, cioè i risultati che il gruppo si attende;
- le attività, ognuna con quando si svolge, ingressi e uscite;
- le procedure numerate passo per passo;
- gli strumenti, con il modo d'uso;
- le metriche, con codice e definizione.

Le definizioni delle metriche stanno nell'ultima sezione. Le soglie e le misure stanno nel Piano di Qualifica.

= Processi primari

== Fornitura

=== Scopo e aspettative
Il processo di fornitura regola i rapporti del gruppo con i proponenti dei capitolati. In questa fase il gruppo incontra i proponenti della rosa e presenta la candidatura. Il gruppo si aspetta incontri regolari, verbali esterni approvati dal proponente e una candidatura completa entro il 2026-10-30.

=== Incontri esplorativi con i proponenti
Quando: tra la scelta della rosa e la scelta del capitolato. Ingressi: il capitolato e le domande del gruppo. Uscite: il verbale esterno approvato dal proponente.

Procedura:
+ Il Responsabile scrive al proponente dalla casella del gruppo e propone tre date. L'oggetto indica il gruppo e il capitolato.
+ La coppia assegnata al capitolato prepara agenda e domande, in ordine di valore. Le domande riguardano il perimetro dell'MVP, le tecnologie imposte, i dati disponibili, i criteri di accettazione, la cadenza degli incontri e l'uso futuro del prodotto.
+ All'incontro un membro fa da portavoce e un altro da redattore.
+ Entro 48 ore il redattore scrive il verbale esterno, secondo la procedura dei verbali.
+ Il Responsabile manda il verbale al proponente dalla casella del gruppo e chiede l'approvazione.
+ Alla risposta il redattore registra l'approvazione nel campo dedicato del verbale. Finché manca, il verbale riporta "in attesa".
+ Se il proponente rimanda il verbale firmato, il redattore salva il PDF accanto al file del verbale, con lo stesso nome e l'estensione `.firmato.pdf`. Il sito pubblica la copia firmata al posto di quella compilata. Da quel momento il verbale non cambia: una correzione richiede una nuova versione e una nuova firma.

Strumenti: casella email del gruppo, piattaforma video scelta dal proponente, repository della documentazione. Metriche: MPC-01.

=== Candidatura
Quando: dal 2026-10-19 al 2026-10-30. Ingressi: i capitolati, i verbali degli incontri, il regolamento. Uscite: Valutazione dei capitolati, Dichiarazione degli impegni, Lettera di Presentazione, tutti pubblicati sul sito.

Procedura:
+ Gli Analisti scrivono la Valutazione dei capitolati: tutti i capitolati, i criteri, il confronto e la scelta motivata.
+ Il Responsabile scrive la Dichiarazione degli impegni: ore per membro e ruolo, regole di rotazione, costo e data di consegna.
+ I Verificatori verificano i due documenti. Chi ha scritto un documento non lo verifica.
+ Il Responsabile approva i due documenti con la riga di approvazione nel registro.
+ Il Responsabile scrive la Lettera di Presentazione, che elenca i prodotti consegnati con i link.
+ Il gruppo controlla il sito: lettera in cima, verbali dal più recente, interni separati dagli esterni, nessuna bozza.
+ Il Responsabile invia la candidatura dalla casella del gruppo, con i soli link e nessun allegato, la mattina del 2026-10-30.

Strumenti: repository della documentazione, sito, casella email del gruppo. Metriche: MPC-03, MPC-05.

== Sviluppo
Le attività di analisi dei requisiti, progettazione, codifica, integrazione e test iniziano dopo l'aggiudicazione. Il gruppo le norma prima di avviarle. Le norme di progettazione e di codifica entrano in questo documento prima del primo sprint che le prevede.

= Processi di supporto

== Documentazione

=== Scopo e aspettative
La documentazione registra ciò che il gruppo decide, pianifica e produce. Il gruppo si aspetta documenti leggibili, coerenti tra loro, verificati da una persona diversa dall'autore e pubblicati solo quando approvati.

=== Ciclo di vita di un documento
Ogni documento con registro passa per quattro stati.
- Bozza: il documento è in lavorazione. Il registro non ha righe, oppure ha solo righe precedenti all'approvazione. Una bozza non va mai sul sito.
- In verifica: l'autore ha aperto la pull request e ha chiesto la verifica.
- Verificato: il verificatore ha dato esito positivo. L'autore aggiunge la riga nel registro con la nuova versione, il proprio nome e quello del verificatore.
- Approvato: il Responsabile aggiunge la riga di approvazione. Solo questa riga rilascia il documento e lo porta sul sito.

Le versioni hanno la forma X.Y.Z. Z cresce per una modifica minore verificata. Y cresce per una modifica sostanziale verificata. X cresce solo con l'approvazione del Responsabile. La versione non cambia mai senza una verifica.

La copertina riporta la versione e la data dell'ultimo aggiornamento, cioè la versione e la data della prima riga del registro. Il piè di pagina le ripete su ogni pagina e il sito le mostra accanto al documento.

Il registro delle modifiche precede l'indice ed è in ordine dalla riga più recente. Ogni riga indica versione, data, autore, verificatore e descrizione. Autore e verificatore sono persone diverse. La riga di approvazione ha il verificatore vuoto e una descrizione che inizia con "Approvazione".

=== Tipi di documento
- Documenti con registro: documenti gestionali e tecnici esterni, documenti interni. Hanno copertina, registro, indice e introduzione.
- Lettere di Presentazione: una per consegna, con la data e senza versione né registro. La data è quella dell'ultimo aggiornamento: la lettera inviata sostituisce le bozze. Stanno in cima al sito.
- Verbali interni ed esterni: hanno la stessa struttura, cartelle diverse e nessun registro. Hanno la versione e la data dell'ultimo aggiornamento.
- Diari di bordo: presentazioni per i docenti, una per settimana, senza registro. Hanno la versione e la data dell'ultimo aggiornamento. Il diario nasce alla versione 1.0.0. Ogni modifica verificata ne aggiorna la data e fa crescere Y se cambia il contenuto, Z negli altri casi. Le slide riportano solo la versione.

=== Convenzioni
- I documenti si scrivono in Typst con il modello del gruppo. Il modello fornisce copertina, registro, intestazioni, tabelle e stile.
- Ogni documento riporta la versione e la data dell'ultimo aggiornamento, nel PDF e sul sito. La Lettera di Presentazione riporta solo la data e le slide del diario di bordo solo la versione.
- Le date sono sempre nella forma AAAA-MM-GG, nel testo e nei nomi dei file. Gli orari sono nella forma HH:MM.
- Nei titoli solo la prima parola ha l'iniziale maiuscola, salvo acronimi e nomi propri.
- Tabelle e figure sono numerate e hanno una didascalia: sopra per le tabelle, sotto per le figure.
- I riferimenti web riportano titolo, indirizzo e data di ultimo accesso.
- Gli standard ISO stanno tra i riferimenti informativi, in una sola versione.
- Le frasi sono brevi. L'indice di leggibilità di ogni documento resta sopra la soglia fissata nel modello.
- Il lessico segue il regolamento: "Lettera di Presentazione", "Dichiarazione degli impegni", "decisioni prese", "lo sprint".

=== Procedura per scrivere un documento con registro
+ L'autore apre una issue per il lavoro, se non esiste, e un branch dedicato.
+ L'autore scrive il documento nel file Typst e lascia il registro con la sola intestazione, se il documento è nuovo.
+ L'autore esegue i controlli automatici in locale e corregge ogni errore.
+ L'autore apre la pull request e chiede la verifica a un membro con il ruolo di Verificatore.
+ Il verificatore segue la procedura di verifica e scrive l'esito nella pull request.
+ A esito positivo l'autore aggiunge la riga nel registro, con versione, data, autore e verificatore. Il verificatore approva la pull request e la integra.
+ Quando il documento è pronto per il rilascio, il Responsabile aggiunge la riga di approvazione con la stessa procedura. Il sito pubblica il documento.

=== Verbali
Quando: dopo ogni riunione interna e ogni incontro con un proponente. Ingressi: gli appunti del redattore. Uscite: il verbale pubblicato e le issue delle azioni.

Un verbale è un file TOML con data, versione, data dell'ultimo aggiornamento, orari, luogo, redattore, verificatore, partecipanti, ordine del giorno, sintesi per punto, decisioni e azioni. Il modello del gruppo lo impagina.

Regole:
- il redattore e il verificatore sono persone diverse;
- il verbale nasce alla versione 1.0.0. Ogni modifica verificata ne aggiorna la data e fa crescere Y se cambia decisioni o azioni, Z negli altri casi;
- l'ordine del giorno viene sempre per primo;
- la sintesi di ogni punto è breve: il verbale registra decisioni motivate, non la discussione;
- ogni decisione ha un identificativo, il testo e la motivazione. Gli identificativi hanno la forma VI-AAAA-MM-GG.n per i verbali interni e VE-AAAA-MM-GG.n per gli esterni;
- ogni decisione che richiede lavoro genera almeno un'azione, con un assegnatario, una scadenza e il link alla issue. L'assegnatario è un membro, mai "tutti";
- il verbale esterno riporta i partecipanti esterni con ruolo e azienda, e l'approvazione del proponente;
- il verbale non contiene giudizi su persone o aziende, motivi personali di assenza, dati privati né linguaggio informale.

Procedura:
+ Entro 48 ore dalla riunione il redattore scrive il verbale in un branch dedicato.
+ Il redattore apre una issue per ogni azione e ne scrive il link nel verbale.
+ Il redattore esegue i controlli automatici e apre la pull request.
+ Il verificatore controlla il verbale con la lista di controllo e approva la pull request.
+ Il verificatore integra la pull request. Il sito pubblica il verbale.

Strumenti: repository della documentazione, controlli automatici, issue. Metriche: MPC-01, MPC-04.

== Gestione della configurazione

=== Scopo e aspettative
La gestione della configurazione conserva la storia di ogni prodotto del gruppo e ne controlla le modifiche. Il gruppo si aspetta che ogni modifica sia tracciata da una issue, passi da una pull request verificata e che il sito mostri solo versioni approvate.

=== Repository
Il gruppo lavora nell'organizzazione GitHub SW2-Corporation. Il repository `docs` è pubblico e contiene la documentazione: dati del gruppo, modello Typst, documenti, verbali, strumenti di controllo e workflow. Il repository del prodotto nasce dopo l'aggiudicazione e viene normato prima dell'uso.

La struttura del repository della documentazione è fissa:
- `dati/`: gruppo, ruoli, ore, preventivo, glossario;
- `documenti/esterni/gestionali/` e `documenti/esterni/tecnici/`: documenti esterni con registro;
- `documenti/interni/`: documenti interni con registro;
- `documenti/lettere/`: Lettere di Presentazione;
- `documenti/verbali/interni/` e `documenti/verbali/esterni/`: verbali;
- `presentazioni/`: diari di bordo e altre presentazioni;
- `modello/`: il modello Typst;
- `strumenti/`: controlli automatici, test e generazione del sito.

=== Branch e commit
Il branch `main` contiene solo lavoro verificato. Nessuno scrive direttamente su `main`: ogni modifica nasce in un branch e arriva su `main` con una pull request.

I branch prendono il nome dal tipo di lavoro:
- `verbale/AAAA-MM-GG` per un verbale;
- `documento/nome-argomento` per un documento, per esempio `documento/norme-di-progetto-verifica`;
- `dati/argomento` per i dati del gruppo;
- `sito/argomento` per modello, strumenti e sito.

Ogni commit porta l'identità git del membro, con nome e cognome. Il messaggio è in italiano. La prima riga descrive la modifica in al massimo 72 caratteri. Il corpo cita la issue con il suo numero, per esempio "Rif. \#12".

=== Pull request
Procedura:
+ L'autore apre la pull request verso `main`. Il titolo dice cosa cambia. La descrizione cita la issue nella forma `Closes #N`, così l'integrazione la chiude, e riporta il contenuto della modifica e come verificarla.
+ I controlli automatici devono risultare verdi. Un errore si corregge nel contenuto, mai nel controllo.
+ L'autore chiede la verifica a un membro diverso da sé. Per un documento è un Verificatore, per il sito e gli strumenti l'Amministratore o un Verificatore.
+ Il verificatore controlla la modifica con la #g("Definition of Done") e scrive l'esito come revisione della pull request: approvata oppure con le modifiche richieste.
+ A esito positivo il verificatore integra la pull request con un commit di merge, senza riscrivere la storia.
+ L'integrazione chiude la issue collegata.

Strumenti: GitHub, GitHub Actions. Metriche: MPC-02, MPC-05.

=== Rilascio e pubblicazione
Il sito della documentazione si rigenera a ogni integrazione su `main`. Il sito mostra i documenti con una riga di approvazione nel registro, tutte le Lettere di Presentazione, tutti i verbali e tutti i diari di bordo. Le bozze e le altre presentazioni non compaiono. L'ordine è dal più recente al più vecchio, con la Lettera di Presentazione in cima. Il sito pubblica anche il cruscotto: ore e costi preventivati e consuntivi, tempi e avanzamento, letti dai file di `dati/` e confrontati con le soglie di `dati/gruppo.toml`.

== Verifica

=== Scopo e aspettative
La verifica accerta che ogni prodotto rispetti le norme e il suo scopo prima di essere integrato. Il gruppo si aspetta che nessun prodotto arrivi su `main` senza una verifica indipendente.

=== Controlli automatici
Lo script `strumenti/verifica.py` controlla il repository. Ogni problema è una riga con percorso, riga, codice e messaggio. I codici che iniziano per E sono errori e fermano la pull request. I codici che iniziano per W sono avvisi e vanno risolti prima del rilascio. I controlli riguardano:
- dati del gruppo, ruoli, ore e preventivo;
- registro delle modifiche: intestazione, ordine, versioni, persone diverse, approvazioni;
- titoli, date, lessico, riferimenti, figure e termini del glossario;
- verbali: schema, date, versione e ultimo aggiornamento, orari, decisioni, azioni, issue, approvazione esterna, nome della copia firmata;
- diari di bordo: data, versione e ultimo aggiornamento;
- leggibilità dei documenti.

I test degli strumenti si eseguono con `python -m unittest discover -s strumenti`. Il workflow `Verifica` esegue controlli e test a ogni pull request e a ogni integrazione.

=== Verifica di un documento
Il verificatore controlla il documento con questa lista:
+ la struttura segue le norme: copertina, registro, indice, introduzione con scopo, glossario e riferimenti;
+ il contenuto risponde allo scopo del documento ed è coerente con le decisioni dei verbali e con il regolamento;
+ ogni affermazione verificabile ha una fonte o un riferimento;
+ le convenzioni sono rispettate: date, titoli, didascalie, lessico, termini del glossario;
+ i controlli automatici sono verdi;
+ le versioni e le righe del registro sono coerenti con la modifica.

Il verificatore scrive l'esito nella pull request, punto per punto, con le correzioni richieste. L'autore corregge e chiede una nuova verifica.

=== Verifica di un verbale
+ Ordine del giorno, sintesi, decisioni e azioni sono presenti e coerenti tra loro.
+ Ogni decisione è motivata.
+ Ogni azione ha assegnatario, scadenza futura e issue.
+ Il verbale non contiene contenuti estranei a un documento ufficiale.
+ Il verbale esterno riporta gli esterni e lo stato dell'approvazione.
+ Versione e data dell'ultimo aggiornamento sono aggiornate con la modifica, secondo le regole dei verbali.

== Accertamento della qualità
Il gruppo norma entro il 2026-11-02 la raccolta delle metriche, il cruscotto e il modo in cui le misure guidano le correzioni. Le definizioni delle metriche già in uso stanno nell'ultima sezione.

== Risoluzione dei problemi
Il gruppo norma entro il 2026-11-02 l'analisi dei rischi e la gestione dei problemi: codici dei rischi, indicatori, mitigazioni e registrazione degli eventi.

= Processi organizzativi

== Gestione dei processi

=== Scopo e aspettative
La gestione dei processi organizza il lavoro del gruppo: chi fa cosa, quando ci si riunisce, come si comunica e come si tracciano le attività. Il gruppo si aspetta ruoli chiari, riunioni regolari con verbale e nessuna attività fuori dal tracciamento.

=== Ruoli
Il gruppo usa i sei ruoli del regolamento.
- Responsabile: pianifica e coordina il lavoro, manda l'ordine del giorno delle riunioni, gestisce la casella email del gruppo, approva i rilasci, presenta il diario di bordo.
- Amministratore: cura repository, strumenti, controlli automatici, sito, board delle issue ed etichette; norma gli strumenti prima di introdurli.
- Analista: studia capitolati e requisiti, scrive la Valutazione dei capitolati e l'Analisi dei Requisiti, prepara le domande per i proponenti.
- Progettista: definisce l'architettura e la progettazione di dettaglio.
- Programmatore: scrive codice e test.
- Verificatore: verifica i prodotti degli altri membri e le pull request.

=== Rotazione dei ruoli
- Ogni membro ricopre un ruolo alla volta.
- Nessuno verifica un proprio prodotto.
- Fino al 2026-11-02 i ruoli sono quelli decisi il 2026-10-16: Responsabile Matteo Bellato, Amministratore Davide Baraldo, Analisti Patrizio Eleuteri e Oussama Mahdi, Verificatori Alessandro Paduret e David Sirbu.
- Dal 2026-11-03 il gruppo lavora per sprint di due settimane e i ruoli ruotano a ogni sprint, secondo la tabella della Dichiarazione degli impegni.
- Ogni membro copre almeno uno sprint per ciascuno dei sei ruoli entro la consegna.
- Nessuno è Responsabile per due sprint di fila.
- Le consegne di ruolo si passano all'apertura dello sprint.
- Ogni periodo è registrato in `dati/ruoli.csv`, con inizio, fine, membro e ruolo. I controlli automatici usano questo file.

=== Riunioni
Il gruppo tiene due riunioni interne a settimana su Discord, nei giorni e orari fissati dal Responsabile a inizio settimana. Una riunione straordinaria si convoca su Telegram con almeno un giorno di anticipo.

Procedura:
+ Il giorno prima il Responsabile pubblica su Telegram l'ordine del giorno, con i punti e il tempo previsto.
+ Il Responsabile conduce la riunione. Il redattore prende appunti. Il redattore cambia a ogni riunione, in ordine alfabetico di cognome, saltando il Responsabile.
+ Per ogni punto il gruppo registra una decisione con la sua motivazione. Per ogni decisione che richiede lavoro il gruppo fissa un'azione, un assegnatario e una scadenza.
+ Il redattore scrive il verbale entro 48 ore, secondo la procedura dei verbali.

=== Comunicazione
- Il gruppo si coordina su Telegram. Il canale serve per avvisi, domande brevi e convocazioni.
- Le riunioni si tengono su Discord.
- Con proponenti e docenti il gruppo scrive solo dalla casella sw2corporation\@gmail.com, gestita dal Responsabile in carica. La casella inoltra ogni messaggio a tutti i membri.
- Le email ai docenti contengono solo link, mai allegati.
- Le decisioni si prendono in riunione e stanno nei verbali. Una decisione presa in chat va confermata nel verbale successivo.

=== Tracciamento delle attività
Ogni attività del gruppo è una issue GitHub nella board del progetto. Una issue ha:
- un titolo all'imperativo, che dice cosa fare;
- un assegnatario, un solo membro;
- la scadenza e il ruolo con cui si svolge;
- la stima in ore, dal 2026-11-03;
- l'origine: la decisione del verbale o il documento che la richiede;
- i criteri di accettazione: le condizioni specifiche del prodotto della issue, ognuna verificabile con un sì o con un no.

La issue passa per gli stati della board: da fare, in corso, fatto. Una issue passa a fatto solo quando soddisfa la Definition of Done. Di norma la chiude l'integrazione della pull request. Le etichette distinguono il ruolo, il documento e il tipo di attività; le crea l'Amministratore.

Dal 2026-11-03 ogni membro registra ogni settimana le ore produttive per ruolo e le ore di orologio in `dati/ore.csv`. Il gruppo norma entro il 2026-11-02 il ciclo dello sprint: preventivo di periodo, consuntivo, retrospettiva e preventivo a finire.

=== Definition of Done
La Definition of Done dice quando il lavoro è fatto. Il lavoro che non la soddisfa non è fatto: non esiste uno stato "quasi fatto" e il lavoro non fatto non entra nel valore conseguito del periodo. Fatto non vuol dire approvato: l'approvazione del Responsabile autorizza il rilascio di un documento e viene dopo.

Una issue è fatta quando la sua pull request è integrata su `main`. La protezione di `main` permette l'integrazione solo con il controllo `verifica` verde, l'approvazione di un membro diverso dall'autore e tutte le conversazioni risolte. Una issue che non modifica il repository, per esempio un'email o un incontro, è fatta quando riporta l'evidenza del risultato e un altro membro la conferma con un commento.

Una issue che modifica un documento è fatta solo se la versione e la data dell'ultimo aggiornamento del documento sono aggiornate con la modifica, secondo le regole del suo tipo. Il PDF le riporta e il sito le mostra quando il documento è pubblicato. La Lettera di Presentazione ha solo la data; le slide del diario di bordo solo la versione.

Uno sprint è fatto quando ogni sua issue è fatta oppure torna da fare con la stima residua. Una consegna è fatta quando ogni documento consegnato ha la riga di approvazione del Responsabile.

Procedura:
+ Chi apre una issue scrive i criteri di accettazione.
+ Il verificatore approva la pull request solo se il prodotto soddisfa i criteri di accettazione e supera la lista di controllo del suo tipo, nella sezione Verifica. Altrimenti chiede le modifiche.

Chi trova una issue fatta che non soddisfa la Definition of Done la riapre e scrive la condizione mancata. Il gruppo modifica la Definition of Done solo con una decisione a verbale, che vale dall'apertura dello sprint successivo.

Strumenti: protezione di `main` su GitHub, configurata dall'Amministratore; modello di pull request `.github/pull_request_template.md`; workflow `Verifica`. Metriche: MPC-06.

== Infrastruttura
#figure(
  table(
    columns: (auto, 1fr, auto),
    table.header([Strumento], [Uso], [Versione]),
    [GitHub], [Organizzazione SW2-Corporation: repository, issue, board, pull request], [--],
    [GitHub Actions], [Workflow `Verifica` e `Pubblicazione`: controlli, test, compilazione e sito], [--],
    [GitHub Pages], [Sito della documentazione, con il cruscotto], [--],
    [Typst], [Compilazione dei documenti con il modello del gruppo], [0.15.1],
    [Python], [Controlli automatici, test e generazione del sito, senza librerie esterne], [3.11 o successiva],
    [Git], [Controllo di versione, con l'identità del membro], [--],
    [Discord], [Riunioni], [--],
    [Telegram], [Coordinamento interno], [--],
    [Casella email del gruppo], [Comunicazioni con proponenti e docenti], [--],
  ),
  caption: [Strumenti del gruppo],
)

Ogni membro installa Git, Typst e Python, clona il repository della documentazione e imposta nome e cognome nella configurazione git del clone. Il file `README.md` del repository spiega i comandi: `make` compila i documenti, `make verifica` esegue i controlli, `make test` esegue i test, `make sito` genera il sito in locale.

Chi introduce uno strumento nuovo scrive prima la norma che ne regola l'uso in questo documento.

== Miglioramento
Il gruppo norma entro il 2026-11-02 il miglioramento dei processi. L'impostazione decisa il 2026-10-16 è questa: quando una retrospettiva o una metrica mostra un problema in un processo, il gruppo apre su quel processo un ciclo PDCA con una metrica e un obiettivo. Il gruppo prova la modifica, ne misura l'effetto e poi la adotta in queste norme, la abbandona o ripete il ciclo. Il verbale di retrospettiva registra ogni ciclo.

== Formazione
Ogni membro impara uno strumento prima di usarlo nel progetto. La fonte principale è la documentazione ufficiale dello strumento e il `README.md` del repository. Chi conosce già uno strumento prepara una breve sessione per gli altri, nella riunione in cui lo strumento viene adottato. Le lezioni del corso sono la fonte per i processi e i documenti.

= Metriche
Le metriche di processo hanno codice MPC-nn, quelle di prodotto MPD-nn. I codici sono unici e non si riusano. Le soglie stanno nel Piano di Qualifica.

#figure(
  table(
    columns: (auto, 1.1fr, 1.5fr, 1.3fr, 1fr),
    table.header([Codice], [Nome], [Formula], [Scopo], [Strumento]),
    [MPC-01], [Puntualità dei verbali], [Ore tra la fine della riunione e l'apertura della pull request del verbale], [Verbali scritti entro 48 ore], [Orari del verbale e della pull request],
    [MPC-02], [Tempo di ciclo delle pull request], [Ore tra apertura e integrazione di una pull request], [Verifiche rapide, lavoro non bloccato], [GitHub],
    [MPC-03], [Indice di leggibilità], [89 + (300 × frasi − 10 × lettere) / parole, per documento], [Documenti leggibili], [`strumenti/verifica.py`],
    [MPC-04], [Azioni tracciate], [Azioni dei verbali con issue / azioni totali], [Nessuna azione fuori dal tracciamento], [`strumenti/verifica.py`],
    [MPC-05], [Errori dei controlli automatici], [Numero di errori segnalati dai controlli su `main`], [Repository sempre conforme alle norme], [Workflow `Verifica`],
    [MPC-06], [Issue riaperte], [Issue riaperte nel periodo / issue fatte nel periodo], [Nessun lavoro dichiarato fatto senza esserlo], [Eventi delle issue su GitHub],
  ),
  caption: [Metriche di processo definite],
)
