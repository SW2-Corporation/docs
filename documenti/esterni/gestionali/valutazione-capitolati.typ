#import "/modello/documento.typ": documento
#import "/modello/comuni.typ": g, rif-doc, rif-web

#show: documento.with(
  titolo: "Valutazione dei capitolati",
  sottotitolo: "Analisi, confronto e motivazione della scelta dei capitolati d'appalto",
  uso: "esterno",
  destinatari: ("Prof. Tullio Vardanega", "Prof. Riccardo Cardin"),
  registro: csv("valutazione-capitolati.registro.csv"),
)

= Introduzione

== Scopo del documento
Questo documento illustra l'analisi condotta dal gruppo SW2 Corporation sui dieci capitolati d'appalto proposti per l'Anno Accademico 2026/2027 nel corso di Ingegneria del Software.

Vengono presentati i cinque criteri di valutazione stabiliti dal gruppo, la disamina critica di ciascuna proposta, la matrice decisionale riassuntiva e la motivazione della graduatoria finale con la scelta primaria e le scelte subordinate.

== Glossario
I termini tecnici o con significato specifico nel contesto del progetto sono raccolti nel glossario del gruppo. Alla loro prima occorrenza nel testo sono contrassegnati con una G a pedice. I titoli delle sezioni non contengono marcature.

== Riferimenti

=== Riferimenti normativi
- #rif-web("Regolamento del progetto didattico di Ingegneria del Software 2026/27 (PD1)", "https://www.math.unipd.it/~tullio/IS-1/2026/Dispense/PD1.pdf", "2026-10-18").
- #rif-doc("Norme di Progetto", "1.0.0").

=== Riferimenti informativi
- #rif-web("Capitolati d'appalto del corso di Ingegneria del Software 2026/27", "https://www.math.unipd.it/~tullio/IS-1/2026/Progetto/Capitolati.html", "2026-10-18").
- #rif-web("Capitolato C0 - AIRA: AI Requests Automation (Sanmarco Informatica)", "https://www.math.unipd.it/~tullio/IS-1/2026/Progetto/C0.pdf", "2026-10-18").
- #rif-web("Capitolato C1 - AURA: Smart Home Bluetooth Mesh (Vimar)", "https://www.math.unipd.it/~tullio/IS-1/2026/Progetto/C1.pdf", "2026-10-18").
- #rif-web("Capitolato C2 - Concierge: Virtual Concierge con IA (Eggon)", "https://www.math.unipd.it/~tullio/IS-1/2026/Progetto/C2.pdf", "2026-10-18").
- #rif-web("Capitolato C3 - FOSSDOT: Smart speaker open source (Uranion EMEA)", "https://www.math.unipd.it/~tullio/IS-1/2026/Progetto/C3.pdf", "2026-10-18").
- #rif-web("Capitolato C4 - GVSPV: Piattaforma gestione veicoli e servizi post-vendita (M31)", "https://www.math.unipd.it/~tullio/IS-1/2026/Progetto/C4.pdf", "2026-10-18").
- #rif-web("Capitolato C5 - RareCare: Piattaforma AI per malattie rare (Miriade)", "https://www.math.unipd.it/~tullio/IS-1/2026/Progetto/C5.pdf", "2026-10-18").
- #rif-web("Capitolato C6 - SCSDF: Caching semantico e dashboard FinOps (Var Group)", "https://www.math.unipd.it/~tullio/IS-1/2026/Progetto/C6.pdf", "2026-10-18").
- #rif-web("Capitolato C7 - SmartDashboard: BI self-service potenziata da AI (Ergon Informatica)", "https://www.math.unipd.it/~tullio/IS-1/2026/Progetto/C7.pdf", "2026-10-18").
- #rif-web("Capitolato C8 - Sonar: documentazione vivente di uno store Shopify (Halue)", "https://www.math.unipd.it/~tullio/IS-1/2026/Progetto/C8.pdf", "2026-10-18").
- #rif-web("Capitolato C9 - SpecCheck: tracciabilità casi d'uso, requisiti e codice (Zucchetti)", "https://www.math.unipd.it/~tullio/IS-1/2026/Progetto/C9.pdf", "2026-10-18").

= Criteri di valutazione

Per confrontare le dieci proposte con parametri trasparenti, il gruppo ha fissato cinque criteri:

1. *Interesse e tecnologie:* stimolo del dominio applicativo e utilità pratica delle tecnologie proposte per la crescita professionale del gruppo.
2. *Chiarezza dei requisiti:* livello di dettaglio della documentazione, separazione tra requisiti obbligatori e opzionali ed esplicitazione dei confini del sistema (non-obiettivi).
3. *Disponibilità del proponente:* canali di comunicazione, frequenza prevista per gli incontri di avanzamento e riscontro concreto alle richieste di contatto del gruppo.
4. *Innovazione e spendibilità:* originalità architetturale, presenza di standard aperti o industriali e valore dell'esperienza maturata.
5. *Fattibilità e gestione dei rischi:* rapporto tra complessità del prodotto e rischi tecnici, quali dipendenze da hardware dedicato, dati sensibili o librerie esterne poco controllabili.

= Analisi dei capitolati

== C0 - AIRA
Il capitolato C0, proposto da Sanmarco Informatica, chiede di automatizzare la gestione di richieste commerciali B2B non strutturate provenienti da email, messaggi vocali WhatsApp, file PDF e immagini. Il sistema deve estrarre le informazioni operative principali e convertirle in payload JSON per alimentare sistemi ERP e CRM tramite API REST.

Lo stack si basa su modelli linguistici multimodali per l'estrazione e strumenti di trascrizione vocale come Whisper, lasciando libera l'architettura software. L'azienda fornisce esempi di messaggi, mentre l'infrastruttura di inferenza e test resta a carico del gruppo.

Il punto debole principale riguarda l'ampia variabilità dei formati di ingresso. Gestire audio rumorosi, foto sfuocate e testi informali rende difficile garantire conversioni prive di errori o allucinazioni e complica la stesura di casi di test deterministici. Per affrontare il progetto servirebbe acquisire padronanza nel prompting con validazione di schemi JSON e nella gestione di flussi audio.

Il gruppo ha considerato l'idea interessante per l'automazione aziendale, ma i requisiti risultano troppo esposti a incertezze sui dati. Non abbiamo richiesto un incontro esplorativo e abbiamo attribuito al capitolato un punteggio di 16 su 25.

== C1 - AURA
La proposta di Vimar prevede lo sviluppo di una piattaforma di configurazione e supervisione per impianti domotici basati su rete Bluetooth Mesh, integrando server e client Model Context Protocol (MCP) per consentire a modelli intelligenti di interagire con sensori e attuatori fisici.

Le tecnologie comprendono il protocollo Bluetooth Mesh, architetture per gateway IoT, specifica MCP e autenticazione OAuth2.

Il limite critico del capitolato risiede nella forte dipendenza da hardware fisico o simulatori dedicati. Questa criticità è amplificata dalla dislocazione geografica dei membri del gruppo SW2 Corporation, che non condividono quotidianamente una sede fisica comune; la condivisione e il collaudo di dispositivi fisici distribuiti introdurrebbero complessi ostacoli logistici. Il rischio concreto è disperdere tempo ed energie su problemi di cablaggio, pairing e connettività a basso livello, sottraendo attenzione alla qualità architetturale e ai processi di sviluppo del software.

Il gruppo ha scelto di non richiedere l'incontro esplorativo per evitare il rischio di dipendenza da dispositivi fisici non facilmente accessibili a tutti. Punteggio: 13 su 25.

== C2 - Concierge
Eggon propone lo sviluppo di un assistente virtuale aziendale (concierge conversazionale basato sulla piattaforma interna NEXUM) dedicato ai dipendenti, con l'obiettivo di agevolare l'onboarding, l'accesso a policy aziendali, procedure HR e documentazione interna attraverso canali di messaggistica istantanea (quali Slack, Teams o Telegram) e un'interfaccia web.

L'architettura fa uso del pattern Retrieval-Augmented Generation (RAG), database vettoriali per la base di conoscenza aziendale e integrazioni con sistemi informativi interni. L'azienda fornisce documentazione di esempio, mentre i costi di inferenza dei modelli linguistici gravano sul gruppo.

Il sistema adotta un'impostazione ampiamente standard nel panorama applicativo attuale dei chatbot aziendali. Questo riduce i rischi realizzativi ma offre poca innovazione architetturale e pone il problema del controllo delle allucinazioni nelle risposte fornite ai dipendenti su tematiche interne sensibili. Le competenze da acquisire riguardano chunking, embedding vettoriali e guardrail di sicurezza per i modelli.

Ritenendo il progetto meno stimolante dal punto di vista dell'ingegneria del software rispetto ad altre alternative, il gruppo non ha richiesto l'incontro esplorativo. Punteggio: 14 su 25.

== C3 - Fossdot
Il capitolato di Uranion EMEA punta alla realizzazione di uno smart speaker completamente open source, con elaborazione vocale eseguita in locale su single-board computer per salvaguardare la riservatezza delle comunicazioni dell'utente.

Lo stack comprende modelli vocali compatti (Speech-to-Text e Text-to-Speech) eseguiti localmente, linguaggi ad alte prestazioni o Python ottimizzato e un'architettura modulare a plugin per collegare dispositivi domotici.

Sul piano tecnico, l'hardware a risorse ridotte impone un compromesso difficile tra tempi di risposta e accuratezza del riconoscimento vocale. C'è inoltre il pericolo concreto di disperdere il lavoro su driver audio, problemi di sistema operativo e ottimizzazione a basso livello.

Pur apprezzando il valore etico della tutela della privacy, il gruppo ha deciso di non richiedere l'incontro esplorativo a causa della marcata componente hardware e delle difficoltà di collaudo locale. Punteggio: 15 su 25.

== C4 - GVSPV
M31 propone una piattaforma distribuita con gestione logicamente centralizzata per governare i flussi post-vendita nel settore automobilistico, mettendo in comunicazione casa costruttrice, concessionarie e proprietari attraverso cinque flussi (anagrafica veicolo, compravendita, manutenzioni, campagne di richiamo e notifiche).

Lo stack di riferimento include un backend a microservizi sviluppato in Go e Node.js con framework Nest.js, message broker NATS per gli eventi asincroni, persistenza poliglotta con PostgreSQL, MongoDB e Redis, container Docker con orchestrazione Kubernetes e interfaccia web in Angular.

L'architettura distribuita enterprise rappresenta un ottimo banco di prova formativo. Tuttavia, il capitolato consiste in una presentazione sintetica di dieci slide, senza requisiti di dettaglio né criteri di accettazione già definiti. La configurazione iniziale di tanti componenti tecnologici eterogenei comporta un carico infrastrutturale non trascurabile.

Sul piano organizzativo, il gruppo ha inoltrato in data 2026-10-19 una richiesta formale di incontro esplorativo, ma M31 non ha fornito alcun riscontro. L'assenza prolungata di risposta, unita alla necessità di formalizzare i requisiti interamente da zero, ha portato il gruppo a penalizzare il punteggio sul supporto e a posizionare C4 al terzo posto della graduatoria, alle spalle di proposte con interlocuzione già felicemente avviata. Punteggio: 19 su 25.

== C5 - RareCare
Miriade propone una piattaforma collaborativa dedicata alle malattie rare, orientata alla raccolta standardizzata di percorsi clinici e al supporto decisionale per medici specialisti mediante algoritmi di correlazione clinica e clustering fenotipico.

Lo stack prevede algoritmi di intelligenza artificiale per il clustering, architettura a servizi web, standard sanitari di interoperabilità (HL7/FHIR) e rispetto dei vincoli GDPR per la protezione dei dati sensibili.

Il progetto mira a coinvolgere e supportare l'intera rete assistenziale che ruota attorno al malato raro, integrando pazienti, caregiver familiari, medici specialisti, pediatri e personale socio-sanitario per favorire l'aderenza terapeutica e la continuità di cura. La criticità principale risiede proprio nell'estrema frammentazione ed eterogeneità di questo ecosistema di attori, che rende ardua la corretta identificazione e delimitazione dei casi d'uso e dei confini del sistema. A ciò si aggiunge la delicatezza estrema dei vincoli normativi sul trattamento di dati clinici sensibili e la complessità degli standard sanitari, con il rischio di assorbire l'impegno del gruppo nella gestione di dinamiche burocratiche e relazionali anziché nello sviluppo software.

Considerata l'elevata complessità di dominio e le incertezze nei criteri di validazione, il gruppo non ha richiesto l'incontro esplorativo. Punteggio: 16 su 25.

== C6 - Var Group
Var Group propone di ottimizzare i consumi di inferenza dei modelli linguistici tramite caching semantico e una dashboard FinOps, intervenendo direttamente sulla libreria open source LiteLLM.

Il progetto richiede sviluppo in Python all'interno di LiteLLM, database vettoriali per la similarità degli embedding e dashboard web. Tra i vincoli figurano la consegna preventiva del modello dati, copertura test non inferiore al 70% in CI e una sessione obbligatoria di design thinking in presenza di tre ore.

La tematica del controllo dei costi dell'intelligenza artificiale è di interesse attuale. Tuttavia, operare direttamente come estensione di una libreria open source di terze parti espone a forti rischi di manutenzione e disallineamento rispetto al repository upstream, con frequenti aggiornamenti che rischiano di invalidare le modifiche del gruppo. Inoltre, l'attività richiesta è fortemente sbilanciata su benchmark quantitativi di latenza e consumi piuttosto che sulla progettazione di un sistema informativo completo e bilanciato.

C6 era stato inserito nella rosa preliminare del 2026-10-16, ma è stato sostituito in data 2026-10-18 da C7, che offre maggiore respiro architetturale e una migliore aderenza alle esigenze didattiche del gruppo. Incontro non richiesto. Punteggio: 17 su 25.

== C7 - SmartDashboard
Ergon Informatica propone una piattaforma di Business Intelligence self-service che permette a figure direzionali e operative di interrogare dati gestionali ERP tramite linguaggio naturale, traducendo le richieste in query SQL (Text-to-SQL) e componendo dashboard con grafici, tabelle pivot, indicatori KPI, mappe e filtri dinamici con esportazione.

L'architettura suggerita si articola su tre livelli: raw store, data warehouse a schema a stella (con DuckDB consigliato) e applicazione web. L'accesso ai modelli linguistici avviene via API commerciale (OpenAI o Anthropic). Il codice va rilasciato con licenza open source e l'azienda mette a disposizione un dataset d'impresa reale su richiesta del gruppo.

La proposta unisce un solido impianto di ingegneria dei dati con le potenzialità dei modelli linguistici. Le difficoltà tecniche principali riguardano la validazione semantica delle query SQL generate automaticamente, per evitare calcoli errati o join incoerenti su schemi complessi, e l'ampiezza della fase iniziale di Business Intelligence, che deve essere pienamente funzionante prima di innestare lo strato di intelligenza artificiale.

Nell'incontro esplorativo del 2026-10-20, il referente Gianluca Carlesso ha confermato che il dataset reale di studio può essere fornito al gruppo (da mantenere strettamente riservato ed escluso dal repository pubblico), la fornitura di credenziali API con plafond per l'accesso ai modelli linguistici (OpenAI o Anthropic) e la disponibilità di domande di business reali per i test di accettazione. L'azienda ha concordato la delimitazione del #g("Minimum Viable Product") sui widget core (tabelle, pivot, card con KPI, istogrammi e filtri dinamici), raccomandando un'architettura modulare con router e confermando supporto continuo e incontri quindicinali. Il gruppo ha tuttavia rilevato un margine di incertezza sulla strategia di verifica del software, poiché il committente non fissa soglie quantitative di copertura né un piano di test formale, rimandandone la definizione alla progettazione; tale aspetto richiederà al gruppo un presidio metodologico autonomo rigoroso per prevenire allucinazioni ed errori di generazione SQL. L'ottimo esito complessivo del confronto consolida saldamente C7 al secondo posto nella graduatoria del gruppo. Punteggio: 21 su 25.

== C8 - Sonar
Halue propone uno strumento di analisi statica del codice e documentazione vivente per store Shopify Plus. Sonar effettua scansioni in sola lettura di temi Liquid, configurazioni GraphQL, metadati, applicazioni installate e script, costruendo un grafo unificato delle dipendenze per identificare codice morto, configurazioni orfane e incongruenze prima del rilascio in produzione.

Lo stack tecnologico è ampio ma definito con estrema precisione e rigore: Next.js distribuito su Vercel (con Vercel Workflows e Cron per i processi asincroni), Supabase PostgreSQL con autenticazione Google e Row Level Security (RLS) per il controllo degli accessi a livello di database, TypeScript in configurazione strict e Shopify Admin GraphQL API. Il parser del linguaggio Liquid si basa su alberi sintattici astratti (AST) integrati con un motore di memorizzazione a grafo. La documentazione del capitolato fornisce obiettivi chiari, delimitati e verificabili su cosa va realizzato, evitando dispersioni.

I vincoli operativi sono chiari: Sonar opera in sola lettura senza compiere modifiche distruttive sullo store; l'ambiente di lavoro si appoggia ai piani gratuiti di Vercel, Supabase e a development store creati con Shopify Partners; la qualità è presidiata da soglie numeriche verificabili (copertura test almeno del 70% in CI, tasso di superamento test almeno del 95% e falsi positivi su regole ad alta severità inferiori al 10%).

I punti qualificanti del capitolato includono la suddivisione formale dei requisiti in obbligatori, desiderabili e opzionali, la delimitazione trasparente dei non-obiettivi, la prescrizione del modello architetturale C4 per la documentazione visiva e dei registri formali delle decisioni (#g("Architecture Decision Record")), e il perfetto allineamento con le scadenze didattiche di #g("Requirements and Technology Baseline") (per il #g("Proof of Concept")) e #g("Product Baseline").

Nell'incontro esplorativo tenutosi il 2026-10-20, il referente unico Valentino Baraldo ha confermato la piena disponibilità a concordare lo scope del Minimum Viable Product, privilegiando il disaccoppiamento architetturale del motore di regole rispetto alla mera quantità di regole iniziali, e ha garantito supporto quindicinale e tramite casella dedicata (`sonar@halue.io`).

C8 rappresenta la prima scelta unanime e indiscussa di SW2 Corporation. Punteggio: 24 su 25.

== C9 - SpecCheck
Zucchetti propone di realizzare skill e verifiche automatizzate nell'ambiente OpenCode per controllare la tracciabilità tra casi d'uso, requisiti software e codice sorgente tramite agenti intelligenti.

Le tecnologie si basano sull'ambiente OpenCode e sull'analisi semantica del codice tramite modelli linguistici.

Il tema del tracciamento è centrale per l'ingegneria del software. La natura marcatamente sperimentale e di ricerca del progetto comporta però confini applicativi sfumati e criteri di accettazione difficili da quantificare in modo deterministico, aumentando il rischio di non pervenire a un prodotto compiuto nei tempi del corso.

Il gruppo ha preferito non richiedere l'incontro esplorativo, orientandosi verso proposte con perimetro operativo e verifiche più definite. Punteggio: 18 su 25.

= Confronto

I punteggi attribuiti a ciascun capitolato sui cinque criteri concordati scaturiscono dalle discussioni collegiali svolte nelle riunioni interne del gruppo.

#figure(
  table(
    columns: (auto, 1fr, auto, auto, auto, auto, auto, auto),
    align: (left, left, center, center, center, center, center, center),
    table.header([*Cod.*], [*Capitolato*], [*Tecn.*], [*Req.*], [*Supp.*], [*Inn.*], [*Fatt.*], [*Totale*]),
    [C8], [Sonar (Halue)], [5], [5], [5], [5], [4], [*24*],
    [C7], [SmartDashboard (Ergon Informatica)], [4], [4], [5], [4], [4], [*21*],
    [C4], [GVSPV (M31)], [4], [4], [2], [5], [4], [*19*],
    [C9], [SpecCheck (Zucchetti)], [4], [3], [4], [4], [3], [*18*],
    [C6], [Var Group (LiteLLM FinOps)], [4], [3], [3], [4], [3], [*17*],
    [C0], [AIRA (Sanmarco Informatica)], [3], [3], [4], [3], [3], [*16*],
    [C5], [RareCare (Miriade)], [3], [3], [3], [4], [3], [*16*],
    [C3], [Fossdot (Uranion EMEA)], [3], [3], [3], [3], [3], [*15*],
    [C2], [Concierge (Eggon)], [3], [3], [3], [3], [2], [*14*],
    [C1], [AURA (Vimar)], [3], [2], [3], [3], [2], [*13*],
  ),
  caption: [Matrice di confronto e punteggi attribuiti ai capitolati d'appalto],
)

La graduatoria evidenzia tre livelli distinti:
- *Prima scelta:* il capitolato *C8 (Sonar)* guida la classifica con 24 punti su 25. Spicca per il rigore nella formulazione dei requisiti, l'impostazione metodologica chiara e la disponibilità dimostrata dal proponente durante l'incontro esplorativo.
- *Scelte subordinate:* i capitolati *C7 (SmartDashboard)* e *C4 (GVSPV)* seguono rispettivamente con 21 e 19 punti. Entrambi presentano architetture valide. C7 si colloca davanti a C4 grazie al riscontro tempestivo dell'azienda, alla disponibilità confermata di incontri regolari e alla chiarezza degli obiettivi emersa durante l'incontro esplorativo.
- *Altre proposte:* i restanti capitolati (da C9 a C1) presentano elementi di interesse ma risultano penalizzati da incertezze di perimetro, vincoli hardware complessi o limitata originalità architetturale.

= Capitolato scelto e motivazioni

== Scelta primaria: C8 - Sonar

Il gruppo SW2 Corporation ha scelto all'unanimità il capitolato *C8 - Sonar: documentazione vivente di uno store Shopify*, proposto da *Halue*, come prima scelta per il progetto didattico.

Le ragioni principali della scelta sono:

1. *Requisiti precisi e perimetro ben delimitato:* il capitolato cataloga con rigore i requisiti in obbligatori, desiderabili e opzionali, corredandoli di criteri di accettazione misurabili. L'esplicitazione dei non-obiettivi e la natura di sola lettura di Sonar mettono il gruppo al riparo da ambiguità e interventi distruttivi.
2. *Metodologia allineata alle Norme di Progetto:* la richiesta di documentare l'architettura con il modello visuale C4 (Context, Containers, Components, Code) e di tracciare le scelte tecniche con registri delle decisioni architetturali si integra in modo naturale con gli standard di qualità adottati dal gruppo.
3. *Interesse tecnologico concreto:* la combinazione tra analisi statica con parser Liquid AST e interrogazione di grafi di dipendenza rappresenta una sfida ingegneristica stimolante e formativa.
4. *Sostenibilità dell'ambiente di lavoro:* il progetto è pensato per funzionare interamente nei piani gratuiti di Vercel, Supabase e Shopify Partners, con regole concordate per monitorare i consumi ed evitare spese impreviste.
5. *Collaborazione affidabile con il proponente:* nell'incontro esplorativo del 2026-10-20, il referente Valentino Baraldo ha confermato la disponibilità a dialogare sullo scope del prodotto, con incontri quindicinali e supporto asincrono dedicato tramite casella email di progetto.

== Scelte subordinate: C7 e C4

A tutela della continuità operativa e per agevolare il coordinamento nell'assegnazione tra gruppi, SW2 Corporation ha definito le proprie preferenze di riserva:

- *Seconda scelta: C7 - SmartDashboard (Ergon Informatica):* la piattaforma di Business Intelligence self-service combina data warehousing su DuckDB e modelli linguistici per la generazione di query Text-to-SQL. Il gruppo ne apprezza l'utilità gestionale concreta e la solida impostazione architetturale. Nell'incontro esplorativo del 2026-10-20, il referente Gianluca Carlesso ha dimostrato disponibilità, concordando la focalizzazione dell'MVP sui widget core e mettendo a disposizione dataset reale, credenziali per le API e supporto continuativo.
- *Terza scelta: C4 - GVSPV (M31):* la piattaforma distribuita per la gestione del post-vendita nel settore automobilistico offre un'architettura enterprise a microservizi moderna e di ampio respiro (Go, Nest.js, NATS, Kubernetes). La collocazione al terzo posto è motivata dal fatto che M31 è l'unica azienda a non aver ancora risposto alla richiesta di contatto inviata il 2026-10-19. Inoltre, la documentazione basata su dieci slide sintetiche senza requisiti dettagliati aumenta i rischi di coordinamento iniziale rispetto a C7 e C8.
