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
- Verbale interno 2026-11-02, con le decisioni sulle procedure operative.
- Verbale esterno 2026-11-17, con le decisioni sull'estensione di OpenCode e sull'avvio dello sviluppo (VE-2026-11-17.2, VE-2026-11-17.8).

=== Riferimenti informativi
- ISO/IEC 12207:1995, Information technology, Software life cycle processes: la tassonomia dei processi usata in questo documento.
- #rif-web("Capitolati d'appalto 2026/27", "https://www.math.unipd.it/~tullio/IS-1/2026/Progetto/Capitolati.html", "2026-10-18").
- #rif-web("K. Schwaber, J. Sutherland, The Scrum Guide, novembre 2020", "https://scrumguides.org/scrum-guide.html", "2026-10-20").
- #rif-web("Processi di ciclo di vita, lezione T02 di Ingegneria del Software 2026/27", "https://www.math.unipd.it/~tullio/IS-1/2026/Dispense/T02.pdf", "2026-11-15").
- #rif-web("Gestione di progetto, lezione T04 di Ingegneria del Software 2026/27", "https://www.math.unipd.it/~tullio/IS-1/2026/Dispense/T04.pdf", "2026-11-15").
- #rif-web("OpenCode, Plugins", "https://opencode.ai/docs/build/plugins/", "2026-11-23").
- #rif-web("OpenSpec, Documentation", "https://openspec.dev/docs/", "2026-11-23").

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
+ Se il proponente rimanda il verbale firmato, l'Amministratore salva il PDF in un branch dedicato. Il file sta accanto al verbale, con lo stesso nome e l'estensione `.firmato.pdf`. L'Amministratore apre la pull request.
+ Un membro diverso dall'Amministratore verifica la copia firmata, approva la pull request e la integra su `main`.
+ Il sito pubblica la copia firmata al posto di quella compilata. Da quel momento il verbale non cambia: una correzione richiede una nuova versione e una nuova firma.

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

=== Scopo e aspettative
Il processo di sviluppo produce il software del capitolato: prima il #g("PoC"), poi l'MVP. Dal 2026-11-17 il gruppo sviluppa il PoC in parallelo all'Analisi dei Requisiti (VE-2026-11-17.8). Il gruppo si aspetta codice tipizzato, provato da test automatici e integrato su `main` solo dopo una verifica indipendente.

Il gruppo norma ogni attività prima di avviarla. Le norme di analisi dei requisiti e di progettazione entrano in questo documento prima dello sprint che le prevede.

=== Codifica del PoC
Quando: a ogni modifica del codice nel repository del prodotto. Ingressi: la issue con i criteri di accettazione. Uscite: codice e test integrati su `main`.

Regole:
- Il codice è in TypeScript. Il controllo dei tipi usa la modalità `strict` del file `tsconfig.json` del repository.
- Il codice usa solo sintassi che Node.js toglie senza trasformarla (`erasableSyntaxOnly`): niente `enum`, `namespace` né proprietà dichiarate nei parametri dei costruttori.
- Gli import locali riportano l'estensione `.ts`, per esempio `import { descriviStato } from "./stato.ts"`.
- Nomi, commenti e messaggi sono in italiano. Restano in inglese i nomi imposti dalle interfacce di OpenCode e di OpenSpec.
- Solo il punto d'ingresso del plugin e gli adattatori verso l'esterno usano l'interfaccia dei plugin di OpenCode. Il resto del codice non dipende da OpenCode.
- La logica si prova con test automatici che non richiedono OpenCode né un LLM. I test stanno in `test/`, in file con il suffisso `.test.ts`, e usano il modulo `node:test` di Node.js.
- L'architettura del prodotto e le sue motivazioni stanno nella Specifica Tecnica. Queste regole non la fissano.
- Il repository non contiene segreti. Chiavi, password e token stanno nelle variabili d'ambiente o nella configurazione locale di OpenCode.
- Ogni dipendenza ha la versione esatta in `package.json` e in `package-lock.json`. Una dipendenza nuova entra solo dopo che la tabella degli strumenti di queste norme la riporta.

Procedura:
+ Il Programmatore apre nel repository del prodotto il branch della issue.
+ Il Programmatore scrive i test della logica, poi il codice che li supera.
+ Il Programmatore esegue in locale `npm run verifica`, cioè controllo dei tipi e test, e corregge ogni errore.
+ Il Programmatore apre la pull request secondo la procedura della gestione della configurazione.

Strumenti: Node.js, npm, TypeScript, OpenCode, CLI di OpenSpec, repository del prodotto. Metriche: MPC-02, MPC-05.

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

=== Diari di bordo
Quando: ogni settimana, prima della presentazione ai docenti. Ingressi: i verbali e le issue della settimana. Uscite: il diario pubblicato sul sito.

I diari di bordo seguono l'iter dei verbali.

Procedura:
+ L'autore scrive il diario nel branch `diario/AAAA-MM-GG`, con la data della presentazione.
+ L'autore esegue i controlli automatici e apre la pull request.
+ Un membro diverso dall'autore verifica il diario e approva la pull request.
+ Il verificatore integra la pull request. Il sito pubblica il diario con la versione e la data dell'ultimo aggiornamento.

Il Responsabile presenta il diario ai docenti.
Durante le lezioni di presentazione dei diari è presente l'Amministratore, che sostituisce il Responsabile in caso di imprevisti.
Se l'Amministratore non può svolgere questa funzione, avvisa almeno 24 ore prima il Responsabile, che delega un sostituto su Telegram.
Nel caso il Responsabile sappia già prima della lezione di non poter svolgere la funzione, avvisa il gruppo su Telegram. Indica un sostituto per la presentazione oltre all'Amministratore. L'Amministratore presenta in via prioritaria, il sostituto è la riserva.

Strumenti: repository della documentazione, controlli automatici, modello del diario.

== Gestione della configurazione

=== Scopo e aspettative
La gestione della configurazione conserva la storia di ogni prodotto del gruppo e ne controlla le modifiche. Il gruppo si aspetta che ogni modifica sia tracciata da una issue, passi da una pull request verificata e che il sito mostri solo versioni approvate.

=== Repository
Il gruppo lavora nell'organizzazione GitHub SW2-Corporation, con due repository pubblici:
- `docs`, il repository della documentazione: dati del gruppo, modello Typst, documenti, verbali, strumenti di controllo e workflow;
- `speccheck`, il repository del prodotto: il codice di SpecCheck, a partire dal PoC.

Il codice del repository del prodotto è distribuito con la licenza open source MIT, riportata nel file `LICENSE`.

La struttura del repository della documentazione è fissa:
- `dati/`: gruppo, ruoli, ore, preventivo, glossario;
- `documenti/esterni/gestionali/` e `documenti/esterni/tecnici/`: documenti esterni con registro;
- `documenti/interni/`: documenti interni con registro;
- `documenti/lettere/`: Lettere di Presentazione;
- `documenti/verbali/interni/` e `documenti/verbali/esterni/`: verbali;
- `presentazioni/`: diari di bordo e altre presentazioni;
- `modello/`: il modello Typst;
- `strumenti/`: controlli automatici, test e generazione del sito.

La struttura del repository del prodotto è fissa:
- `src/`: il codice del plugin e la logica di SpecCheck;
- `test/`: i test automatici;
- `.opencode/plugins/speccheck/`: il punto d'ingresso da cui OpenCode carica il plugin;
- `esempi/`: i progetti di prova, con casi d'uso e modifiche proposte di OpenSpec con discrepanze note (VE-2026-11-17.7);
- `.github/`: workflow e modelli di issue e pull request;
- `package.json`, `package-lock.json` e `.npmrc`: le dipendenze, con le versioni esatte, e la versione di Node.js;
- `README.md`: installazione e avvio dell'ambiente, esecuzione dei test e delle skill;
- `LICENSE`: il testo della licenza MIT.

=== Branch e commit
Il branch `main` contiene solo lavoro verificato. Nessuno scrive direttamente su `main`: ogni modifica nasce in un branch e arriva su `main` con una pull request.

I branch prendono il nome dal tipo di lavoro:
- `verbale/AAAA-MM-GG` per un verbale;
- `diario/AAAA-MM-GG` per un diario di bordo, con la data della presentazione;
- `documento/nome-argomento` per un documento, per esempio `documento/norme-di-progetto-verifica`;
- `dati/argomento` per i dati del gruppo;
- `sito/argomento` per modello, strumenti e sito.

Nel repository del prodotto valgono le stesse regole, con altri tipi di lavoro:
- `funzione/argomento` per una funzione nuova o estesa, per esempio `funzione/confronto-casi-d-uso`;
- `correzione/argomento` per la correzione di un difetto;
- `ambiente/argomento` per dipendenze, configurazione di OpenCode, controlli e workflow.

Ogni commit porta l'identità git del membro, con nome e cognome. Il messaggio è in italiano. La prima riga descrive la modifica in al massimo 72 caratteri. Il corpo cita la issue con il suo numero, per esempio "Rif. \#12".

=== Pull request
Procedura:
+ L'autore apre la pull request verso `main`. Il titolo dice cosa cambia. La descrizione cita la issue nella forma `Closes #N`, così l'integrazione la chiude, e riporta il contenuto della modifica e come verificarla.
+ I controlli automatici devono risultare verdi. Un errore si corregge nel contenuto, mai nel controllo.
+ L'autore chiede la verifica a un membro diverso da sé. Per un documento e per il codice del prodotto è un Verificatore, per il sito e gli strumenti l'Amministratore o un Verificatore.
+ Il verificatore controlla la modifica con la #g("Definition of Done") e scrive l'esito come revisione della pull request: approvata oppure con le modifiche richieste.
+ A esito positivo il verificatore integra la pull request con un commit di merge, senza riscrivere la storia.
+ L'integrazione chiude la issue collegata.

Nel repository del prodotto il workflow `Verifica` installa le dipendenze con `npm ci` su una macchina pulita, controlla che OpenCode risponda con la versione fissata ed esegue `npm run verifica` a ogni pull request e a ogni integrazione: controllo dei tipi e test. La protezione di `main` ha le stesse regole del repository della documentazione.

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
- Amministratore: cura repository, strumenti, controlli automatici, sito, board delle issue ed etichette; salva nel repository i verbali firmati dai proponenti; norma gli strumenti prima di introdurli; aggiorna queste norme con i miglioramenti approvati; presenta il diario di bordo in assenza del Responsabile.
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
Il gruppo tiene due riunioni interne a settimana su Discord, il martedì alle 17:30 e il venerdì alle 18:00.

Una riunione straordinaria si convoca su Telegram con almeno un giorno di anticipo.

All'apertura di ogni riunione i presenti scelgono il redattore, per disponibilità o di comune accordo. Sono candidati tutti i presenti, tranne il Responsabile, che conduce la riunione, e l'unico Verificatore in carica, che deve poter verificare il verbale.
La scelta rispetta l'equa rotazione fra i membri, prediligendo membri che hanno scritto meno verbali.
Se nessuno si offre e non c'è accordo, il verbale lo scrive il candidato che ne ha scritti meno; a parità, il primo in ordine alfabetico di cognome.

Procedura:
+ Il giorno prima il Responsabile pubblica su Telegram l'ordine del giorno, con i punti e il tempo previsto.
+ Il Responsabile conduce la riunione. Il redattore, scelto in apertura, prende appunti.
+ Per ogni punto il gruppo registra una decisione con la sua motivazione. Per ogni decisione che richiede lavoro il gruppo fissa un'azione, un assegnatario e una scadenza.
+ Il redattore scrive il verbale entro 48 ore, secondo la procedura dei verbali.

=== Comunicazione
- Il gruppo si coordina su Telegram. Il canale serve per avvisi, domande brevi, convocazioni, proporre miglioramenti.
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

=== Indisponibilità
Quando: un membro sa di non poter finire una o più issue entro la scadenza. Ingressi: le issue del membro. Uscite: le issue riassegnate o tornate da fare.

Procedura:
+ Il membro avvisa il gruppo su Telegram appena lo sa, prima della scadenza. Per ogni issue indica lo stato e la stima residua.
+ Se può, il membro salva nel branch della issue il lavoro già fatto.
+ Entro 24 ore dall'avviso il Responsabile, sentito il gruppo, riassegna ogni issue. Rispetta il monte ore complessivo e il limite orario a persona, indicati nella Dichiarazione degli impegni.
+ Il Responsabile aggiorna nella issue assegnatario, ruolo e stima. Il nuovo assegnatario registra le ore con il ruolo che ricopre.
+ Se nessuno può prendere una issue, la issue torna da fare con la stima residua e il Responsabile ne aggiorna la scadenza.
+ Il verbale della riunione successiva conferma ogni riassegnazione con una decisione e un'azione.

Se l'indisponibile è il Responsabile, a riassegnare provvede l'Amministratore.

Strumenti: Telegram, issue.

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
    [OpenCode], [Agente di harness che carica il plugin di SpecCheck; pacchetto npm `@opencode/cli`], [2.3.2],
    [Interfaccia dei plugin di OpenCode], [Scrittura del plugin con `Plugin.define`; pacchetto npm `@opencode/plugin`], [2.3.2],
    [CLI di OpenSpec], [Sistema di specifiche con cui SpecCheck si integra: generazione e lettura delle modifiche proposte nelle prove e nei progetti di prova (VE-2026-11-17.2, VE-2026-11-17.7); pacchetto npm `@fission-ai/openspec`], [2.1.1],
    [TypeScript], [Linguaggio del plugin e della logica di SpecCheck, con il controllo dei tipi di `tsc`. Il plugin lo esegue OpenCode, test e controlli li esegue Node.js], [7.0.2],
    [Node.js], [Ambiente di esecuzione di test, controlli e CLI; esegue TypeScript senza compilarlo], [26 LTS],
    [npm], [Installazione delle dipendenze con le versioni esatte di `package-lock.json`], [quella di Node.js 26],
    [Discord], [Riunioni], [--],
    [Telegram], [Coordinamento interno], [--],
    [Casella email del gruppo], [Comunicazioni con proponenti e docenti], [--],
  ),
  caption: [Strumenti del gruppo],
)

Ogni membro installa Git, Typst e Python, clona il repository della documentazione e imposta nome e cognome nella configurazione git del clone. Il file `README.md` del repository spiega i comandi: `make` compila i documenti, `make verifica` esegue i controlli, `make test` esegue i test, `make sito` genera il sito in locale.

Per il repository del prodotto ogni membro installa anche Node.js 26. Il file `.npmrc` del repository contiene `engine-strict=true`, così npm non installa le dipendenze con una versione di Node.js diversa. Nel clone il membro esegue `npm ci`, che installa OpenCode, la CLI di OpenSpec e TypeScript nelle versioni della tabella. Avvia OpenCode dal clone con `npm run opencode`, che usa la versione fissata e non un'eventuale installazione globale. Il file `README.md` del repository del prodotto spiega i comandi.

Chi introduce uno strumento nuovo scrive prima la norma che ne regola l'uso in questo documento.

== Miglioramento

=== Scopo e aspettative
Il miglioramento valuta e corregge il modo di lavorare del gruppo per tutta la durata del progetto. Ha le tre attività di ISO/IEC 12207:1995: la definizione dei processi, cioè queste norme; la valutazione dei processi, nella retrospettiva di ogni sprint; il miglioramento, con il ciclo PDCA (Plan, Do, Check, Act). Il gruppo si aspetta che ogni modifica a un processo nasca da un problema documentato, abbia un obiettivo misurabile, sia approvata a verbale, entri in queste norme e sia verificata dopo l'uso.

Il ciclo PDCA agisce solo sui processi definiti in queste norme, mai sui prodotti. Ha quattro fasi:
- Plan: il gruppo trova la causa del problema e sceglie una modifica al processo, con un obiettivo e la metrica che lo misura;
- Do: la modifica entra in queste norme e il gruppo la applica;
- Check: alla data fissata il gruppo misura l'effetto e lo confronta con l'obiettivo;
- Act: il gruppo conferma la modifica, la corregge con un nuovo ciclo oppure la toglie.

Un ciclo prende l'identificativo della decisione a verbale che lo apre.

=== Fonti dei miglioramenti
Un ciclo parte da una di queste fonti:
- la retrospettiva di uno sprint;
- una metrica di processo o un indicatore del cruscotto fuori soglia;
- un rilievo del committente o del proponente sul modo di lavorare del gruppo, per esempio dopo una revisione di avanzamento;
- un problema segnalato da un membro durante il lavoro, come una norma ambigua o una procedura che blocca il lavoro;
- un problema che si ripete nei prodotti, per esempio lo stesso errore trovato in più verifiche, quando la causa sta in un processo.

Un rilievo sul modo di lavorare riceve una risposta nel verbale della riunione successiva. Il gruppo lo recepisce con un ciclo oppure lo respinge con una motivazione.

=== Valutazione dei processi
Quando: nella retrospettiva, cioè nella prima riunione di ogni sprint, sullo sprint appena concluso. Ingressi: il cruscotto, le metriche di processo, le proposte ricevute e i cicli con la verifica in scadenza. Uscite: il punto di retrospettiva del verbale, con decisioni e azioni.

Procedura:
+ Il Responsabile mette la retrospettiva al primo punto dell'ordine del giorno. Vi elenca le proposte ricevute e i cicli da verificare.
+ Il Responsabile dello sprint concluso presenta il cruscotto e le metriche di processo fuori soglia.
+ Ogni membro dice cosa ha funzionato e cosa no nel modo di lavorare, e perché.
+ Il gruppo verifica i cicli in scadenza, con la procedura del ciclo di miglioramento.
+ Per ogni problema di processo il gruppo cerca la causa. Poi apre un ciclo, rimanda il problema alla retrospettiva successiva oppure lo scarta. Un rinvio o uno scarto ha sempre una motivazione.
+ Il redattore riporta nella sintesi del punto cosa ha funzionato, cosa no e le cause trovate.

Strumenti: Discord, cruscotto, verbali.

=== Ciclo di miglioramento
Quando: per ogni problema di processo che il gruppo decide di affrontare. Ingressi: il problema e la sua evidenza. Uscite: la decisione a verbale, queste norme aggiornate e l'esito della verifica.

Procedura:
+ Ogni membro può proporre un miglioramento in qualsiasi momento. Scrive su Telegram il processo, il problema con la sua evidenza e la modifica proposta.
+ Il Responsabile mette la proposta all'ordine del giorno della prima riunione utile.
+ Il gruppo discute la proposta e cerca la causa del problema. Se la approva, il verbale registra una decisione. Il testo indica il processo, la modifica, l'obiettivo con la sua metrica e la data della verifica. La motivazione riporta il problema e la sua evidenza.
+ La decisione genera l'azione che aggiorna queste norme. La issue ha l'etichetta "miglioramento" e di norma va all'Amministratore.
+ L'assegnatario segue la procedura per scrivere un documento con registro. La descrizione della riga del registro cita la decisione.
+ La modifica vale dall'integrazione su `main`, salvo una data diversa fissata dalla decisione o da queste norme.
+ Alla data della verifica il Responsabile mette il ciclo all'ordine del giorno, di norma nella retrospettiva. Il gruppo misura la metrica e la confronta con l'obiettivo.
+ Una nuova decisione registra l'esito e cita quella del ciclo. Se l'obiettivo è raggiunto, la modifica resta. Altrimenti il gruppo apre un nuovo ciclo oppure toglie la modifica da queste norme, con un'azione e la sua issue.

Se un problema di processo blocca il lavoro e non può aspettare la riunione, il Responsabile decide una misura temporanea e la comunica su Telegram. Il verbale della riunione successiva la conferma con una decisione, che apre il ciclo.

Una correzione di queste norme che non cambia il modo di lavorare, come un errore di scrittura, non richiede un ciclo. Segue la sola procedura per scrivere un documento con registro.

Il Piano di Qualifica elenca i cicli aperti e chiusi, con decisione, obiettivo, metrica, data della verifica ed esito.

Strumenti: Telegram, verbali, issue con l'etichetta "miglioramento", repository della documentazione. Metriche: MPC-07, MPC-08.

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
    [MPC-07], [Cicli di miglioramento verificati], [Cicli con l'esito a verbale entro la data della verifica / cicli con la data della verifica scaduta], [Nessuna modifica ai processi senza misura dell'effetto], [Verbali],
    [MPC-08], [Cicli di miglioramento efficaci], [Cicli chiusi con l'obiettivo raggiunto / cicli chiusi], [Modifiche ai processi utili], [Verbali],
  ),
  caption: [Metriche di processo definite],
)
