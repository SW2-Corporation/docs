# Ruoli e rotazione

Ruoli di progetto di SW2 Corporation, con i cambi nel tempo. La fonte dei periodi è `dati/ruoli.csv`, che alimenta i controlli automatici; questo file spiega le regole e riporta la tabella leggibile.

## Regole

Decise nella riunione interna del 2026-10-16 (decisioni VI-2026-10-16.2, VI-2026-10-16.3 e VI-2026-10-16.4) e fissate nella Dichiarazione degli impegni v1.0.0, approvata il 2026-10-29:

- dal 2026-11-03 si lavora per sprint di due settimane, dal martedì al lunedì di due settimane dopo;
- i ruoli cambiano a turni; all'inizio un turno dura uno sprint;
- in seguito un turno può durare meno di uno sprint, per esempio una settimana: la durata cambia con una decisione a verbale e vale dall'apertura dello sprint successivo;
- un ruolo a testa per turno;
- nessuno verifica un proprio prodotto: documenti e verbali li verifica un Verificatore, sito e strumenti un Verificatore o l'Amministratore;
- nessuno è Responsabile per due turni di fila, compreso il passaggio dalla candidatura al primo sprint;
- entro la consegna ogni membro copre ciascuno dei sei ruoli per almeno un turno;
- le consegne di ruolo si passano all'inizio del turno.

I sei ruoli sono Responsabile, Amministratore, Analista, Progettista, Programmatore e Verificatore.

## Periodo della candidatura

Dal 2026-10-16 al 2026-11-02, fino all'aggiudicazione del 2026-11-03.

| Ruolo | Membro |
|---|---|
| Responsabile | Matteo Bellato |
| Amministratore | Davide Baraldo |
| Analista | Patrizio Eleuteri |
| Analista | Oussama Mahdi |
| Verificatore | Alessandro Paduret |
| Verificatore | David Sirbu |

Progettista e Programmatore non sono assegnati: prima dell'aggiudicazione non ci sono attività di progettazione né di codifica.

## Rotazione per sprint

Matrice di rotazione della Dichiarazione degli impegni v1.0.0, dall'aggiudicazione del 2026-11-03 alla consegna del 2027-03-19. Vale finché un turno dura uno sprint: se i turni si accorciano, il gruppo la aggiorna con la stessa decisione a verbale.

| Sprint | Periodo |
|---|---|
| S1 | 2026-11-03 → 2026-11-16 |
| S2 | 2026-11-17 → 2026-11-30 |
| S3 | 2026-12-01 → 2026-12-14 |
| S4 | 2026-12-15 → 2026-12-28 |
| S5 | 2026-12-29 → 2027-01-11 |
| S6 | 2027-01-12 → 2027-01-25 |
| S7 | 2027-01-26 → 2027-02-08 |
| S8 | 2027-02-09 → 2027-02-22 |
| S9 | 2027-02-23 → 2027-03-08 |
| S10 | 2027-03-09 → 2027-03-22 |

| Membro | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | S9 | S10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Davide Baraldo | AN | VE | PO | RE | AN | AM | PR | VE | PO | AM |
| Matteo Bellato | AM | AN | PR | VE | PO | VE | AN | PO | AM | RE |
| Patrizio Eleuteri | RE | AN | VE | PO | PR | RE | PO | AM | VE | PO |
| Oussama Mahdi | AN | RE | AN | VE | AM | PR | RE | PO | VE | PR |
| Alessandro Paduret | PR | AM | RE | AN | VE | PO | PO | RE | PO | VE |
| David Sirbu | VE | PO | AM | PR | RE | AN | VE | PR | RE | VE |

Legenda: RE Responsabile, AM Amministratore, AN Analista, PR Progettista, PO Programmatore, VE Verificatore.

In ogni sprint c'è un solo Responsabile e almeno un Verificatore. Negli sprint 4 e 7, di festività e di esami, non è previsto l'Amministratore.

## Come si aggiorna

A ogni cambio di ruolo:

1. aggiungere la riga in `dati/ruoli.csv` con inizio, fine, membro e ruolo, senza sovrapporre i periodi dello stesso membro;
2. aggiornare la tabella di questo file;
3. riportare il cambio nel verbale della riunione che lo decide.

## Storico delle modifiche

| Data | Modifica |
|---|---|
| 2026-10-30 | Regole e matrice di rotazione allineate alla Dichiarazione degli impegni v1.0.0 (decisione VI-2026-10-30.1). |
| 2026-10-18 | Prima versione: ruoli della candidatura e proposta di rotazione per sprint. |
