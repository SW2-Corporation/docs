#import "/modello/documento.typ": documento
#import "/modello/comuni.typ": g, impegni, rif-doc, rif-web, tabella-costi, tabella-ore

#show: documento.with(
  titolo: "Dichiarazione degli impegni",
  uso: "esterno",
  destinatari: ("Prof. Tullio Vardanega", "Prof. Riccardo Cardin"),
  registro: csv("dichiarazione-impegni.registro.csv"),
)

= Introduzione

== Scopo del documento
// Cosa dichiara il documento e a chi si rivolge.

== Glossario
// Come sono marcati i termini (pedice G alla prima occorrenza, mai nei titoli) e dove si consulta il glossario.

== Riferimenti

=== Riferimenti normativi
// Documenti versionati con rif-doc, risorse web con rif-web e data di ultimo accesso, ad esempio:
// - #rif-web("Regolamento del progetto didattico", "https://www.math.unipd.it/~tullio/IS-1/2026/Dispense/PD1.pdf", "AAAA-MM-GG")

=== Riferimenti informativi
// Slide del corso e altre fonti; gli standard ISO in una sola versione.

= Impegni
// Testo dell'impegno del gruppo. Scadenza e costo vengono da dati/gruppo.toml e dati/preventivo.toml.
#impegni()

= Ripartizione delle ore per membro e ruolo
// Criteri della ripartizione: ogni membro tra 80 e 95 ore e su tutti i ruoli.
// La tabella viene da dati/preventivo.toml.
#tabella-ore()

= Regole di rotazione dei ruoli
// Criteri e cadenza della rotazione (a ogni sprint) e vincoli: un ruolo alla volta, nessuno verifica il proprio lavoro.

= Preventivo
// Commento alla ripartizione del costo per ruolo, calcolata alle tariffe del regolamento.
#tabella-costi()
