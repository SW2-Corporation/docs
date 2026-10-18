#import "/modello/documento.typ": documento
#import "/modello/comuni.typ": g, rif-doc, rif-web

#show: documento.with(
  titolo: "Valutazione dei capitolati",
  uso: "esterno",
  destinatari: ("Prof. Tullio Vardanega", "Prof. Riccardo Cardin"),
  registro: csv("valutazione-capitolati.registro.csv"),
)

= Introduzione

== Scopo del documento
// Cosa contiene il documento e a chi si rivolge.

== Glossario
// Come sono marcati i termini (pedice G alla prima occorrenza, mai nei titoli) e dove si consulta il glossario.

== Riferimenti

=== Riferimenti normativi
// Regolamento del progetto didattico e capitolati, con rif-doc o rif-web e data di ultimo accesso.

=== Riferimenti informativi
// Slide del corso e altre fonti consultate.

= Criteri di valutazione
// Criteri adottati per confrontare i capitolati e loro peso nella scelta.

= Analisi dei capitolati
// Per ogni capitolato: dominio, requisiti principali, tecnologie, vincoli, punti di forza,
// criticità e rischi, competenze da acquisire, esito degli incontri esplorativi.

== C0 - AIRA
// Proponente: Sanmarco Informatica.

== C1 - AURA
// Proponente: Vimar.

== C2 - Concierge
// Proponente: Eggon.

== C3 - Fossdot
// Proponente: Uranion EMEA.

== C4 - GVSPV
// Proponente: M31.

== C5 - RareCare
// Proponente: Miriade.

== C6 - Var Group
// Caching semantico e dashboard FinOps che estende LiteLLM.

== C7 - SmartDashboard
// Proponente: Ergon Informatica.

== C8 - Sonar
// Proponente: Halue.

== C9 - SpecCheck
// Proponente: Zucchetti.

= Confronto
// Confronto dei capitolati sui criteri: una tabella (dentro una figure) e il suo commento.

= Capitolato scelto e motivazioni
// Capitolato scelto, motivazioni e preferenze subordinate.
