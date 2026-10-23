"""Compila con typst i documenti pubblicabili e genera il sito statico.

Uso: python strumenti/sito.py --out site [--typst percorso]

Vanno sul sito i documenti rilasciati (prima riga del registro = approvazione),
tutte le lettere, tutti i verbali e tutti i diari di bordo, più le pagine del cruscotto,
della pianificazione, del gruppo e del glossario.
Ogni PDF ha la sua pagina di lettura (pdf.js), con lo stesso nome e l'estensione .html.
"""

import argparse
import csv
import datetime
import html
import json
import math
import re
import shutil
import subprocess
import sys
import tomllib
import unicodedata
from pathlib import Path

from verifica import RADICE, RUOLI, data_iso, nome_verbale, numero, rilascio, slug

ACCENTO_PREDEFINITO = "#d7262f"
SOTTOTITOLO = "Progetto didattico di Ingegneria del Software, Università degli Studi di Padova"
MESI = ("gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic")

# Tema scuro: usato sia quando il dispositivo lo preferisce sia quando l'utente lo sceglie.
TEMA_SCURO = """--carta: #0f0f0f; --inchiostro: #ece9e2; --tenue: #aaa69f; --filetto: #2e2e2e; --superficie: #1b1b1b;
  --piano: #262624; --piano-bordo: #3d3c39; --fatto: #4ade80; --corso: #82a8ff; --previsto: #8a867f; --ritardo: var(--accento-chiaro);
  --accento-testo: var(--accento-chiaro); --sole: block; --luna: none; color-scheme: dark;"""

# {accento} e {scuro} vengono sostituiti dal colore del gruppo e dal blocco del tema scuro.
# Carta e inchiostro; serif per i titoli, monospazio per date ed etichette.
# --accento-testo è la variante dell'accento usata per il testo: sugli sfondi scuri è schiarita
# per tenere il contrasto sopra 4,5:1. I colori dei ruoli reggono il testo bianco in entrambi i temi.
# Nel grafico delle ore --corso (consumate) e --previsto (previste) restano distinguibili anche con
# le discromatopsie; le previste sono anche tratteggiate.
STILE = """
@font-face { font-family: "Atkinson Hyperlegible Next"; src: url("font/atkinson-hyperlegible-next.woff2") format("woff2"); font-weight: 200 800; font-display: swap; }
@font-face { font-family: "Atkinson Hyperlegible Mono"; src: url("font/atkinson-hyperlegible-mono.woff2") format("woff2"); font-weight: 200 800; font-display: swap; }
:root { --accento: {accento}; --accento-chiaro: #f0545b; --accento-chiaro: color-mix(in srgb, var(--accento) 72%, white);
        --accento-testo: var(--accento); --carta: #faf9f6; --inchiostro: #141414; --tenue: #57564f; --filetto: #dcd9d2;
        --superficie: #f0eee8; --piano: #e9e6de; --piano-bordo: #cdc9be; --fatto: #15803d; --corso: #1d4ed8; --previsto: #8a877f;
        --ritardo: var(--accento);
        --sole: none; --luna: block; color-scheme: light;
        --sans: "Atkinson Hyperlegible Next", system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        --mono: "Atkinson Hyperlegible Mono", ui-monospace, "Cascadia Code", "SF Mono", Menlo, Consolas, "Liberation Mono", monospace; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { {scuro} } }
:root[data-theme="dark"] { {scuro} }
* { box-sizing: border-box; }
/* gli script nascondono elementi che nel CSS hanno un display proprio */
[hidden] { display: none !important; }
html { font-size: 106.25%; scroll-behavior: smooth; }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
body { margin: 0; font-family: var(--sans); font-size: 1.0625rem; line-height: 1.65; background: var(--carta); color: var(--inchiostro);
       -webkit-font-smoothing: antialiased; border-top: 3px solid var(--accento); }
a { color: inherit; }
:focus-visible { outline: 2px solid var(--accento-testo); outline-offset: 3px; }
.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; border: 0; }
.salta { position: absolute; left: 1rem; top: -4rem; z-index: 10; padding: .6rem 1rem; background: var(--inchiostro); color: var(--carta);
         font-size: .95rem; text-decoration: none; }
.salta:focus { top: 1rem; }
/* maiuscoletto monospazio solo per le etichette brevi; il testo da leggere resta a corpo pieno */
.kicker, .indice .titoletto { font-family: var(--mono); font-size: .8rem; letter-spacing: .06em; text-transform: uppercase; }
/* date, versioni e numeri in monospazio, con cifre allineate */
.mono, .utente, .asse, .data, .conta, .numeri { font-family: var(--mono); font-size: .85rem; font-variant-numeric: tabular-nums; }
.pagina { max-width: 74rem; margin: 0 auto; padding: 0 clamp(1rem, 4vw, 3rem); }

.testa { display: flex; align-items: center; flex-wrap: wrap; gap: .5rem 1rem; padding: .85rem 0; border-bottom: 1px solid var(--filetto); }
.marchio { display: inline-flex; align-items: center; gap: .8rem; margin-right: auto; text-decoration: none; color: var(--tenue); font-size: .95rem; }
.marchio img { width: 34px; height: 34px; border-radius: 50%; }
.marchio b { color: var(--inchiostro); font-weight: 700; }
.marchio .sep { padding: 0 .4rem; }
.marchio .sep, .marchio .sotto-marchio { display: none; }
@media (min-width: 75rem) { .marchio .sep, .marchio .sotto-marchio { display: inline; } }
/* menu delle pagine: su mobile va a capo sotto il marchio e scorre in orizzontale */
.menu { order: 3; flex-basis: 100%; overflow-x: auto; scrollbar-width: none; }
.menu::-webkit-scrollbar { display: none; }
.menu ul { display: flex; gap: .25rem; list-style: none; margin: 0; padding: 0; }
.menu a { display: block; padding: .5rem .85rem; border-radius: 8px; color: var(--tenue); font-weight: 600; text-decoration: none; white-space: nowrap; }
.menu a:hover { background: var(--superficie); color: var(--inchiostro); }
.menu a[aria-current="page"] { background: var(--inchiostro); color: var(--carta); }
@media (max-width: 30rem) { .menu ul { display: grid; grid-template-columns: 1fr 1fr; } .menu a { text-align: center; } }
@media (min-width: 48rem) { .menu { order: 0; flex-basis: auto; } }
.tema { width: 2.75rem; height: 2.75rem; display: grid; place-items: center; border: 0; border-radius: 50%; background: transparent;
        color: var(--inchiostro); cursor: pointer; }
.tema:hover { background: var(--superficie); }
.tema svg { width: 20px; height: 20px; }
.tema .sole { display: var(--sole); }
.tema .luna { display: var(--luna); }

.apertura { padding: clamp(3rem, 8vw, 6rem) 0 2.5rem; border-bottom: 1px solid var(--inchiostro); }
.apertura.compatta { padding-top: clamp(2rem, 5vw, 3.5rem); padding-bottom: 2rem; }
.kicker { margin: 0 0 1rem; color: var(--accento-testo); }
.titolone { margin: 0; font-weight: 700; font-size: clamp(2.8rem, 8vw, 6rem); line-height: .96; letter-spacing: -.025em; text-wrap: balance; }
.compatta .titolone { font-size: clamp(2.2rem, 5vw, 3.6rem); }
.titolone .accento { color: var(--accento-testo); }
.sotto { margin: 1.25rem 0 0; max-width: 38rem; font-size: 1.15rem; color: var(--tenue); }
.meta { list-style: none; margin: 1.75rem 0 0; padding: 0; display: flex; flex-wrap: wrap; gap: .4rem 1.5rem; color: var(--tenue); font-size: .95rem; }
.meta a { color: var(--inchiostro); text-decoration: none; border-bottom: 1px solid var(--filetto); }
.meta a:hover { border-color: var(--accento-testo); color: var(--accento-testo); }

/* in home: a che punto è il progetto, con il link alla pianificazione */
.stato-progetto { display: flex; flex-wrap: wrap; align-items: center; gap: .4rem 1.5rem; margin: 1.75rem 0 0; padding: .9rem 1.1rem;
                  border: 1px solid var(--filetto); border-radius: 8px; background: var(--superficie); font-size: .95rem; }
.stato-progetto b { font-weight: 700; }
.stato-progetto a { margin-left: auto; color: var(--inchiostro); font-weight: 700; text-decoration: none; border-bottom: 1px solid var(--inchiostro); }
.stato-progetto a::after { content: " →"; color: var(--accento-testo); }

.colonne { display: grid; grid-template-columns: minmax(0, 1fr); }
/* su mobile l'indice è una barra fissa a tutta larghezza che scorre in orizzontale */
.indice { position: sticky; top: 0; z-index: 5; min-width: 0; display: flex; align-items: center; gap: 1.25rem;
          margin: 0 calc(-1 * clamp(1rem, 4vw, 3rem)); padding: 0 clamp(1rem, 4vw, 3rem); overflow-x: auto; scrollbar-width: none;
          background: var(--carta); border-bottom: 1px solid var(--filetto); }
.indice::-webkit-scrollbar { display: none; }
.indice .titoletto { display: none; margin: 0 0 .6rem; color: var(--tenue); }
.indice ol { display: flex; gap: 1.25rem; list-style: none; margin: 0; padding: 0; }
.indice li { flex: none; }
.indice ol a { display: block; padding: .9rem 0; color: var(--tenue); font-size: .95rem; text-decoration: none; border-bottom: 2px solid transparent; white-space: nowrap; }
.indice ol a:hover, .indice ol a[aria-current="true"] { color: var(--inchiostro); }
.indice ol a[aria-current="true"] { border-bottom-color: var(--accento); }
@media (min-width: 60rem) {
  .colonne { grid-template-columns: 13rem minmax(0, 1fr); gap: 0 5rem; }
  .indice { top: 1.5rem; align-self: start; display: block; margin: 0; padding: 2.5rem 0 0; overflow: visible; background: transparent; border-bottom: 0; }
  .indice .titoletto { display: block; }
  .indice ol { display: block; }
  /* la sezione che si sta leggendo ha la barra d'accento a sinistra */
  .indice ol a { padding: .55rem 0 .55rem 1rem; border-bottom: 0; border-left: 2px solid var(--filetto); white-space: normal; }
  .indice ol a[aria-current="true"] { border-left-color: var(--accento); font-weight: 700; }
}

.sezioni { min-width: 0; }
.sezione { padding: 2.5rem 0; border-bottom: 1px solid var(--filetto); scroll-margin-top: 4rem; }
@media (min-width: 60rem) { .sezione { scroll-margin-top: 1rem; } }
.sezione:last-child { border-bottom: 0; }
.sezione h2 { margin: 0; font-weight: 700; font-size: clamp(1.7rem, 3vw, 2.3rem); line-height: 1.1; letter-spacing: -.01em; }
.sezione h2 .conta { display: inline-block; margin-left: .7rem; padding: .1rem .55rem; border-radius: 999px; background: var(--superficie);
                     color: var(--tenue); font-size: .8rem; line-height: 1.4; vertical-align: .45em; }
.sezione h3 { margin: 1.75rem 0 .25rem; font-size: 1.05rem; font-weight: 600; }
.sezione > p { margin: 1rem 0 0; max-width: 42rem; }
.vuoto, .nota { margin: 1rem 0 0; max-width: 42rem; color: var(--tenue); font-size: .95rem; }
.vuoto::before { content: "— "; }
.sezione .intro { margin: .5rem 0 0; max-width: 42rem; color: var(--tenue); }
/* voce di un elenco: titolo e dettagli a sinistra, PDF a destra */
ol.voci { list-style: none; margin: .5rem 0 0; padding: 0; }
.voce { display: grid; grid-template-columns: minmax(0, 1fr) auto; align-items: center; gap: .25rem 1rem; padding: .85rem 0;
        border-top: 1px dotted var(--filetto); }
.voce:first-child { border-top: 0; }
.voce .titolo { font-size: 1.15rem; font-weight: 600; line-height: 1.35; text-decoration: none; }
.voce .titolo:hover { color: var(--accento-testo); text-decoration: underline; text-underline-offset: .18em; }
.voce .dettaglio { grid-column: 1; color: var(--tenue); font-size: .95rem; }
.voce .pdf { grid-column: 2; grid-row: 1 / span 2; display: inline-flex; align-items: center; min-height: 2.75rem; padding: 0 .9rem;
             border: 1px solid var(--piano-bordo); border-radius: 8px; color: var(--inchiostro); font-size: .9rem; font-weight: 600;
             text-decoration: none; white-space: nowrap; }
.voce .pdf::after { content: " ↓"; white-space: pre; color: var(--accento-testo); }
.voce .pdf:hover { border-color: var(--accento-testo); color: var(--accento-testo); }
/* la lettera più recente è la prima cosa da aprire */
.in-evidenza .voce:first-child { padding: 1rem 1.1rem; border: 1px solid var(--piano-bordo); border-radius: 8px; background: var(--superficie); }
.approvazione { font-weight: 600; }
.a-approvato .icona { color: var(--fatto); }
.a-attesa { color: var(--accento-testo); }

ul.persone { list-style: none; margin: .75rem 0 0; padding: 0; }
.persona { display: flex; align-items: center; flex-wrap: wrap; gap: .5rem 1rem; padding: .8rem 0; border-top: 1px dotted var(--filetto); }
.persona:first-child { border-top: 0; }
.persona img, .persona .iniziali { width: 36px; height: 36px; border-radius: 50%; flex: none; }
.persona img { filter: grayscale(1); }
.persona:hover img { filter: none; }
.persona .iniziali { display: inline-grid; place-items: center; background: var(--inchiostro); color: var(--carta); font-family: var(--mono); font-size: .72rem; }
.persona .nome { font-size: 1.2rem; flex: 1 1 10rem; }
.persona .utente { color: var(--tenue); text-decoration: none; }
.persona .utente:hover { color: var(--accento-testo); }
/* su schermi stretti l'utente va a capo, allineato al nome */
@media (max-width: 40rem) { .persona .utente { flex-basis: 100%; padding-left: calc(36px + 1rem); margin-top: -.4rem; } }
.ruolo { display: inline-block; padding: .22rem .6rem; border-radius: 3px; color: #fff; font-size: .82rem; font-weight: 600; line-height: 1.3; white-space: nowrap; }
.r-responsabile { background: var(--accento); } .r-amministratore { background: #1d4ed8; } .r-analista { background: #047857; }
.r-progettista { background: #b45309; } .r-programmatore { background: #6d28d9; } .r-verificatore { background: #0e7490; }

.legenda { display: flex; flex-wrap: wrap; gap: .5rem 1.4rem; list-style: none; margin: 1.25rem 0 0; padding: 0; color: var(--tenue); font-size: .95rem; }
.legenda i { display: inline-block; width: .8rem; height: .8rem; margin-right: .5rem; vertical-align: -.05rem; border-radius: 2px; }
.linea { --colonna: 12rem; position: relative; margin-top: 1.5rem; }
.asse { position: relative; height: 2.6rem; margin-left: var(--colonna); color: var(--tenue); }
.asse span { position: absolute; bottom: 0; transform: translateX(-50%); white-space: nowrap; }
.asse span::before { content: ""; display: block; width: 1px; height: .45rem; margin: 0 auto .2rem; background: var(--filetto); }
.asse span.inizio { transform: none; } .asse span.inizio::before { margin-left: 0; }
.asse span.fine { transform: translateX(-100%); } .asse span.fine::before { margin-right: 0; }
.riga { display: grid; grid-template-columns: var(--colonna) 1fr; align-items: center; border-top: 1px dotted var(--filetto); }
.chi { font-size: 1.05rem; padding: .6rem .75rem .6rem 0; }
.traccia { position: relative; height: 2.4rem; }
.barra { position: absolute; top: .5rem; bottom: .5rem; display: flex; align-items: center; padding: 0 .5rem; border-radius: 2px; color: #fff;
         font-size: .8rem; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.con-oggi .traccia::after { content: ""; position: absolute; top: 0; bottom: 0; left: var(--oggi); width: 0; border-left: 1px dashed var(--inchiostro); opacity: .75; }
.con-oggi .asse::after { content: "Oggi"; position: absolute; top: 0; left: var(--oggi); transform: translateX(-50%); color: var(--inchiostro); font-weight: 700; }
@media (max-width: 40rem) { .linea { --colonna: 0px; } .riga { grid-template-columns: 1fr; } .chi { padding: .6rem 0 0; } .asse span.mese { display: none; } }
.scorri { overflow-x: auto; }
table.periodi { width: 100%; border-collapse: collapse; margin-top: 1rem; }
.periodi th { text-align: left; padding: .5rem .75rem .5rem 0; color: var(--tenue); font-size: .875rem; font-weight: 600; border-bottom: 1px solid var(--inchiostro); }
.periodi td { padding: .65rem .75rem .65rem 0; border-top: 1px dotted var(--filetto); vertical-align: middle; }
.periodi td:first-child { font-size: 1.1rem; white-space: nowrap; }
.periodi .data, .periodi .numeri { color: var(--tenue); white-space: nowrap; }

/* riquadri della situazione di oggi */
.riquadri { display: grid; grid-template-columns: repeat(auto-fit, minmax(11rem, 1fr)); gap: 1rem; margin-top: 1.5rem; }
.riquadro { padding: 1.1rem 1.25rem 1.2rem; border: 1px solid var(--filetto); border-radius: 8px; background: var(--superficie); }
.riquadro .etichetta { display: block; color: var(--tenue); font-size: .875rem; }
.riquadro .valore { display: block; margin-top: .35rem; font-size: 1.5rem; font-weight: 700; line-height: 1.15; }
.riquadro .dopo { display: block; margin-top: .4rem; color: var(--tenue); font-size: .9rem; line-height: 1.45; }
.avanzamento { height: .45rem; margin-top: .8rem; border-radius: 99px; background: var(--piano); overflow: hidden; }
.avanzamento i { display: block; height: 100%; background: var(--corso); }
.sezione h3.attenzione { color: var(--accento-testo); }
ul.allarmi { margin: .6rem 0 0; padding-left: 1.2rem; max-width: 46rem; }
ul.allarmi li { margin: .35rem 0; }

/* diagramma di Gantt: fascia grigia = previsto, barra colorata = effettivo, colore = stato */
.gantt { --colonna: 18rem; margin-top: 1.25rem; }
.asse-g { position: relative; height: 3rem; margin: 0 .75rem 0 var(--colonna); border-bottom: 1px solid var(--inchiostro);
          color: var(--tenue); font-family: var(--mono); font-size: .78rem; }
.asse-g span { position: absolute; bottom: .4rem; transform: translateX(-50%); white-space: nowrap; }
.asse-g .oggi-e { top: 0; bottom: auto; padding: .05rem .5rem; border-radius: 99px; background: var(--inchiostro); color: var(--carta); font-weight: 700; }
/* margine a destra: la milestone sull'ultimo giorno non esce dalla colonna */
.corpo-g { position: relative; margin-right: .75rem; }
.griglia { position: absolute; top: 0; bottom: 0; left: var(--colonna); right: 0; pointer-events: none; }
.griglia span { position: absolute; top: 0; bottom: 0; border-left: 1px solid var(--filetto); }
.griglia .oggi-l { z-index: 2; border-left: 2px solid var(--inchiostro); }
.righe-g { list-style: none; margin: 0; padding: 0; }
.righe-g li { display: grid; grid-template-columns: var(--colonna) minmax(0, 1fr); border-bottom: 1px solid var(--filetto); }
.righe-g .chi { position: relative; z-index: 3; padding: .7rem 1.25rem .7rem 0; background: var(--carta); font-family: var(--sans);
                font-size: 1rem; line-height: 1.35; }
.righe-g .nome { display: block; font-weight: 600; }
.righe-g li.fase .nome { font-size: 1.15rem; }
.righe-g .info { display: block; margin-top: .25rem; color: var(--tenue); font-size: .875rem; }
.righe-g .traccia { position: relative; height: auto; min-height: 3.4rem; }
.piano { position: absolute; top: 50%; height: 1.7rem; transform: translateY(-50%); border: 1px solid var(--piano-bordo); border-radius: 5px; background: var(--piano); }
.reale { position: absolute; top: 50%; z-index: 1; height: .75rem; transform: translateY(-50%); border-radius: 3px; }
.b-conclusa { background: var(--fatto); }
.b-in-corso { background: var(--corso); }
.b-in-ritardo { background: repeating-linear-gradient(135deg, var(--ritardo) 0 5px, transparent 5px 9px); box-shadow: inset 0 0 0 1.5px var(--ritardo); }
.rombo { position: absolute; top: 50%; z-index: 1; width: 1rem; height: 1rem; transform: translate(-50%, -50%) rotate(45deg);
         border: 2px solid var(--inchiostro); background: var(--carta); }
.fase .rombo { width: .8rem; height: .8rem; }
.rombo.m-raggiunta { border-color: var(--fatto); background: var(--fatto); }
.rombo.m-in-ritardo { border-color: var(--ritardo); }
.legenda i.l-piano { width: 1.4rem; border: 1px solid var(--piano-bordo); background: var(--piano); }
.legenda i.l-conclusa { width: 1.4rem; height: .5rem; background: var(--fatto); }
.legenda i.l-in-corso { width: 1.4rem; height: .5rem; background: var(--corso); }
.legenda i.l-in-ritardo { width: 1.4rem; height: .5rem; background: repeating-linear-gradient(135deg, var(--ritardo) 0 4px, transparent 4px 7px); box-shadow: inset 0 0 0 1px var(--ritardo); }
.legenda i.l-rombo { width: .7rem; height: .7rem; margin: 0 .6rem 0 .1rem; border: 2px solid var(--inchiostro); border-radius: 0; transform: rotate(45deg); }
.legenda i.l-oggi { width: 2px; height: 1rem; margin-right: .6rem; border-radius: 0; background: var(--inchiostro); }
details.dettagli { margin-top: 1.25rem; }
details.dettagli summary { cursor: pointer; font-weight: 600; }
p.riassunto { margin: .75rem 0 0; }
@media (max-width: 40rem) {
  .gantt { --colonna: 0px; }
  .righe-g li { grid-template-columns: minmax(0, 1fr); }
  .righe-g .chi { padding-bottom: .2rem; }
  .righe-g .traccia { min-height: 2.6rem; }
}
table.tempi td:first-child { white-space: normal; min-width: 11rem; }
/* il periodo va a capo tra inizio e fine solo se lo spazio manca */
table.tempi .data { white-space: normal; } table.tempi .data span { white-space: nowrap; }
table.tempi td.attivita { font-family: var(--sans); font-size: 1rem; }
table.tempi tbody th { padding: 1.6rem 0 .4rem; text-align: left; font-size: 1.15rem; font-weight: 600;
                       border-bottom: 1px solid var(--filetto); }
table.tempi tfoot td { border-top: 1px solid var(--inchiostro); font-weight: 600; }
.nota-fase { display: block; margin-top: .15rem; color: var(--tenue); font-family: var(--sans); font-size: .875rem; }
.stato { white-space: nowrap; font-size: .95rem; }
.s-in-corso, .s-raggiunta, .s-conclusa, .s-concluso, .s-sotto-controllo { font-weight: 600; }
.s-in-ritardo, .s-fuori-soglia { color: var(--accento-testo); font-weight: 700; }
.s-conclusa .icona, .s-concluso .icona, .s-raggiunta .icona, .s-sotto-controllo .icona { color: var(--fatto); }
.s-in-corso .icona { color: var(--corso); }
.s-da-iniziare, .s-prevista, .s-da-misurare { color: var(--tenue); }

/* cruscotto: esito, indicatori con la loro soglia, grafico delle ore */
p.esito { margin: 1rem 0 0; max-width: 46rem; font-size: 1.3rem; line-height: 1.35; }
.esito .stato { font-size: inherit; }
.riquadro .valore .stato { font-size: 1.15rem; white-space: normal; }
.riquadro .soglia { display: block; margin-top: .5rem; color: var(--tenue); font-size: .85rem; line-height: 1.4; }
.avanzamento i.oltre { background: var(--ritardo); }
td .avanzamento { width: 6rem; margin-top: .35rem; }
.grafico { --colonna: 3rem; margin: 1.5rem 0 0; }
.piano-g { position: relative; height: 15rem; margin: 0 .75rem 0 var(--colonna); border-bottom: 1px solid var(--inchiostro); touch-action: pan-y; }
.piano-g:focus-visible { outline-offset: 6px; }
.piano-g svg { position: absolute; inset: 0; width: 100%; height: 100%; overflow: visible; }
.piano-g polyline { fill: none; stroke-width: 2; stroke-linejoin: round; stroke-linecap: round; }
.piano-g .l-consumate { stroke: var(--corso); }
.piano-g .l-previste { stroke: var(--previsto); stroke-dasharray: 6 5; }
.tacca-y { position: absolute; left: 0; right: 0; border-top: 1px solid var(--filetto); }
.tacca-y b { position: absolute; right: calc(100% + .5rem); top: 0; transform: translateY(-50%); color: var(--tenue);
             font-family: var(--mono); font-size: .78rem; font-weight: 400; white-space: nowrap; }
.rif-g { position: absolute; left: 0; right: 0; border-top: 1px solid var(--tenue); }
.rif-g span { position: absolute; right: 0; bottom: .15rem; color: var(--tenue); font-size: .8rem; }
.oggi-g, .mirino { position: absolute; top: 0; bottom: 0; border-left: 1px solid var(--inchiostro); }
.mirino { border-left-color: var(--tenue); }
.punto-g { position: absolute; width: 10px; height: 10px; border-radius: 50%; transform: translate(-50%, 50%); background: var(--corso);
           box-shadow: 0 0 0 2px var(--carta); }
.fumetto { position: absolute; top: .5rem; z-index: 4; min-width: 9rem; padding: .5rem .7rem; border: 1px solid var(--filetto); border-radius: 8px;
           background: var(--carta); box-shadow: 0 4px 16px rgb(0 0 0 / .12); font-size: .875rem; line-height: 1.45; pointer-events: none; }
.fumetto b { font-variant-numeric: tabular-nums; }
.grafico .asse { height: 2.2rem; margin: 0 .75rem 0 var(--colonna); }
.legenda i.l-consumate, .legenda i.l-previste, .legenda i.l-preventivo { width: 1.4rem; height: 0; border-radius: 0; vertical-align: middle; }
.legenda i.l-consumate { border-top: 2px solid var(--corso); }
.legenda i.l-previste { border-top: 2px dashed var(--previsto); }
.legenda i.l-preventivo { border-top: 1px solid var(--tenue); }

.alfabeto { display: flex; flex-wrap: wrap; gap: .3rem; margin: 0; padding: .5rem 0; list-style: none; }
.alfabeto a { display: inline-grid; place-items: center; min-width: 2.2rem; height: 2.2rem; font-family: var(--mono); font-size: 1rem; text-decoration: none; color: var(--tenue); }
.alfabeto a:hover { color: var(--accento-testo); }
.lettera h2 { font-size: clamp(2.4rem, 5vw, 3.4rem); }
dl { margin: 1rem 0 0; }
dt { font-size: 1.2rem; font-weight: 700; margin-top: 1.25rem; }
dd { margin: .2rem 0 0; max-width: 42rem; }
dd .nota { display: block; margin-top: .25rem; }
.cerca { margin-top: 2.5rem; max-width: 32rem; }
.cerca label { display: block; font-weight: 700; }
.cerca input { width: 100%; margin-top: .45rem; padding: .7rem .9rem; border: 1px solid var(--piano-bordo); border-radius: 8px;
               background: var(--carta); color: var(--inchiostro); font: inherit; }
.cerca .nota { margin-top: .5rem; }

footer { margin-top: 3rem; padding: 1.25rem 0 3rem; border-top: 1px solid var(--inchiostro); display: flex; justify-content: space-between; flex-wrap: wrap;
         gap: .5rem 2rem; color: var(--tenue); font-size: .9rem; }
footer a { color: inherit; }
"""

# Applica subito il tema salvato, prima del rendering, per evitare lo sfarfallio.
SCRIPT_TESTA = """(function(){try{var t=localStorage.getItem('tema');if(t==='light'||t==='dark'){document.documentElement.setAttribute('data-theme',t);}}catch(e){}})();"""

SCRIPT_TEMA = """(function(){
var b=document.querySelector('.tema');if(!b)return;
var mq=window.matchMedia('(prefers-color-scheme: dark)');
function attuale(){return document.documentElement.getAttribute('data-theme')||(mq.matches?'dark':'light');}
function aggiorna(){var scuro=attuale()==='dark';b.setAttribute('aria-pressed',scuro?'true':'false');
b.setAttribute('aria-label',scuro?'Passa al tema chiaro':'Passa al tema scuro');b.title=b.getAttribute('aria-label');
var m=document.querySelector('meta[name="theme-color"]');if(m){m.setAttribute('content',scuro?'#0f0f0f':'#faf9f6');}}
b.addEventListener('click',function(){var nuovo=attuale()==='dark'?'light':'dark';
document.documentElement.setAttribute('data-theme',nuovo);try{localStorage.setItem('tema',nuovo);}catch(e){}aggiorna();});
if(mq.addEventListener){mq.addEventListener('change',aggiorna);}
aggiorna();
var nav=document.querySelector('.indice');
if(nav&&'IntersectionObserver' in window){var voci={};nav.querySelectorAll('a[href^="#"]').forEach(function(a){var s=document.querySelector(a.getAttribute('href'));if(s){voci[s.id]=a;}});
var io=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting){Object.keys(voci).forEach(function(k){voci[k].removeAttribute('aria-current');});voci[x.target.id].setAttribute('aria-current','true');}});},{rootMargin:'-15% 0px -70% 0px'});
Object.keys(voci).forEach(function(k){io.observe(document.getElementById(k));});}
})();"""

# Ruoli in carica alla data di oggi (calcolati nel browser, perché il sito si genera una volta sola)
# e marcatore "Oggi" sulla linea del tempo.
SCRIPT_RUOLI = """(function(){
var el=document.getElementById('dati-ruoli');if(!el)return;
var periodi=JSON.parse(el.textContent).periodi;
var ora=new Date();var oggi=ora.getFullYear()+'-'+String(ora.getMonth()+1).padStart(2,'0')+'-'+String(ora.getDate()).padStart(2,'0');
function slug(s){return s.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').replace(/\\s+/g,'-');}
var attuali={},ultimo=null;
periodi.forEach(function(p){if(p.inizio<=oggi&&oggi<=p.fine){attuali[p.membro]=p.ruolo;}if(!ultimo||p.fine>ultimo.fine){ultimo=p;}});
var vuoto=Object.keys(attuali).length===0;
if(vuoto&&ultimo){periodi.forEach(function(p){if(p.fine===ultimo.fine){attuali[p.membro]=p.ruolo;}});}
document.querySelectorAll('[data-membro]').forEach(function(n){var r=attuali[n.getAttribute('data-membro')];var b=n.querySelector('.ruolo');
if(!b)return;if(r){b.textContent=r;b.className='ruolo r-'+slug(r);b.hidden=false;}else{b.hidden=true;}});
var nota=document.getElementById('nota-attuali');
if(nota){nota.textContent=vuoto&&ultimo?'Nessun periodo copre la data di oggi ('+oggi+'): ruoli dell\\'ultimo periodo registrato, fino al '+ultimo.fine+'.':(vuoto?'Nessun periodo registrato.':'Ruoli in carica oggi, '+oggi+'.');}
var linea=document.querySelector('.linea');
if(linea){var a=new Date(linea.getAttribute('data-inizio')),b=new Date(linea.getAttribute('data-fine'));var x=(ora-a)/(b-a)*100;
if(isFinite(x)){linea.style.setProperty('--oggi',Math.max(0,Math.min(100,x)).toFixed(2)+'%');linea.classList.add('con-oggi');}}
})();"""

# Ricerca nel glossario: filtra termini, definizioni e sinonimi, senza accenti né maiuscole.
SCRIPT_GLOSSARIO = """(function(){
var q=document.getElementById('cerca');if(!q)return;var esito=document.getElementById('esito-ricerca');
function norm(s){return s.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');}
q.addEventListener('input',function(){var t=norm(q.value.trim()),n=0;
document.querySelectorAll('.lettera').forEach(function(s){var v=0;
s.querySelectorAll('dt').forEach(function(dt){var dd=dt.nextElementSibling;var ok=!t||norm(dt.textContent+' '+(dd?dd.textContent:'')).indexOf(t)>=0;
dt.hidden=!ok;if(dd){dd.hidden=!ok;}if(ok){v++;}});s.hidden=v===0;n+=v;});
esito.textContent=t?(n===0?'Nessun termine trovato.':(n===1?'1 termine trovato.':n+' termini trovati.')):'';});
})();"""

# Ricerca nella pagina Documenti: ogni parola cercata deve comparire nella voce o nel titolo della sua sezione.
# Le parole perdono la vocale finale, così "verbale esterno" trova anche "Verbali" ed "Esterni".
# Senza script il campo resta nascosto e si vede tutto l'elenco.
SCRIPT_DOCUMENTI = """(function(){
var q=document.getElementById('cerca');if(!q)return;var esito=document.getElementById('esito-ricerca');q.closest('.cerca').hidden=false;
function norm(s){return s.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');}
var voci=[].map.call(document.querySelectorAll('.sezione .voce'),function(li){var h=li.parentNode.previousElementSibling;
return {li:li,testo:norm(li.closest('.sezione').querySelector('h2').textContent+' '+(h&&h.tagName==='H3'?h.textContent:'')+' '+li.textContent)};});
q.addEventListener('input',function(){var parole=norm(q.value).split(/\\s+/).filter(Boolean).map(function(p){return p.length>3?p.replace(/[aeiou]$/,''):p;}),n=0;
voci.forEach(function(v){var ok=parole.every(function(p){return v.testo.indexOf(p)>=0;});v.li.hidden=!ok;if(ok){n++;}});
document.querySelectorAll('.sezione ol.voci').forEach(function(l){var vuoto=!l.querySelector('.voce:not([hidden])'),h=l.previousElementSibling;
l.hidden=vuoto;if(h&&h.tagName==='H3'){h.hidden=vuoto;}});
document.querySelectorAll('.sezione').forEach(function(s){s.hidden=!s.querySelector('.voce:not([hidden])');});
esito.textContent=parole.length?(n===0?'Nessun documento trovato.':(n===1?'1 documento trovato.':n+' documenti trovati.')):'';});
})();"""

# Grafico delle ore: il mirino segue il puntatore o le frecce e il fumetto riporta i valori del punto più vicino.
# I valori sono anche nella tabella sotto il grafico.
SCRIPT_GRAFICO = """(function(){
document.querySelectorAll('.grafico').forEach(function(g){
var piano=g.querySelector('.piano-g'),punti=JSON.parse(g.getAttribute('data-punti')),mirino=g.querySelector('.mirino'),fumetto=g.querySelector('.fumetto'),i=-1;
function riga(valore,nome){var r=document.createElement('div'),b=document.createElement('b');b.textContent=valore;r.appendChild(b);r.appendChild(document.createTextNode(' '+nome));return r;}
function mostra(n){i=Math.max(0,Math.min(punti.length-1,n));var p=punti[i],destra=p.x>60;mirino.style.left=p.x+'%';mirino.hidden=false;
fumetto.textContent='';var t=document.createElement('div');t.textContent=p.al;fumetto.appendChild(t);
if(p.c!==null){fumetto.appendChild(riga(p.c,'consumate'));}if(p.p!==null){fumetto.appendChild(riga(p.p,'previste'));}
fumetto.style.left=destra?'auto':'calc('+p.x+'% + .75rem)';fumetto.style.right=destra?'calc('+(100-p.x)+'% + .75rem)':'auto';fumetto.hidden=false;}
function nascondi(){mirino.hidden=true;fumetto.hidden=true;}
function vicino(ev){var r=piano.getBoundingClientRect(),x=(ev.clientX-r.left)/r.width*100,m=0;
punti.forEach(function(p,k){if(Math.abs(p.x-x)<Math.abs(punti[m].x-x)){m=k;}});mostra(m);}
piano.addEventListener('pointermove',vicino);piano.addEventListener('pointerdown',vicino);
piano.addEventListener('pointerleave',nascondi);piano.addEventListener('blur',nascondi);
piano.addEventListener('keydown',function(ev){if(ev.key==='ArrowRight'||ev.key==='ArrowLeft'){ev.preventDefault();
mostra(i<0?punti.length-1:i+(ev.key==='ArrowRight'?1:-1));}else if(ev.key==='Escape'){nascondi();}});
});
})();"""

# Pagina di lettura dei PDF: pdf.js da jsDelivr, con versione e impronte SRI fissate.
# shortcut: pdf.js arriva dal CDN; se il sito deve funzionare senza rete, copiarlo in assets/.
PDFJS = "https://cdn.jsdelivr.net/npm/pdfjs-dist@6.4.299/"
SRI_PDFJS = {
    "web/pdf_viewer.css": "sha384-3UXS7i1WpE5V91TL4VCyVEM/qnLn6NYnXegUpsQEooST19Vnke3To/VrUZAEqrtw",
    "build/pdf.min.mjs": "sha384-QCvhu/UPp22U/TNLVbQNONL82ES2yY717GAiqP9VVu37Y7+m9VPKvadGx9XlFvcp",
    "web/pdf_viewer.mjs": "sha384-Vm8r8cVwMps+rKsgyjIcfFWYMNGvu4DblNS+wwwWLdjbsrCMSx4VNoasrlXnIw0w",
    "build/pdf.worker.min.mjs": "sha384-NfW/OTMWezITv4oaALvfH7MFLwzPxEvpySmDpoALa1mtTY8MC200l0ZNFD+SOlrM",
}

# Il lettore riempie lo schermo sotto la testata e scorre nel suo riquadro: il piè di pagina non serve.
# Su mobile il menu lascia spazio al documento; restano il marchio e il link ai documenti.
STILE_PDF = """
.pagina { display: flex; flex-direction: column; height: calc(100dvh - 3px); }
.pagina > main { flex: 1; min-height: 0; display: flex; flex-direction: column; }
.pagina > footer { display: none; }
.comandi-pdf { display: flex; flex-wrap: wrap; align-items: center; gap: .5rem .75rem; padding: .6rem 0; border-bottom: 1px solid var(--filetto); }
.comandi-pdf h1 { flex: 1 1 14rem; min-width: 0; margin: 0; font-size: 1.1rem; line-height: 1.3; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.torna { display: inline-flex; align-items: center; justify-content: center; gap: .35rem; min-width: 2.75rem; min-height: 2.75rem;
         color: var(--tenue); font-weight: 600; text-decoration: none; white-space: nowrap; }
/* su mobile della barra resta la freccia: l'etichetta la legge solo lo screen reader */
@media (max-width: 47.99rem) {
  .testa .menu { display: none; }
  .torna .etichetta { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
  .scarica { padding: 0 .9rem; }
}
.torna:hover { color: var(--accento-testo); }
.numero-pagina { margin: 0 auto 0 0; color: var(--tenue); white-space: nowrap; }
.zoom { display: inline-flex; border: 1px solid var(--filetto); border-radius: 8px; overflow: hidden; }
.zoom button { min-width: 2.75rem; height: 2.75rem; padding: 0 .6rem; border: 0; background: transparent; color: var(--inchiostro);
               font: inherit; font-weight: 600; font-variant-numeric: tabular-nums; cursor: pointer; }
.zoom button + button { border-left: 1px solid var(--filetto); }
.zoom button:hover:not(:disabled) { background: var(--superficie); }
.zoom button:disabled { color: var(--tenue); cursor: default; }
.scarica { display: inline-flex; align-items: center; height: 2.75rem; padding: 0 1rem; border-radius: 8px; background: var(--inchiostro);
           color: var(--carta); font-weight: 600; text-decoration: none; white-space: nowrap; }
.scarica:hover { background: var(--accento-testo); }
.area-pdf { position: relative; flex: 1; min-height: 0; margin: 0 calc(-1 * clamp(1rem, 4vw, 3rem)); background: var(--superficie); }
#contenitore-pdf { position: absolute; inset: 0; overflow: auto; overscroll-behavior: contain; }
#contenitore-pdf:focus-visible { outline-offset: -3px; }
.pdfViewer { padding: clamp(.5rem, 2vw, 1.5rem) 0; }
.pdfViewer.removePageBorders .page { margin: 0 auto clamp(.5rem, 2vw, 1.25rem); box-shadow: 0 1px 2px rgb(0 0 0 / .12), 0 6px 24px rgb(0 0 0 / .1); }
/* fuori dal contenitore, che pdf.js svuota: sopra il riquadro finché il PDF non c'è */
.avviso-pdf { position: absolute; top: 3rem; left: 0; right: 0; max-width: 32rem; margin: 0 auto; padding: 0 1rem; color: var(--tenue); text-align: center; }
"""

# Modulo eseguito dopo pdf.js; la configurazione arriva dagli attributi data- del contenitore.
# "auto" adatta la pagina alla larghezza su mobile, fino al 125% sugli schermi larghi, e si ricalcola a ogni ridimensionamento.
SCRIPT_PDF = """
const contenitore = document.getElementById("contenitore-pdf");
const { pdf, pdfjs, worker } = contenitore.dataset;
const numero = document.getElementById("pagina-pdf"), zoom = document.getElementById("zoom-pdf"), avviso = document.getElementById("avviso-pdf");
try {
  const { pdfjsLib, pdfjsViewer } = globalThis;
  // il worker passa da un blob, così anche il suo codice è controllato dall'impronta SRI
  const codice = await (await fetch(pdfjs + "build/pdf.worker.min.mjs", { integrity: worker })).blob();
  pdfjsLib.GlobalWorkerOptions.workerPort = new Worker(URL.createObjectURL(codice), { type: "module" });
  const bus = new pdfjsViewer.EventBus();
  const collegamenti = new pdfjsViewer.PDFLinkService({ eventBus: bus, externalLinkTarget: pdfjsViewer.LinkTarget.BLANK, externalLinkRel: "noopener" });
  const lettore = new pdfjsViewer.PDFViewer({ container: contenitore, eventBus: bus, linkService: collegamenti, removePageBorders: true });
  collegamenti.setViewer(lettore);
  // pdf.js porta la prima pagina a filo del riquadro: si torna in cima per lasciare il margine sopra
  bus.on("pagesinit", () => { lettore.currentScaleValue = "auto"; contenitore.scrollTop = 0; });
  bus.on("pagechanging", ({ pageNumber }) => { numero.textContent = `${pageNumber} di ${lettore.pagesCount}`; });
  bus.on("scalechanging", ({ scale }) => { zoom.textContent = `${Math.round(scale * 100)}%`; });
  const documento = await pdfjsLib.getDocument({ url: pdf, cMapUrl: pdfjs + "cmaps/", standardFontDataUrl: pdfjs + "standard_fonts/",
                                               wasmUrl: pdfjs + "wasm/", iccUrl: pdfjs + "iccs/" }).promise;
  lettore.setDocument(documento);
  collegamenti.setDocument(documento);
  numero.textContent = `1 di ${documento.numPages}`;
  avviso.hidden = true;
  new ResizeObserver(() => { if (lettore.currentScaleValue === "auto") lettore.currentScaleValue = "auto"; }).observe(contenitore);
  const azioni = { meno: () => lettore.decreaseScale(), adatta: () => { lettore.currentScaleValue = "auto"; }, piu: () => lettore.increaseScale() };
  for (const bottone of document.querySelectorAll("[data-zoom]")) {
    bottone.disabled = false;
    bottone.addEventListener("click", azioni[bottone.dataset.zoom]);
  }
} catch (errore) {
  console.error(errore);
  avviso.firstChild.textContent = "Il PDF non si può mostrare qui: ";
}
"""

ICONE = {
    "sole": '<svg class="sole" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32 1.41 1.41M2 12h2m16 0h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>',
    "luna": '<svg class="luna" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>',
}

NUOVA_SCHEDA = '<span class="sr-only"> (si apre in una nuova scheda)</span>'

# pagine del sito, nell'ordine del menu in alto
PAGINE = (("index.html", "Documenti"), ("cruscotto.html", "Cruscotto"), ("pianificazione.html", "Pianificazione"),
          ("ruoli.html", "Gruppo"), ("glossario.html", "Glossario"))
ICONE_STATO = {"Conclusa": "✓", "Concluso": "✓", "Raggiunta": "◆", "In corso": "●", "In ritardo": "!", "Da iniziare": "○", "Prevista": "◇",
               "Sotto controllo": "✓", "Fuori soglia": "!", "Da misurare": "○"}
UN_GIORNO = datetime.timedelta(days=1)


def e(testo):
    return html.escape(str(testo))


def link(href, testo):
    return f'<a href="{e(href)}" target="_blank" rel="noopener">{e(testo)}{NUOVA_SCHEDA}</a>'


def evidenzia_cifre(nome):
    """Le cifre del nome nel colore d'accento, come il 2 del logo."""
    return re.sub(r"(\d+)", r'<span class="accento">\1</span>', e(nome))


def voce(pdf, testo, meta="", nascosto="", sotto=""):
    """Voce di un elenco di documenti: titolo, riga dei dettagli e link per scaricare il PDF.

    Il titolo porta alla pagina di lettura del PDF, con lo stesso nome e l'estensione .html.
    `meta` (data, versione) è testo in monospazio; `sotto` è già in HTML e lo segue nella stessa
    riga, per esempio lo stato di approvazione di un verbale. `nascosto` completa il nome dei link
    per chi usa uno screen reader quando più voci hanno lo stesso titolo visibile, per esempio " del 2026-10-14".
    """
    extra = f'<span class="sr-only">{e(nascosto)}</span>' if nascosto else ""
    parti = [f'<span class="mono">{e(meta)}</span>' if meta else "", sotto]
    dettaglio = " · ".join(p for p in parti if p)
    return (f'<a class="titolo" href="{e(pdf.removesuffix(".pdf"))}.html">{e(testo)}{extra}</a>'
            + (f'<span class="dettaglio">{dettaglio}</span>' if dettaglio else "")
            + f'<a class="pdf" href="{e(pdf)}" download>PDF<span class="sr-only"> di {e(testo)}{e(nascosto)}</span></a>')


def elenco(voci, vuoto):
    if not voci:
        return f'<p class="vuoto">{e(vuoto)}</p>'
    return '<ol class="voci">' + "".join(f'<li class="voce">{v}</li>' for v in voci) + "</ol>"


def sottogruppi(parti, vuoto):
    """Elenchi con sottotitolo; i sottogruppi vuoti non compaiono e, se lo sono tutti, resta un solo messaggio."""
    pieni = [(titolo, voci) for titolo, voci in parti if voci]
    if not pieni:
        return f'<p class="vuoto">{e(vuoto)}</p>'
    return "".join(f"<h3>{e(titolo)}</h3>" + elenco(voci, "") for titolo, voci in pieni)


def sezione(identificatore, titolo, contenuto, conta=None):
    badge = f'<span class="conta"><span class="sr-only">Elementi: </span>{e(conta)}</span>' if conta else ""
    return (f'<section class="sezione" id="{e(identificatore)}" aria-labelledby="titolo-{e(identificatore)}">'
            f'<h2 id="titolo-{e(identificatore)}">{e(titolo)}{badge}</h2>{contenuto}</section>')


def indice(sezioni):
    """Indice laterale delle sezioni della pagina; le altre pagine sono nel menu in alto."""
    voci = "".join(f'<li><a href="{e(href)}">{e(testo)}</a></li>' for href, testo in sezioni)
    return f'<nav class="indice" aria-label="In questa pagina"><p class="titoletto" aria-hidden="true">In questa pagina</p><ol>{voci}</ol></nav>'


def apertura(titolo_html, kicker, sotto="", meta=(), compatta=False, dopo=""):
    classe = "apertura compatta" if compatta else "apertura"
    testo_sotto = f'<p class="sotto">{e(sotto)}</p>' if sotto else ""
    testo_meta = f'<ul class="meta">{"".join(f"<li>{m}</li>" for m in meta)}</ul>' if meta else ""
    return (f'<section class="{classe}"><p class="kicker">{e(kicker)}</p><h1 class="titolone">{titolo_html}</h1>'
            f'{testo_sotto}{testo_meta}{dopo}</section>')


def pagina(titolo, testata, corpo, gruppo, logo, accento, dati=None, laterale="", corrente=None, script="", in_testa=""):
    """Pagina completa del sito; `in_testa` va nell'head prima dello stile del sito, che così prevale a parità di selettore."""
    info = gruppo.get("gruppo", {})
    nome = info.get("nome") or "Documentazione di progetto"
    icona = f'<link rel="icon" type="image/png" href="{e(logo)}">' if logo else ""
    # testo e titoli si scaricano subito, per non vedere il cambio di carattere
    precarica = "".join(f'<link rel="preload" href="font/{f}.woff2" as="font" type="font/woff2" crossorigin>'
                        for f in ("atkinson-hyperlegible-next", "atkinson-hyperlegible-mono"))
    immagine = f'<img src="{e(logo)}" alt="">' if logo else ""
    repo = f' · {link(info["repo"], "Sorgenti su GitHub")}' if info.get("repo") else ""
    stile = STILE.replace("{accento}", accento).replace("{scuro}", TEMA_SCURO)
    bottone = (f'<button class="tema" type="button" aria-pressed="false" aria-label="Passa al tema scuro">'
               f'{ICONE["sole"]}{ICONE["luna"]}</button>')
    script_dati = ""
    if dati is not None:
        # "</" spezzato: il JSON non può chiudere il proprio script
        testo = json.dumps(dati, ensure_ascii=False).replace("</", "<\\/")
        script_dati = f'<script id="dati-ruoli" type="application/json">{testo}</script>\n<script>{SCRIPT_RUOLI}</script>'
    colonne = f'<div class="colonne">{laterale}<div class="sezioni">{corpo}</div></div>' if laterale else corpo
    voci_menu = []
    for href, testo in PAGINE:
        attuale = ' aria-current="page"' if href == corrente else ""
        voci_menu.append(f'<li><a href="{e(href)}"{attuale}>{e(testo)}</a></li>')
    menu = f'<nav class="menu" aria-label="Pagine del sito"><ul>{"".join(voci_menu)}</ul></nav>'
    script_pagina = f"<script>{script}</script>" if script else ""
    return f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#faf9f6">
<title>{e(titolo)}</title>
{icona}
{precarica}
<script>{SCRIPT_TESTA}</script>
{in_testa}
<style>{stile}</style>
</head>
<body>
<a class="salta" href="#contenuto">Vai al contenuto</a>
<div class="pagina">
<header class="testa"><a class="marchio" href="index.html">{immagine}<span><b>{e(nome)}</b><span class="sep">·</span><span class="sotto-marchio">Documentazione di progetto</span></span></a>{menu}{bottone}</header>
<main id="contenuto" tabindex="-1">
{testata}
{colonne}
</main>
<footer><span>{e(nome)} · Università degli Studi di Padova</span><span>Sito generato dai sorgenti del repository{repo}</span></footer>
</div>
<script>{SCRIPT_TEMA}</script>
{script_dati}
{script_pagina}
</body>
</html>
"""


def compila(typst, sorgente, pdf, dati=None):
    comando = [typst, "compile", "--root", str(RADICE), str(sorgente), str(pdf)]
    if dati:
        comando += ["--input", f"dati={dati}"]
    esito = subprocess.run(comando, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if esito.returncode != 0:
        sys.exit(f"errore nella compilazione di {dati or sorgente.relative_to(RADICE).as_posix()}:\n{esito.stderr}")


def lettere(typst, out):
    voci = []
    for sorgente in sorted((RADICE / "documenti/lettere").glob("*.typ"), reverse=True):
        if data_iso(sorgente.stem):
            nome = f"Lettera di Presentazione {sorgente.stem}"
            compila(typst, sorgente, out / (nome.replace(" ", "_") + ".pdf"))
            voci.append(voce(nome.replace(" ", "_") + ".pdf", "Lettera di Presentazione", sorgente.stem, nascosto=f" del {sorgente.stem}"))
    return voci


def documenti(typst, out, cartella):
    rilasciati = []
    for sorgente in (RADICE / cartella).glob("*.typ"):
        registro = sorgente.with_name(sorgente.stem + ".registro.csv")
        stato = rilascio(registro) if registro.exists() else None
        if not stato:
            continue
        versione, data = stato
        titolo = re.search(r'titolo:\s*"([^"]+)"', sorgente.read_text(encoding="utf-8-sig"))
        titolo = titolo[1] if titolo else sorgente.stem
        pdf = f"{titolo.replace(' ', '_')}_v{versione}.pdf"
        compila(typst, sorgente, out / pdf)
        rilasciati.append((data, titolo, voce(pdf, titolo, f"v{versione}", sotto=f"aggiornato\u00a0il\u00a0{e(data)}")))
    # le ultime approvazioni in cima
    rilasciati.sort(key=lambda d: d[1])
    rilasciati.sort(key=lambda d: d[0], reverse=True)
    return [testo for _, _, testo in rilasciati]


def verbali(typst, out, cartella):
    tipo = {"interni": "interno", "esterni": "esterno"}[cartella]
    voci = []
    for sorgente in sorted((RADICE / "documenti/verbali" / cartella).glob("*.toml"), reverse=True):
        if parti := nome_verbale(sorgente.stem):
            nome = f"Verbale {tipo} {sorgente.stem}"
            pdf = out / (nome.replace(" ", "_") + ".pdf")
            # la copia firmata dal proponente è quella ufficiale: va sul sito così com'è
            if (firmato := sorgente.with_name(sorgente.stem + ".firmato.pdf")).is_file():
                shutil.copyfile(firmato, pdf)
            else:
                compila(typst, RADICE / "modello/verbale.typ", pdf, dati=f"/documenti/verbali/{cartella}/{sorgente.name}")
            # due verbali dello stesso giorno si distinguono per il suffisso: "2026-10-20 C7"
            quando = f"{parti[0]} {parti[1].upper()}".strip()
            dati = tomllib.loads(sorgente.read_text(encoding="utf-8-sig"))
            meta = f"{quando} · v{dati['versione']}" if dati.get("versione") else quando
            # spazi non separabili: su mobile "aggiornato il" non va a capo lontano dalla data
            sotto = stato_verbale(dati) + (f" · aggiornato\u00a0il\u00a0{e(dati['aggiornato'])}" if dati.get("aggiornato") else "")
            voci.append(voce(nome.replace(" ", "_") + ".pdf", titolo_verbale(dati), meta, nascosto=f", verbale del {quando}",
                             sotto=sotto))
    return voci


def diari(typst, out):
    """Diari di bordo, dal più recente: data e versione nel nome del PDF, ultimo aggiornamento sotto."""
    voci = []
    for sorgente in sorted((RADICE / "presentazioni/diari").glob("*.typ"), reverse=True):
        if not data_iso(sorgente.stem):
            continue
        testo = sorgente.read_text(encoding="utf-8-sig")
        # il primo valore di ogni campo è quello di presentazione.with(...), che precede le slide
        titolo, versione, aggiornato = (m[1] if (m := re.search(rf'\b{campo}:\s*"([^"]*)"', testo)) else ""
                                        for campo in ("titolo", "versione", "aggiornato"))
        nome = f"Diario di bordo {sorgente.stem}" + (f" v{versione}" if versione else "")
        pdf = nome.replace(" ", "_") + ".pdf"
        compila(typst, sorgente, out / pdf)
        meta = f"{sorgente.stem} · v{versione}" if versione else sorgente.stem
        sotto = f"aggiornato\u00a0il\u00a0{e(aggiornato)}" if aggiornato else ""
        voci.append(voce(pdf, titolo or "Diario di bordo", meta, nascosto=f", diario di bordo del {sorgente.stem}", sotto=sotto))
    return voci


def titolo_verbale(v):
    """Il campo titolo; senza, l'azienda incontrata (esterni) o il primo punto dell'ordine del giorno."""
    if v.get("titolo"):
        return v["titolo"]
    aziende = list(dict.fromkeys(x["azienda"] for x in v.get("esterni", []) if x.get("azienda")))
    if v.get("tipo") == "esterno" and aziende:
        return "Incontro con " + " e ".join(aziende)
    punti = v.get("ordine_del_giorno", [])
    if len(punti) > 2:
        return f"{punti[0]} e altri {len(punti) - 1} punti"
    return " e ".join(punti) or f"Verbale {v.get('tipo', '')}".strip()


def stato_verbale(v):
    """Approvazione del proponente per gli esterni; gli interni sono verificati da un membro diverso dal redattore."""
    if v.get("tipo") == "esterno":
        approvazione = v.get("approvazione_esterna", "").strip()
        if not approvazione:
            return ('<span class="approvazione a-attesa"><span class="icona" aria-hidden="true">○</span> '
                    'In attesa di approvazione del proponente</span>')
        testo = approvazione if approvazione.lower().startswith("approvat") else f"Approvato: {approvazione}"
        return f'<span class="approvazione a-approvato"><span class="icona" aria-hidden="true">✓</span> {e(testo)}</span>'
    return (f'<span class="approvazione a-approvato"><span class="icona" aria-hidden="true">✓</span> '
            f'Verificato da {e(v.get("verificatore", ""))}</span>')


def nome_membro(membro):
    return f"{membro.get('nome', '')} {membro.get('cognome', '')}".strip()


def persona(membro, con_ruolo=False):
    nome = nome_membro(membro)
    utente = membro.get("github")
    # il ruolo lo compila lo script dai periodi di dati/ruoli.csv
    attributo = f' data-membro="{e(nome)}"' if con_ruolo else ""
    ruolo = '<span class="ruolo" hidden></span>' if con_ruolo else ""
    if utente:
        avatar = f'<img src="https://github.com/{e(utente)}.png?size=72" alt="" loading="lazy">'
        profilo = f'<a class="utente" href="https://github.com/{e(utente)}" target="_blank" rel="noopener">@{e(utente)}{NUOVA_SCHEDA}</a>'
    else:
        iniziali = "".join(parte[0] for parte in nome.split()[:2]).upper()
        avatar = f'<span class="iniziali" aria-hidden="true">{e(iniziali)}</span>'
        profilo = ""
    return f'<li class="persona"{attributo}>{avatar}<span class="nome">{e(nome)}</span>{ruolo}{profilo}</li>'


def leggi_ruoli():
    """Periodi di dati/ruoli.csv già validati da verifica.py; le righe malformate si saltano."""
    percorso = RADICE / "dati/ruoli.csv"
    if not percorso.exists():
        return []
    periodi = []
    with percorso.open(encoding="utf-8-sig", newline="") as f:
        for riga in csv.DictReader(f):
            try:
                inizio = datetime.date.fromisoformat(riga["inizio"].strip())
                fine = datetime.date.fromisoformat(riga["fine"].strip())
            except (KeyError, ValueError, AttributeError):
                continue
            periodi.append({"inizio": inizio.isoformat(), "fine": fine.isoformat(),
                            "membro": riga["membro"].strip(), "ruolo": riga["ruolo"].strip()})
    periodi.sort(key=lambda p: (p["inizio"], p["membro"]))
    return periodi


def pct(x):
    return f"{x:g}"


def scala(inizio, fine):
    """Posizione percentuale di un giorno tra inizio e fine (esclusa) e asse con le tacche dei mesi."""
    totale = max((fine - inizio).days, 1)

    def pos(d):
        # percentuale con al più due decimali, senza ".0" finale
        return float(f"{(d - inizio).days / totale * 100:.2f}")

    tacche = [f'<span class="inizio" style="left:0%">{inizio.isoformat()}</span>']
    mese = inizio.replace(day=1)
    while True:
        mese = (mese.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
        if mese >= fine:
            break
        # niente mesi troppo vicini alle date di inizio e fine: le etichette si sovrapporrebbero
        if 18 < pos(mese) < 82:
            tacche.append(f'<span class="mese" style="left:{pct(pos(mese))}%">{MESI[mese.month - 1]} {mese.year}</span>')
    tacche.append(f'<span class="fine" style="left:100%">{(fine - UN_GIORNO).isoformat()}</span>')
    return pos, f'<div class="asse">{"".join(tacche)}</div>'


def linea_del_tempo(periodi, nomi):
    """Barre per membro su una scala comune; l'ultimo giorno di ogni periodo è incluso."""
    giorno = datetime.date.fromisoformat
    inizio = min(giorno(p["inizio"]) for p in periodi)
    fine = max(giorno(p["fine"]) for p in periodi) + UN_GIORNO
    pos, asse = scala(inizio, fine)

    righe = []
    for nome in nomi:
        barre = []
        for p in periodi:
            if p["membro"] != nome:
                continue
            a, b = pos(giorno(p["inizio"])), pos(giorno(p["fine"]) + UN_GIORNO)
            barre.append(f'<span class="barra r-{e(slug(p["ruolo"]))}" style="left:{pct(a)}%;width:{pct(round(b - a, 2))}%" '
                         f'title="{e(p["ruolo"])} dal {p["inizio"]} al {p["fine"]}">{e(p["ruolo"])}</span>')
        righe.append(f'<div class="riga"><div class="chi">{e(nome)}</div><div class="traccia">{"".join(barre)}</div></div>')
    return (f'<div class="linea" aria-hidden="true" data-inizio="{inizio.isoformat()}" data-fine="{fine.isoformat()}">'
            f'{asse}{"".join(righe)}</div>')


def tabella_periodi(periodi):
    righe = "".join(f'<tr><td>{e(p["membro"])}</td><td><span class="ruolo r-{e(slug(p["ruolo"]))}">{e(p["ruolo"])}</span></td>'
                    f'<td class="data">{e(p["inizio"])}</td><td class="data">{e(p["fine"])}</td></tr>' for p in periodi)
    # la regione scorrevole deve essere raggiungibile da tastiera
    return ('<div class="scorri" role="region" aria-label="Tabella dei periodi" tabindex="0">'
            '<table class="periodi"><thead><tr><th scope="col">Membro</th><th scope="col">Ruolo</th>'
            f'<th scope="col">Dal</th><th scope="col">Al</th></tr></thead><tbody>{righe}</tbody></table></div>')


def pagina_indice(gruppo, typst, out, logo, accento, fasi=(), oggi=None):
    info, progetto = gruppo.get("gruppo", {}), gruppo.get("progetto", {})
    nome = info.get("nome") or "Documentazione di progetto"
    oggi = oggi or datetime.date.today()

    meta = []
    if progetto.get("capitolato"):
        testo = f"Capitolato {progetto['capitolato']}"
        if progetto.get("proponente"):
            testo += f" · {progetto['proponente']}"
        meta.append(e(testo))
    if info.get("email"):
        meta.append(f'<a href="mailto:{e(info["email"])}">{e(info["email"])}</a>')
    if info.get("repo"):
        meta.append(link(info["repo"], "Repository"))
    meta.append(f"Aggiornato il {oggi.isoformat()}")
    testata = apertura(evidenzia_cifre(nome), "Documentazione di progetto", SOTTOTITOLO, meta, compatta=True,
                       dopo=stato_progetto(fasi, oggi))

    voci_lettere = lettere(typst, out)
    gestionali = documenti(typst, out, "documenti/esterni/gestionali")
    tecnici = documenti(typst, out, "documenti/esterni/tecnici")
    interni = documenti(typst, out, "documenti/interni")
    verbali_esterni = verbali(typst, out, "esterni")
    verbali_interni = verbali(typst, out, "interni")
    voci_diari = diari(typst, out)
    return pagina_documenti(gruppo, logo, accento, testata, voci_lettere, (gestionali, tecnici, interni),
                            (verbali_esterni, verbali_interni), voci_diari)


def pagina_documenti(gruppo, logo, accento, testata, voci_lettere, voci_documenti, voci_verbali, voci_diari):
    """Pagina Documenti: la lettera più recente in cima, poi documenti, verbali e diari, dal più recente.

    Compaiono solo le sezioni con almeno una voce; una riga elenca quelle ancora vuote.
    """
    nome = gruppo.get("gruppo", {}).get("nome") or "Documentazione di progetto"
    gestionali, tecnici, interni = voci_documenti
    verbali_esterni, verbali_interni = voci_verbali
    # (id, titolo, voce dell'indice, introduzione, contenuto, numero di voci)
    parti = [
        ("lettere", "Lettere di presentazione", "Lettere", "Una per consegna, con i link ai prodotti consegnati.",
         elenco(voci_lettere, ""), len(voci_lettere)),
        ("documenti", "Documenti", "Documenti",
         "Documenti esterni, gestionali e tecnici, e documenti interni, nell'ultima versione approvata dal Responsabile.",
         sottogruppi([("Gestionali", gestionali), ("Tecnici", tecnici), ("Interni", interni)], ""),
         len(gestionali) + len(tecnici) + len(interni)),
        ("verbali", "Verbali", "Verbali", "Dal più recente. I verbali esterni riportano l'approvazione del proponente.",
         sottogruppi([("Esterni", verbali_esterni), ("Interni", verbali_interni)], ""), len(verbali_esterni) + len(verbali_interni)),
        ("diari", "Diari di bordo", "Diari di bordo", "La presentazione settimanale ai docenti, dalla più recente.",
         elenco(voci_diari, ""), len(voci_diari)),
    ]
    piene = [p for p in parti if p[5]]
    vuote = [p[1].lower() for p in parti if not p[5]]
    corpo = []
    if piene:
        corpo.append('<div class="cerca" hidden><label for="cerca">Cerca tra i documenti</label>'
                     '<input id="cerca" type="search" autocomplete="off" spellcheck="false" placeholder="Titolo, data o tipo">'
                     '<p class="nota" id="esito-ricerca" aria-live="polite"></p></div>')
    if vuote:
        elenco_vuote = vuote[0] if len(vuote) == 1 else ", ".join(vuote[:-1]) + " e " + vuote[-1]
        corpo.append(f'<p class="nota">Ancora da pubblicare: {e(elenco_vuote)}.</p>')
    for identificatore, titolo, _, intro, contenuto, conta in piene:
        blocco = sezione(identificatore, titolo, f'<p class="intro">{e(intro)}</p>{contenuto}', conta)
        corpo.append(blocco.replace('class="sezione"', 'class="sezione in-evidenza"', 1) if identificatore == "lettere" else blocco)
    laterale = indice([(f"#{p[0]}", p[2]) for p in piene]) if piene else ""
    return pagina(nome, testata, "\n".join(corpo), gruppo, logo, accento, laterale=laterale, corrente="index.html",
                  script=SCRIPT_DOCUMENTI)


def pagina_ruoli(gruppo, logo, accento, periodi):
    info = gruppo.get("gruppo", {})
    nome = info.get("nome") or "Documentazione di progetto"
    membri = gruppo.get("membro", [])
    nomi = [nome_membro(m) for m in membri]
    nomi += sorted({p["membro"] for p in periodi} - set(nomi))
    meta = [f'<a href="mailto:{e(info["email"])}">{e(info["email"])}</a>'] if info.get("email") else []
    if info.get("repo"):
        meta.append(link(info["repo"].rstrip("/") + "/blob/main/documenti/interni/ruoli.md", "Regole di rotazione"))
    testata = apertura(e("Gruppo"), nome, "Chi siamo e chi ricopre quale ruolo, oggi e nel tempo.", meta, compatta=True)

    attuali = [persona(m, con_ruolo=True) for m in membri]
    presenti = [r for r in RUOLI if any(p["ruolo"] == r for p in periodi)]
    legenda = '<ul class="legenda">' + "".join(f'<li><i class="r-{e(slug(r))}" aria-hidden="true"></i>{e(r)}</li>' for r in presenti) + "</ul>"
    corpo = [sezione("attuali", "Membri e ruoli attuali",
                     '<p class="nota" id="nota-attuali">Ruoli in carica alla data di oggi.</p>'
                     + (f'<ul class="persone">{"".join(attuali)}</ul>' if attuali else '<p class="vuoto">Membri non ancora indicati</p>'),
                     len(attuali))]
    voci_indice = [("#attuali", "Membri e ruoli")]
    if periodi:
        corpo += [sezione("linea", "Linea del tempo", legenda + linea_del_tempo(periodi, nomi)),
                  sezione("periodi", "Periodi", tabella_periodi(periodi)
                          + '<p class="nota">I periodi futuri compaiono quando il gruppo li conferma in dati/ruoli.csv.</p>', len(periodi))]
        voci_indice += [("#linea", "Linea del tempo"), ("#periodi", "Periodi")]
    else:
        corpo.append(sezione("periodi", "Periodi", '<p class="vuoto">Nessun periodo ancora registrato in dati/ruoli.csv</p>'))
        voci_indice.append(("#periodi", "Periodi"))
    return pagina(f"Gruppo - {nome}", testata, "\n".join(corpo), gruppo, logo, accento, dati={"periodi": periodi},
                  laterale=indice(voci_indice), corrente="ruoli.html")


def leggi_pianificazione():
    """Fasi di dati/pianificazione.toml, già validate da verifica.py."""
    percorso = RADICE / "dati/pianificazione.toml"
    if not percorso.exists():
        return []
    return tomllib.loads(percorso.read_text(encoding="utf-8-sig")).get("fase", [])


def leggi_ore():
    """(giorno, ore, membro, ruolo) delle righe di dati/ore.csv; le righe malformate si saltano."""
    percorso = RADICE / "dati/ore.csv"
    if not percorso.exists():
        return []
    ore = []
    with percorso.open(encoding="utf-8-sig", newline="") as f:
        for riga in csv.DictReader(f):
            try:
                ore.append((datetime.date.fromisoformat(riga["data"].strip()), float(riga["ore"]),
                            riga["membro"].strip(), riga["ruolo"].strip()))
            except (KeyError, ValueError, AttributeError, TypeError):
                continue
    return ore


def leggi_preventivo():
    """Tariffe e ripartizione di dati/preventivo.toml, già validate da verifica.py."""
    percorso = RADICE / "dati/preventivo.toml"
    if not percorso.exists():
        return {}
    return tomllib.loads(percorso.read_text(encoding="utf-8-sig"))


def tempo(voce, oggi):
    """Giorni previsti e usati, stato e scostamento di una fase o di un'attività.

    Senza fine_effettiva il periodo effettivo arriva a oggi; il primo e l'ultimo giorno sono inclusi.
    """
    inizio, fine = voce.get("inizio_effettivo"), voce.get("fine_effettiva")
    t = {"previsti": (voce["fine"] - voce["inizio"]).days + 1, "usati": 0, "fine": fine or (oggi if inizio else None), "dettaglio": ""}
    if inizio:
        t["usati"] = (t["fine"] - inizio).days + 1
    oltre = (oggi - voce["fine"]).days
    if fine:
        t["stato"], t["dettaglio"] = "Conclusa", differenza(fine, voce["fine"])
    elif inizio:
        t["stato"] = "In ritardo" if oltre > 0 else "In corso"
        if oltre > 0:
            t["dettaglio"] = f"{giorni(oltre)} oltre la fine prevista"
    elif oggi > voce["inizio"]:
        t["stato"] = "In ritardo"
        t["dettaglio"] = f"non iniziata, {giorni(oltre)} oltre la fine prevista" if oltre > 0 else f"non iniziata, prevista dal {voce['inizio']}"
    else:
        t["stato"] = "Da iniziare"
    return t


def tempo_milestone(milestone, oggi):
    """(stato, scostamento) di una milestone."""
    if milestone.get("data_effettiva"):
        return "Raggiunta", differenza(milestone["data_effettiva"], milestone["data"])
    if oggi > milestone["data"]:
        return "In ritardo", f"{giorni((oggi - milestone['data']).days)} oltre la data prevista"
    return "Prevista", ""


def differenza(effettiva, prevista):
    scarto = (effettiva - prevista).days
    if scarto == 0:
        return "nei tempi"
    return f"{giorni(abs(scarto))} di {'ritardo' if scarto > 0 else 'anticipo'}"


def voci_fase(fase, attivita=True):
    """(è_milestone, voce) di attività e milestone in ordine di data; a pari data prima la milestone."""
    voci = [(False, a) for a in fase.get("attivita", []) if attivita] + [(True, m) for m in fase.get("milestone", [])]
    return sorted(voci, key=lambda v: (v[1]["data"] if v[0] else v[1]["inizio"], not v[0]))


def ore_fase(fase, ore):
    """Ore di dati/ore.csv nel periodo effettivo della fase; una fase non iniziata non ne ha."""
    inizio = fase.get("inizio_effettivo")
    fine = fase.get("fine_effettiva") or datetime.date.max
    return sum(h for giorno, h, *_ in ore if inizio and inizio <= giorno <= fine)


def giorni(n):
    return f"{n} giorno" if n == 1 else f"{n} giorni"


def numero_it(x):
    return "—" if x is None else f"{x:g}".replace(".", ",")


def stato_html(stato, dettaglio=""):
    sotto = f'<span class="nota-fase">{e(dettaglio)}</span>' if dettaglio else ""
    return (f'<span class="stato s-{slug(stato)}"><span class="icona" aria-hidden="true">{ICONE_STATO[stato]}</span> {e(stato)}</span>'
            f'{sotto}')


def intervallo(inizio, fine):
    """Periodo su due righe se lo spazio manca; senza fine è in corso."""
    if not inizio:
        return "—"
    return f'<span>{inizio.isoformat()}</span> <span>→ {fine.isoformat() if fine else "in corso"}</span>'


def info_voce(voce, milestone, oggi):
    """Riga sotto il nome nel Gantt: stato, giorni o data, scostamento."""
    if milestone:
        stato, dettaglio = tempo_milestone(voce, oggi)
        quando = voce.get("data_effettiva") or voce["data"]
        mancano = (voce["data"] - oggi).days
        parti = [quando.isoformat()]
        if stato == "Prevista":
            parti.append("oggi" if mancano == 0 else f"fra {giorni(mancano)}")
    else:
        t = tempo(voce, oggi)
        stato, dettaglio = t["stato"], t["dettaglio"]
        parti = [f'{t["usati"]} di {giorni(t["previsti"])}' if voce.get("inizio_effettivo") else f'{giorni(t["previsti"])} previsti']
    if dettaglio:
        parti.append(dettaglio)
    return f'{stato_html(stato)} · {e(" · ".join(parti))}'


def gantt(fasi, oggi, attivita=True):
    """Gantt di attività e milestone di una fase, oppure panoramica delle fasi (attivita=False).

    Ogni riga ha nome, stato e giorni in chiaro; la traccia è decorativa: fascia grigia del previsto,
    barra colorata dell'effettivo, che per le voci in corso arriva a oggi.
    """
    date = []
    for fase in fasi:
        for milestone, voce in [(False, fase), *voci_fase(fase, attivita)]:
            if milestone:
                date += [voce["data"], voce.get("data_effettiva")]
            else:
                date += [voce["inizio"], voce["fine"], voce.get("inizio_effettivo"), tempo(voce, oggi)["fine"]]
    date = [d for d in date if d]
    inizio, fine = min(date), max(date) + UN_GIORNO
    pos, _ = scala(inizio, fine)

    def centro(d):
        return round((pos(d) + pos(d + UN_GIORNO)) / 2, 2)

    def barra(classe, a, b, titolo):
        x, y = pos(a), pos(b + UN_GIORNO)
        return f'<span class="{classe}" style="left:{pct(x)}%;width:{pct(round(y - x, 2))}%" title="{e(titolo)}"></span>'

    def rombo(milestone):
        stato, _ = tempo_milestone(milestone, oggi)
        quando = milestone.get("data_effettiva") or milestone["data"]
        return f'<span class="rombo m-{slug(stato)}" style="left:{pct(centro(quando))}%" title="{e(milestone["nome"])}: {quando}"></span>'

    def riga(voce, milestone=False, classe=""):
        if milestone:
            traccia = rombo(voce)
        else:
            t = tempo(voce, oggi)
            traccia = barra("piano", voce["inizio"], voce["fine"], f"Previsto dal {voce['inizio']} al {voce['fine']}")
            if voce.get("inizio_effettivo"):
                al = f"al {t['fine']}" if voce.get("fine_effettiva") else "a oggi"
                traccia += barra(f"reale b-{slug(t['stato'])}", voce["inizio_effettivo"], t["fine"],
                                 f"Effettivo dal {voce['inizio_effettivo']} {al}")
            if classe:
                traccia += "".join(rombo(m) for m in voce.get("milestone", []))
        return (f'<li{classe}><div class="chi"><span class="nome">{e(voce["nome"])}</span>'
                f'<span class="info">{info_voce(voce, milestone, oggi)}</span></div>'
                f'<div class="traccia" aria-hidden="true">{traccia}</div></li>')

    if attivita:
        righe = [riga(voce, milestone) for fase in fasi for milestone, voce in voci_fase(fase)]
    else:
        righe = [riga(fase, classe=' class="fase"') for fase in fasi]

    # sotto i 100 giorni una tacca ogni lunedì, altrimenti una al primo di ogni mese
    settimanale = (fine - inizio).days <= 100
    d = inizio + datetime.timedelta(days=-inizio.weekday() % 7) if settimanale else inizio.replace(day=1)
    tacche, linee = [], []
    while d < fine:
        if d >= inizio:
            x = pos(d)
            linee.append(f'<span style="left:{pct(x)}%"></span>')
            # niente etichette sui bordi: uscirebbero dalla traccia
            if 4 <= x <= 92:
                testo = f"{d.day} {MESI[d.month - 1]}" if settimanale else f"{MESI[d.month - 1]} {d.year}"
                tacche.append(f'<span style="left:{pct(x)}%">{testo}</span>')
        d = d + datetime.timedelta(days=7) if settimanale else (d.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
    if inizio <= oggi < fine:
        tacche.append(f'<span class="oggi-e" style="left:{pct(centro(oggi))}%">Oggi</span>')
        linee.append(f'<span class="oggi-l" style="left:{pct(centro(oggi))}%"></span>')
    return (f'<div class="gantt"><div class="asse-g" aria-hidden="true">{"".join(tacche)}</div>'
            f'<div class="corpo-g"><div class="griglia" aria-hidden="true">{"".join(linee)}</div>'
            f'<ol class="righe-g">{"".join(righe)}</ol></div></div>')


LEGENDA_GANTT = ('<ul class="legenda" aria-hidden="true"><li><i class="l-piano"></i>Previsto</li><li><i class="l-conclusa"></i>Conclusa</li>'
                 '<li><i class="l-in-corso"></i>In corso</li><li><i class="l-in-ritardo"></i>In ritardo</li>'
                 '<li><i class="l-rombo"></i>Milestone</li><li><i class="l-oggi"></i>Oggi</li></ul>')


def ore_previste(fasi):
    """Somma delle ore previste, None finché una fase non le indica."""
    if any("ore_previste" not in f for f in fasi):
        return None
    return sum(f["ore_previste"] for f in fasi)


def tabella_fasi(fasi, ore, oggi):
    """Tempo previsto e usato per fase, in giorni e in ore, con il totale del progetto."""
    righe = []
    for fase in fasi:
        t = tempo(fase, oggi)
        nota = f'<span class="nota-fase">{e(fase["nota"])}</span>' if fase.get("nota") else ""
        righe.append(f'<tr><td>{e(fase["nome"])}{nota}</td><td class="data">{intervallo(fase["inizio"], fase["fine"])}</td>'
                     f'<td class="data">{intervallo(fase.get("inizio_effettivo"), fase.get("fine_effettiva"))}</td>'
                     f'<td class="numeri">{t["usati"]} di {t["previsti"]}</td>'
                     f'<td class="numeri">{numero_it(ore_fase(fase, ore))} di {numero_it(fase.get("ore_previste"))}</td>'
                     f'<td>{stato_html(t["stato"], t["dettaglio"])}</td></tr>')
    primo, ultimo = fasi[0], fasi[-1]
    previsti = (ultimo["fine"] - primo["inizio"]).days + 1
    inizio, fine = primo.get("inizio_effettivo"), ultimo.get("fine_effettiva")
    usati = ((fine or oggi) - inizio).days + 1 if inizio else 0
    totale = (f'<tfoot><tr><td>Totale</td><td class="data">{intervallo(primo["inizio"], ultimo["fine"])}</td>'
              f'<td class="data">{intervallo(inizio, fine)}</td><td class="numeri">{usati} di {previsti}</td>'
              f'<td class="numeri">{numero_it(sum(h for _, h, *_ in ore))} di {numero_it(ore_previste(fasi))}</td>'
              '<td></td></tr></tfoot>')
    return ('<div class="scorri" role="region" aria-label="Tempo per fase" tabindex="0"><table class="periodi tempi">'
            '<thead><tr><th scope="col">Fase</th><th scope="col">Previsto</th><th scope="col">Effettivo</th>'
            '<th scope="col">Giorni usati</th><th scope="col">Ore usate</th><th scope="col">Stato</th></tr></thead>'
            f'<tbody>{"".join(righe)}</tbody>{totale}</table></div>')


def tabella_attivita(fase, oggi):
    """Date previste ed effettive di attività e milestone di una fase."""
    righe = []
    for milestone, voce in voci_fase(fase):
        if milestone:
            stato, dettaglio = tempo_milestone(voce, oggi)
            nome = f'{e(voce["nome"])}<span class="nota-fase">Milestone</span>'
            previsto, durata = voce["data"].isoformat(), "—"
            effettivo = voce["data_effettiva"].isoformat() if voce.get("data_effettiva") else "—"
        else:
            t = tempo(voce, oggi)
            stato, dettaglio, nome = t["stato"], t["dettaglio"], e(voce["nome"])
            previsto = intervallo(voce["inizio"], voce["fine"])
            effettivo = intervallo(voce.get("inizio_effettivo"), voce.get("fine_effettiva"))
            durata = f'{t["usati"]} di {t["previsti"]}'
        righe.append(f'<tr><td class="attivita">{nome}</td><td class="data">{previsto}</td><td class="data">{effettivo}</td>'
                     f'<td class="numeri">{durata}</td><td>{stato_html(stato, dettaglio)}</td></tr>')
    return (f'<div class="scorri" role="region" aria-label="Date di {e(fase["nome"])}" tabindex="0"><table class="periodi tempi">'
            '<thead><tr><th scope="col">Attività</th><th scope="col">Previsto</th><th scope="col">Effettivo</th>'
            f'<th scope="col">Giorni usati</th><th scope="col">Stato</th></tr></thead><tbody>{"".join(righe)}</tbody></table></div>')


def riquadro(etichetta, valore, dopo="", avanzamento=None):
    barra = (f'<div class="avanzamento" aria-hidden="true"><i style="width:{pct(avanzamento)}%"></i></div>'
             if avanzamento is not None else "")
    dopo = f'<span class="dopo">{dopo}</span>' if dopo else ""
    return f'<div class="riquadro"><span class="etichetta">{e(etichetta)}</span><span class="valore">{valore}</span>{dopo}{barra}</div>'


def fase_corrente(fasi):
    return next((f for f in fasi if f.get("inizio_effettivo") and not f.get("fine_effettiva")), None)


def prossima_milestone(fasi):
    """(data, nome) della prima milestone non ancora raggiunta, oppure None."""
    return min(((m["data"], m["nome"]) for f in fasi for m in f.get("milestone", []) if not m.get("data_effettiva")), default=None)


def quanto_manca(data, oggi):
    mancano = (data - oggi).days
    if mancano == 0:
        return "oggi"
    return f"fra {giorni(mancano)}" if mancano > 0 else f"{giorni(-mancano)} di ritardo"


def stato_progetto(fasi, oggi):
    """Riga della home: fase in corso e prossima milestone, con il link al cruscotto."""
    if not fasi:
        return ""
    corrente, prossima = fase_corrente(fasi), prossima_milestone(fasi)
    parti = [f"<span>Fase in corso: <b>{e(corrente['nome'])}</b></span>" if corrente else "<span>Nessuna fase in corso</span>"]
    if prossima:
        parti.append(f"<span>Prossima milestone: <b>{e(prossima[1])}</b>, {prossima[0]} ({quanto_manca(prossima[0], oggi)})</span>")
    return f'<p class="stato-progetto">{"".join(parti)}<a href="cruscotto.html">Cruscotto</a></p>'


def ritardi(fasi, oggi):
    """(voce, fase, scostamento) delle attività e delle milestone in ritardo, fase per fase."""
    trovati = []
    for fase in fasi:
        for milestone, voce in voci_fase(fase):
            if milestone:
                stato, dettaglio = tempo_milestone(voce, oggi)
            else:
                t = tempo(voce, oggi)
                stato, dettaglio = t["stato"], t["dettaglio"]
            if stato == "In ritardo":
                trovati.append((voce["nome"], fase["nome"], dettaglio))
    return trovati


def situazione(fasi, ore, oggi):
    """Riquadri con fase in corso, prossima milestone, attività e ore, poi le voci in ritardo."""
    corrente = fase_corrente(fasi)
    if corrente:
        t = tempo(corrente, oggi)
        giorno = min(t["usati"], t["previsti"])
        riquadri = [riquadro("Fase in corso", e(corrente["nome"]),
                             f'Giorno {t["usati"]} di {t["previsti"]}, fine prevista il {corrente["fine"]}',
                             round(giorno / t["previsti"] * 100, 2))]
    else:
        prossima_fase = next((f for f in fasi if not f.get("inizio_effettivo")), None)
        riquadri = [riquadro("Fase in corso", "Nessuna",
                             f'Prossima: {e(prossima_fase["nome"])}, dal {prossima_fase["inizio"]}' if prossima_fase else "")]

    prossima = prossima_milestone(fasi)
    if prossima:
        riquadri.append(riquadro("Prossima milestone", quanto_manca(prossima[0], oggi).capitalize(), f"{e(prossima[1])}, {prossima[0]}"))

    if corrente and corrente.get("attivita"):
        stati = [tempo(a, oggi)["stato"] for a in corrente["attivita"]]
        conta = {s: stati.count(s) for s in ("Conclusa", "In corso", "In ritardo", "Da iniziare")}
        resto = " · ".join(f"{n} {s.lower()}" for s, n in conta.items() if n and s != "Conclusa")
        riquadri.append(riquadro("Attività della fase", f'{conta["Conclusa"]} di {len(stati)} concluse', resto))

    previste = ore_previste(fasi)
    riquadri.append(riquadro("Ore usate", f"{numero_it(sum(h for _, h, *_ in ore))} h",
                             f"di {numero_it(previste)} previste" if previste is not None else "Ore previste da definire"))

    voci = [f'<li><b>{e(nome)}</b> ({e(fase)}): {e(dettaglio)}</li>' for nome, fase, dettaglio in ritardi(fasi, oggi)]
    allarmi = (f'<h3 class="attenzione">Da recuperare</h3><ul class="allarmi">{"".join(voci)}</ul>' if voci
               else '<p class="nota">Nessuna attività né milestone in ritardo.</p>')
    return f'<div class="riquadri">{"".join(riquadri)}</div>{allarmi}'


def pagina_pianificazione(gruppo, logo, accento, fasi, ore, oggi):
    nome = gruppo.get("gruppo", {}).get("nome") or "Documentazione di progetto"
    testata = apertura(e("Pianificazione"), nome, "A che punto siamo: fasi, attività e milestone, con il tempo previsto e il tempo usato.",
                       [f"Situazione al {oggi.isoformat()}"], compatta=True)
    if not fasi:
        corpo = [sezione("fasi", "Fasi", '<p class="vuoto">Nessuna fase ancora pianificata in dati/pianificazione.toml</p>')]
        return pagina(f"Pianificazione - {nome}", testata, "\n".join(corpo), gruppo, logo, accento,
                      laterale=indice([("#fasi", "Fasi")]), corrente="pianificazione.html")

    lettura = ('<p class="nota">Fascia grigia: periodo previsto. Barra colorata: periodo effettivo, fino a oggi se in corso; '
               'il colore dice lo stato.</p>')
    corpo = [sezione("situazione", "Situazione", situazione(fasi, ore, oggi)),
             sezione("panoramica", "Panoramica delle fasi", LEGENDA_GANTT + gantt(fasi, oggi, attivita=False) + lettura),
             sezione("fasi", "Tempo per fase", tabella_fasi(fasi, ore, oggi)
                     + '<p class="nota">Le ore usate sono quelle di dati/ore.csv nel periodo effettivo di ogni fase; '
                       'il totale le comprende tutte.</p>', len(fasi))]
    voci_indice = [("#situazione", "Situazione"), ("#panoramica", "Panoramica"), ("#fasi", "Tempo per fase")]
    # id per posizione: il nome della fase può contenere caratteri che rompono i selettori dell'indice
    for numero, fase in enumerate(fasi, start=1):
        t = tempo(fase, oggi)
        riassunto = (f'<p class="riassunto">{stato_html(t["stato"])} · previsto dal {fase["inizio"]} al {fase["fine"]}'
                     + (f' · {e(fase["nota"])}' if fase.get("nota") else "") + "</p>")
        voci = len(fase.get("attivita", [])) + len(fase.get("milestone", []))
        contenuto = riassunto + LEGENDA_GANTT + (gantt([fase], oggi) if voci else "")
        if voci:
            contenuto += f'<details class="dettagli"><summary>Date previste ed effettive</summary>{tabella_attivita(fase, oggi)}</details>'
        corpo.append(sezione(f"fase-{numero}", fase["nome"], contenuto, voci))
        voci_indice.append((f"#fase-{numero}", fase["nome"]))
    return pagina(f"Pianificazione - {nome}", testata, "\n".join(corpo), gruppo, logo, accento,
                  laterale=indice(voci_indice), corrente="pianificazione.html")


def euro(x):
    """12600.5 -> "12.600,50 €", come euro() di modello/comuni.typ."""
    return f"{x:,.2f}".translate(str.maketrans(",.", ".,")) + "\u00a0€"


def ore_h(x):
    return f"{numero_it(round(x, 1))}\u00a0h"


def percento(x, segno=False):
    testo = f"{x:+.1f}".replace("-", "\u2212") if segno else f"{x:.0f}"
    return testo.replace(".", ",") + "%"


def ore_previste_al(fasi, giorno):
    """Ore previste fino al giorno incluso: le ore_previste di ogni fase, distribuite in modo uniforme sui suoi giorni previsti.

    None se una fase già iniziata, secondo il previsto, non indica le sue ore.
    """
    totale = 0
    for fase in fasi:
        if giorno < fase["inizio"]:
            continue
        if "ore_previste" not in fase:
            return None
        durata = (fase["fine"] - fase["inizio"]).days + 1
        totale += fase["ore_previste"] * min((giorno - fase["inizio"]).days + 1, durata) / durata
    return totale


def conti(ore, preventivo):
    """Ore e costi del preventivo (ripartizione di dati/preventivo.toml) e del consuntivo (dati/ore.csv), alle tariffe del preventivo."""
    tariffe, ripartizione = preventivo.get("tariffe", {}), preventivo.get("ripartizione", [])
    c = {"tariffe": {r: tariffe.get(r, 0) for r in RUOLI},
         "preventivo_ruolo": {r: sum(p.get(r, 0) for p in ripartizione) for r in RUOLI},
         "preventivo_membro": {p.get("membro", ""): sum(p.get(r, 0) for r in RUOLI) for p in ripartizione},
         "consuntivo_ruolo": dict.fromkeys(RUOLI, 0.0), "consuntivo_membro": {}}
    for _, h, membro, ruolo in ore:
        c["consuntivo_ruolo"][ruolo] = c["consuntivo_ruolo"].get(ruolo, 0) + h
        c["consuntivo_membro"][membro] = c["consuntivo_membro"].get(membro, 0) + h
    c["ore_preventivo"] = sum(c["preventivo_ruolo"].values())
    c["ore_consuntivo"] = sum(c["consuntivo_ruolo"].values())
    c["costo_preventivo"] = sum(x * c["tariffe"][r] for r, x in c["preventivo_ruolo"].items())
    c["costo_consuntivo"] = sum(h * tariffe.get(r, 0) for r, h in c["consuntivo_ruolo"].items())
    return c


def costo_aggiudicato(gruppo):
    costo = gruppo.get("progetto", {}).get("costo_aggiudicato", 0)
    return costo if numero(costo) and costo > 0 else 0


def controlli(gruppo, fasi, ore, c, oggi):
    """Indicatori del cruscotto come (nome, stato, valore in HTML, soglia).

    Lo stato è "Sotto controllo", "Fuori soglia" oppure "Da misurare" quando mancano i dati.
    """
    risultati = []

    aggiudicato = costo_aggiudicato(gruppo)
    limite, quale = (aggiudicato, "aggiudicato") if aggiudicato else (c["costo_preventivo"], "preventivato")
    if limite:
        speso = c["costo_consuntivo"]
        stato = "Sotto controllo" if speso <= limite else "Fuori soglia"
        valore = f"{euro(speso)} di {euro(limite)}, il {percento(speso / limite * 100)}."
    else:
        stato, valore = "Da misurare", "Manca il preventivo: la ripartizione di dati/preventivo.toml è vuota."
    risultati.append(("Costo", stato, valore, f"il costo consuntivo non supera il costo {quale}."))

    soglia = gruppo.get("soglie", {}).get("scostamento_ore", 10)
    soglia = soglia if numero(soglia) and soglia > 0 else 10
    previste = ore_previste_al(fasi, oggi)
    consumate = sum(h for giorno, h, *_ in ore if giorno <= oggi)
    if not fasi:
        stato, valore = "Da misurare", "Manca la pianificazione in dati/pianificazione.toml."
    elif previste is None:
        stato, valore = "Da misurare", "Una fase già iniziata non ha ore_previste in dati/pianificazione.toml."
    elif not previste:
        stato, valore = (("Fuori soglia", f"{ore_h(consumate)} consumate e nessuna ora prevista fino a oggi.") if consumate
                         else ("Da misurare", "Nessuna ora prevista né consumata fino a oggi."))
    else:
        scarto = (consumate - previste) / previste * 100
        stato = "Sotto controllo" if abs(scarto) <= soglia else "Fuori soglia"
        valore = f"{ore_h(consumate)} consumate e {ore_h(previste)} previste a oggi: {percento(scarto, segno=True)}."
    risultati.append(("Ore rispetto al previsto", stato, valore, f"scostamento entro ±{numero_it(soglia)}% dalle ore previste a oggi."))

    in_ritardo = ritardi(fasi, oggi)
    if not fasi:
        stato, valore = "Da misurare", "Manca la pianificazione in dati/pianificazione.toml."
    elif in_ritardo:
        nomi = [nome for nome, _, _ in in_ritardo]
        quante = "1 voce" if len(nomi) == 1 else f"{len(nomi)} voci"
        elenco_nomi = ", ".join(nomi[:3]) + (f" e altre {len(nomi) - 3}" if len(nomi) > 3 else "")
        stato = "Fuori soglia"
        valore = f'{quante} in ritardo: {e(elenco_nomi)}. <a href="pianificazione.html#situazione">Dettagli</a>'
    else:
        stato, valore = "Sotto controllo", "Nessuna attività né milestone in ritardo."
    risultati.append(("Tempi", stato, valore, "nessuna attività né milestone oltre la data prevista."))

    if not ore:
        stato, valore = "Da misurare", "Nessuna ora ancora registrata in dati/ore.csv."
    else:
        per_membro = c["consuntivo_membro"]
        oltre = [m for m, h in sorted(per_membro.items()) if h > min(95, c["preventivo_membro"].get(m, 95))]
        stato = "Fuori soglia" if oltre else "Sotto controllo"
        valore = f"Oltre il limite: {e(', '.join(oltre))}." if oltre else f"Al massimo {ore_h(max(per_membro.values()))} per membro."
    risultati.append(("Ore per membro", stato, valore, "nessuno oltre le ore della sua ripartizione né oltre 95 ore."))
    return risultati


def esito(risultati):
    """Frase in apertura del cruscotto: il progetto è sotto controllo, e su quanti indicatori."""
    n = len(risultati)
    fuori = [nome.lower() for nome, stato, *_ in risultati if stato == "Fuori soglia"]
    misurati = sum(1 for _, stato, *_ in risultati if stato != "Da misurare")
    if fuori:
        stato, testo = "Fuori soglia", f"{len(fuori)} {'indicatore' if len(fuori) == 1 else 'indicatori'} su {n} ({', '.join(fuori)})."
    elif not misurati:
        stato, testo = "Da misurare", "nessun indicatore ha ancora i dati che servono."
    elif misurati == n:
        stato, testo = "Sotto controllo", f"tutti e {n} gli indicatori sono nella soglia."
    else:
        stato, testo = "Sotto controllo", f"{misurati} {'indicatore' if misurati == 1 else 'indicatori'} su {n} nella soglia, {n - misurati} ancora da misurare."
    return f'<p class="esito">{stato_html(stato)}: {e(testo)}</p>'


def ore_e_costi(gruppo, membri, fasi, c):
    """Riquadri dei totali, poi preventivo e consuntivo per ruolo e per membro."""
    def quota(parte, totale):
        return round(min(parte / totale, 1) * 100, 2) if totale else None

    aggiudicato = costo_aggiudicato(gruppo)
    preventivo_h, preventivo = c["ore_preventivo"], c["costo_preventivo"]
    riquadri = [
        riquadro("Ore consumate", ore_h(c["ore_consuntivo"]),
                 f"di {ore_h(preventivo_h)} preventivate" if preventivo_h else "Preventivo da definire",
                 quota(c["ore_consuntivo"], preventivo_h)),
        riquadro("Costo consuntivo", euro(c["costo_consuntivo"]),
                 f"di {euro(preventivo)} preventivati" if preventivo else "Preventivo da definire",
                 quota(c["costo_consuntivo"], preventivo)),
        riquadro("Residuo del preventivo", euro(preventivo - c["costo_consuntivo"]) if preventivo else "—",
                 f"{ore_h(preventivo_h - c['ore_consuntivo'])} ancora da usare" if preventivo_h else "Preventivo da definire"),
        riquadro("Costo aggiudicato", euro(aggiudicato) if aggiudicato else "Da definire",
                 f"Residuo: {euro(aggiudicato - c['costo_consuntivo'])}" if aggiudicato
                 else "In dati/gruppo.toml dopo l'aggiudicazione"),
    ]

    righe = []
    for r in RUOLI:
        tariffa, previste, consumate = c["tariffe"][r], c["preventivo_ruolo"][r], c["consuntivo_ruolo"][r]
        righe.append(f'<tr><td><span class="ruolo r-{e(slug(r))}">{e(r)}</span></td><td class="numeri">{numero_it(tariffa)} €/h</td>'
                     f'<td class="numeri">{ore_h(previste)}</td><td class="numeri">{ore_h(consumate)}</td>'
                     f'<td class="numeri">{euro(previste * tariffa)}</td><td class="numeri">{euro(consumate * tariffa)}</td></tr>')
    totale = (f'<tfoot><tr><td>Totale</td><td></td><td class="numeri">{ore_h(preventivo_h)}</td><td class="numeri">{ore_h(c["ore_consuntivo"])}</td>'
              f'<td class="numeri">{euro(preventivo)}</td><td class="numeri">{euro(c["costo_consuntivo"])}</td></tr></tfoot>')
    per_ruolo = ('<h3>Per ruolo</h3><div class="scorri" role="region" aria-label="Ore e costi per ruolo" tabindex="0"><table class="periodi">'
                 '<thead><tr><th scope="col">Ruolo</th><th scope="col">Tariffa</th><th scope="col">Ore preventivate</th>'
                 '<th scope="col">Ore consumate</th><th scope="col">Costo preventivato</th><th scope="col">Costo consuntivo</th></tr></thead>'
                 f'<tbody>{"".join(righe)}</tbody>{totale}</table></div>')

    righe = []
    for m in membri + sorted(set(c["consuntivo_membro"]) - set(membri)):
        previste, consumate = c["preventivo_membro"].get(m), c["consuntivo_membro"].get(m, 0)
        usate = "—"
        if previste:
            uso = consumate / previste * 100
            classe = ' class="oltre"' if consumate > previste else ""
            usate = (f'{percento(uso)}<div class="avanzamento" aria-hidden="true"><i{classe} style="width:{pct(round(min(uso, 100), 2))}%"></i></div>')
        righe.append(f'<tr><td>{e(m)}</td><td class="numeri">{ore_h(previste) if previste is not None else "—"}</td>'
                     f'<td class="numeri">{ore_h(consumate)}</td>'
                     f'<td class="numeri">{ore_h(previste - consumate) if previste is not None else "—"}</td><td class="numeri">{usate}</td></tr>')
    per_membro = ('<h3>Per membro</h3><div class="scorri" role="region" aria-label="Ore per membro" tabindex="0"><table class="periodi">'
                  '<thead><tr><th scope="col">Membro</th><th scope="col">Ore preventivate</th><th scope="col">Ore consumate</th>'
                  f'<th scope="col">Ore residue</th><th scope="col">Usate</th></tr></thead><tbody>{"".join(righe)}</tbody></table></div>')

    note = []
    if not preventivo_h:
        note.append("La ripartizione delle ore di dati/preventivo.toml è ancora vuota: le colonne del preventivo si riempiono "
                    "con la Dichiarazione degli impegni.")
    fasi_h = ore_previste(fasi) if fasi else None
    if preventivo_h and fasi_h is not None and abs(fasi_h - preventivo_h) > 0.05:
        note.append(f"Le ore previste delle fasi di dati/pianificazione.toml ({ore_h(fasi_h)}) non coincidono con quelle del preventivo "
                    f"({ore_h(preventivo_h)}).")
    note.append("Le ore consumate sono quelle di dati/ore.csv; i costi sono calcolati alle tariffe di dati/preventivo.toml.")
    # senza preventivo né ore le tabelle sarebbero solo zeri
    tabelle = per_ruolo + per_membro if preventivo_h or c["ore_consuntivo"] else ""
    return f'<div class="riquadri">{"".join(riquadri)}</div>{tabelle}' + "".join(f'<p class="nota">{e(n)}</p>' for n in note)


def tacche(massimo):
    """Valori tondi dell'asse verticale, con passo 1, 2 o 5 per una potenza di 10, da 0 fino a coprire `massimo`."""
    passo = 10 ** math.floor(math.log10(massimo / 4))
    passo *= next(m for m in (1, 2, 5, 10) if massimo / (passo * m) <= 5)
    return [round(i * passo, 6) for i in range(math.ceil(massimo / passo) + 1)]


def grafico_ore(fasi, ore, preventivo_h, oggi):
    """Ore consumate e previste cumulate, un punto ogni 7 giorni più oggi e l'ultimo giorno; "" senza dati.

    Le previste vengono da ore_previste_al(), le consumate da dati/ore.csv e si fermano a oggi.
    Il punto t è la fine del t-esimo giorno dall'inizio; t = 0 è l'inizio del primo.
    """
    con_ore = [f for f in fasi if f.get("ore_previste", 0) > 0]
    giorni_ore = [giorno for giorno, *_ in ore]
    if not con_ore and not giorni_ore:
        return ""
    inizio = min([f["inizio"] for f in con_ore] + giorni_ore)
    fine = max([f["fine"] for f in con_ore] + giorni_ore)
    durata = (fine - inizio).days + 1
    t_oggi = (oggi - inizio).days + 1
    passi = sorted(set(range(0, durata, 7)) | {durata} | ({t_oggi} if 0 < t_oggi < durata else set()))
    punti = []
    for t in passi:
        giorno = inizio + datetime.timedelta(days=t - 1)
        consumate = sum(h for g, h, *_ in ore if g <= giorno) if giorno <= oggi else None
        punti.append((t, giorno, ore_previste_al(fasi, giorno), consumate))
    valori = [v for _, _, p, c in punti for v in (p, c) if v is not None] + [preventivo_h]
    if max(valori) <= 0:
        return ""
    scala_y = tacche(max(valori))
    alto = scala_y[-1]

    def x(t):
        return round(t / durata * 100, 2)

    def y(v):
        return round(v / alto * 100, 2)

    previste = []
    for t, _, p, _ in punti:
        if p is None:
            break
        previste.append(f"{pct(x(t))},{pct(round(100 - y(p), 2))}")
    consumate = [(t, c) for t, _, _, c in punti if c is not None]
    linee = "".join(f'<polyline class="{classe}" points="{" ".join(p)}" vector-effect="non-scaling-stroke"/>'
                    for classe, p in (("l-previste", previste), ("l-consumate", [f"{pct(x(t))},{pct(round(100 - y(c), 2))}" for t, c in consumate]))
                    if len(p) > 1)
    griglia = "".join(f'<span class="tacca-y" style="bottom:{pct(y(v))}%"><b>{numero_it(v)}</b></span>' for v in scala_y)
    riferimento = (f'<span class="rif-g" style="bottom:{pct(y(preventivo_h))}%"><span>Preventivo {ore_h(preventivo_h)}</span></span>'
                   if preventivo_h else "")
    segni = f'<span class="oggi-g" style="left:{pct(x(t_oggi))}%"></span>' if 0 < t_oggi <= durata else ""
    if consumate:
        t, c = consumate[-1]
        segni += f'<span class="punto-g" style="left:{pct(x(t))}%;bottom:{pct(y(c))}%"></span>'
    dati = [{"x": x(t), "al": f"Al {g.isoformat()}", "p": None if p is None else ore_h(p), "c": None if c is None else ore_h(c)}
            for t, g, p, c in punti]
    _, asse = scala(inizio, fine + UN_GIORNO)
    voci_legenda = [("l-consumate", "Ore consumate"), ("l-previste", "Ore previste")]
    voci_legenda += [("l-preventivo", "Ore del preventivo")] if preventivo_h else []
    legenda = '<ul class="legenda">' + "".join(f'<li><i class="{k}" aria-hidden="true"></i>{t}</li>'
                                               for k, t in voci_legenda + [("l-oggi", "Oggi")]) + "</ul>"
    figura = (f'<figure class="grafico" data-punti="{e(json.dumps(dati, ensure_ascii=False))}">'
              '<div class="piano-g" tabindex="0" role="group" aria-label="Ore consumate e previste: frecce sinistra e destra per leggere i valori">'
              f'{griglia}{riferimento}<svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true" focusable="false">{linee}</svg>'
              f'{segni}<span class="mirino" hidden></span><div class="fumetto" hidden aria-live="polite"></div></div>'
              f'{asse}<figcaption>{legenda}</figcaption></figure>')

    if t_oggi > 0:
        previste_oggi = ore_previste_al(fasi, oggi)
        sintesi = (f"Al {oggi.isoformat()}: {ore_h(sum(h for g, h, *_ in ore if g <= oggi))} consumate"
                   + (f" e {ore_h(previste_oggi)} previste" if previste_oggi is not None else "")
                   + (f", su {ore_h(preventivo_h)} del preventivo." if preventivo_h else "."))
    else:
        sintesi = f"Il conteggio delle ore parte il {inizio.isoformat()}."
    righe = "".join(f'<tr><td class="data">{g.isoformat()}</td><td class="numeri">{"—" if p is None else ore_h(p)}</td>'
                    f'<td class="numeri">{"—" if c is None else ore_h(c)}</td></tr>' for t, g, p, c in punti if t)
    tabella = ('<details class="dettagli"><summary>Valori del grafico</summary>'
               '<div class="scorri" role="region" aria-label="Valori del grafico" tabindex="0"><table class="periodi">'
               '<thead><tr><th scope="col">Al giorno</th><th scope="col">Ore previste</th><th scope="col">Ore consumate</th></tr></thead>'
               f'<tbody>{righe}</tbody></table></div></details>')
    return f'{figura}<p class="nota">{e(sintesi)}</p>{tabella}'


def avanzamento(fasi, oggi):
    """Attività concluse e milestone raggiunte, in totale e per fase."""
    righe, totali = [], [0, 0, 0, 0]
    for fase in fasi:
        attivita, milestone = fase.get("attivita", []), fase.get("milestone", [])
        conte = [sum(1 for a in attivita if a.get("fine_effettiva")), len(attivita),
                 sum(1 for m in milestone if m.get("data_effettiva")), len(milestone)]
        totali = [a + b for a, b in zip(totali, conte)]
        t = tempo(fase, oggi)
        righe.append(f'<tr><td>{e(fase["nome"])}</td><td class="numeri">{conte[0]} di {conte[1]}</td>'
                     f'<td class="numeri">{conte[2]} di {conte[3]}</td><td>{stato_html(t["stato"], t["dettaglio"])}</td></tr>')
    concluse, attivita, raggiunte, milestone = totali
    riquadri = (riquadro("Attività concluse", f"{concluse} di {attivita}", "In tutte le fasi",
                         round(concluse / attivita * 100, 2) if attivita else None)
                + riquadro("Milestone raggiunte", f"{raggiunte} di {milestone}", "In tutte le fasi",
                           round(raggiunte / milestone * 100, 2) if milestone else None))
    tabella = ('<div class="scorri" role="region" aria-label="Avanzamento per fase" tabindex="0"><table class="periodi">'
               '<thead><tr><th scope="col">Fase</th><th scope="col">Attività concluse</th><th scope="col">Milestone raggiunte</th>'
               f'<th scope="col">Stato</th></tr></thead><tbody>{"".join(righe)}</tbody></table></div>')
    return (f'<div class="riquadri">{riquadri}</div>{tabella}'
            '<p class="nota">Un\'attività conta quando ha la fine effettiva, una milestone quando ha la data effettiva. '
            'Il diagramma di Gantt di ogni fase è nella <a href="pianificazione.html">Pianificazione</a>.</p>')


def consuntivo_periodi(periodi, ore, tariffe, oggi):
    """Ore e costo di ogni periodo di dati/ruoli.csv; ogni ora conta nel periodo del suo membro."""
    giorno = datetime.date.fromisoformat
    somme = {k: [0.0, 0.0] for k in sorted({(p["inizio"], p["fine"]) for p in periodi})}
    for g, h, membro, ruolo in ore:
        periodo = next((p for p in periodi if p["membro"] == membro and giorno(p["inizio"]) <= g <= giorno(p["fine"])), None)
        if periodo:
            somma = somme[periodo["inizio"], periodo["fine"]]
            somma[0] += h
            somma[1] += h * tariffe.get(ruolo, 0)
    righe = []
    for (inizio, fine), (h, costo) in somme.items():
        stato = "Da iniziare" if giorno(inizio) > oggi else "Concluso" if giorno(fine) < oggi else "In corso"
        righe.append(f'<tr><td class="data">{intervallo(giorno(inizio), giorno(fine))}</td><td>{stato_html(stato)}</td>'
                     f'<td class="numeri">{ore_h(h)}</td><td class="numeri">{euro(costo)}</td></tr>')
    return ('<div class="scorri" role="region" aria-label="Consuntivo per periodo" tabindex="0"><table class="periodi">'
            '<thead><tr><th scope="col">Periodo</th><th scope="col">Stato</th><th scope="col">Ore consumate</th>'
            f'<th scope="col">Costo consuntivo</th></tr></thead><tbody>{"".join(righe)}</tbody></table></div>'
            '<p class="nota">I periodi sono quelli di dati/ruoli.csv, uno per sprint; il preventivo di ogni periodo sta nel Piano di Progetto.</p>')


def pagina_cruscotto(gruppo, logo, accento, fasi, ore, preventivo, periodi, oggi):
    """Il progetto è sotto controllo? Indicatori con le soglie, ore e costi, andamento, avanzamento e consuntivo per periodo."""
    nome = gruppo.get("gruppo", {}).get("nome") or "Documentazione di progetto"
    testata = apertura(e("Cruscotto"), nome, "Il progetto è sotto controllo? Ore, costi e tempi, previsti e consuntivi, "
                       "a confronto con le soglie del gruppo.", [f"Situazione al {oggi.isoformat()}"], compatta=True)
    c = conti(ore, preventivo)
    risultati = controlli(gruppo, fasi, ore, c, oggi)
    indicatori = "".join(riquadro(nome_, stato_html(stato), f'{valore}<span class="soglia">Soglia: {e(soglia)}</span>')
                         for nome_, stato, valore, soglia in risultati)
    grafico = grafico_ore(fasi, ore, c["ore_preventivo"], oggi)
    membri = [nome_membro(m) for m in gruppo.get("membro", [])]
    corpo = [
        sezione("controllo", "Sotto controllo?", esito(risultati) + f'<div class="riquadri">{indicatori}</div>'),
        sezione("ore-e-costi", "Ore e costi", ore_e_costi(gruppo, membri, fasi, c)),
        sezione("andamento", "Andamento delle ore", grafico or '<p class="vuoto">Il grafico compare quando una fase di '
                'dati/pianificazione.toml ha ore_previste o dati/ore.csv ha la prima ora.</p>'),
        sezione("avanzamento", "Avanzamento", avanzamento(fasi, oggi) if fasi
                else '<p class="vuoto">Nessuna fase ancora pianificata in dati/pianificazione.toml</p>'),
        sezione("periodi", "Consuntivo per periodo", consuntivo_periodi(periodi, ore, c["tariffe"], oggi) if periodi
                else '<p class="vuoto">Nessun periodo ancora registrato in dati/ruoli.csv</p>'),
    ]
    laterale = indice([("#controllo", "Sotto controllo?"), ("#ore-e-costi", "Ore e costi"), ("#andamento", "Andamento delle ore"),
                       ("#avanzamento", "Avanzamento"), ("#periodi", "Consuntivo per periodo")])
    return pagina(f"Cruscotto - {nome}", testata, "\n".join(corpo), gruppo, logo, accento, laterale=laterale,
                  corrente="cruscotto.html", script=SCRIPT_GRAFICO if grafico else "")


def senza_accenti(testo):
    return "".join(c for c in unicodedata.normalize("NFD", testo) if not unicodedata.combining(c)).casefold()


def pagina_glossario(gruppo, voci, logo, accento):
    nome = gruppo.get("gruppo", {}).get("nome") or "Documentazione di progetto"
    per_iniziale = {}
    for voce_ in sorted(voci, key=lambda v: senza_accenti(v["termine"])):
        iniziale = senza_accenti(voce_["termine"])[:1].upper()
        per_iniziale.setdefault(iniziale if iniziale.isalpha() else "#", []).append(voce_)

    testata = apertura(e("Glossario"), nome, "I termini del progetto, con definizioni e sinonimi, come sono usati nei documenti.",
                       ["1 voce" if len(voci) == 1 else f"{len(voci)} voci"], compatta=True)
    if not per_iniziale:
        corpo = [sezione("vuoto", "Nessuna voce", '<p class="vuoto">Nessuna voce ancora presente</p>')]
        return pagina(f"Glossario - {nome}", testata, "\n".join(corpo), gruppo, logo, accento,
                      laterale=indice([("#vuoto", "Glossario")]), corrente="glossario.html")

    corpo = ['<div class="cerca"><label for="cerca">Cerca un termine</label>'
             '<input id="cerca" type="search" autocomplete="off" spellcheck="false">'
             '<p class="nota" id="esito-ricerca" aria-live="polite"></p></div>']
    for iniziale, gruppo_voci in per_iniziale.items():
        righe = []
        for voce_ in gruppo_voci:
            sinonimi = voce_.get("sinonimi", [])
            ancore = "".join(f'<span id="{e(slug(s))}"></span>' for s in sinonimi)
            nota = f'<span class="nota">Sinonimi: {e(", ".join(sinonimi))}</span>' if sinonimi else ""
            righe.append(f'<dt id="{e(slug(voce_["termine"]))}">{ancore}{e(voce_["termine"])}</dt>'
                         f"<dd>{e(voce_['definizione'])}{nota}</dd>")
        blocco = sezione(slug(iniziale) or "altro", iniziale, "<dl>" + "".join(righe) + "</dl>", len(gruppo_voci))
        corpo.append(blocco.replace('class="sezione"', 'class="sezione lettera"', 1))
    alfabeto = "".join(f'<li><a href="#{e(slug(i)) or "altro"}">{e(i)}</a></li>' for i in per_iniziale)
    laterale = (f'<nav class="indice" aria-label="Iniziali"><p class="titoletto" aria-hidden="true">Iniziali</p>'
                f'<ul class="alfabeto">{alfabeto}</ul></nav>')
    return pagina(f"Glossario - {nome}", testata, "\n".join(corpo), gruppo, logo, accento, laterale=laterale,
                  corrente="glossario.html", script=SCRIPT_GLOSSARIO)


def pagina_pdf(gruppo, logo, accento, pdf):
    """Pagina di lettura di un PDF del sito: testo selezionabile, link attivi, zoom e download, anche su mobile."""
    nome = gruppo.get("gruppo", {}).get("nome") or "Documentazione di progetto"
    titolo = pdf.removesuffix(".pdf").replace("_", " ")
    # pdf_viewer.css imposta color-scheme su :root: va prima dello stile del sito, che decide il tema
    in_testa = (f'<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>\n'
                f'<link rel="stylesheet" href="{PDFJS}web/pdf_viewer.css" integrity="{SRI_PDFJS["web/pdf_viewer.css"]}" crossorigin="anonymous">\n'
                f"<style>{STILE_PDF}</style>")
    moduli = "".join(f'<script type="module" src="{PDFJS}{f}" integrity="{SRI_PDFJS[f]}" crossorigin="anonymous"></script>\n'
                     for f in ("build/pdf.min.mjs", "web/pdf_viewer.mjs"))
    corpo = f"""<div class="comandi-pdf">
<a class="torna" href="index.html"><span aria-hidden="true">←</span><span class="etichetta">Documenti</span></a>
<h1>{e(titolo)}</h1>
<p class="numero-pagina mono"><span class="sr-only">Pagina </span><span id="pagina-pdf">–</span></p>
<div class="zoom" role="group" aria-label="Ingrandimento">
<button type="button" data-zoom="meno" aria-label="Riduci" title="Riduci" disabled>−</button>
<button type="button" data-zoom="adatta" title="Adatta alla finestra" disabled><span class="sr-only">Adatta alla finestra, ora al </span><span id="zoom-pdf">100%</span></button>
<button type="button" data-zoom="piu" aria-label="Ingrandisci" title="Ingrandisci" disabled>+</button>
</div>
<a class="scarica" href="{e(pdf)}" download>Scarica<span class="sr-only"> il PDF</span></a>
</div>
<div class="area-pdf"><div id="contenitore-pdf" tabindex="0" role="region" aria-label="Pagine del documento" data-pdf="{e(pdf)}" data-pdfjs="{PDFJS}" data-worker="{SRI_PDFJS["build/pdf.worker.min.mjs"]}">
<div class="pdfViewer"></div></div>
<p class="avviso-pdf" id="avviso-pdf" role="status">Caricamento del PDF… Se non compare, <a href="{e(pdf)}">scaricalo</a>.</p>
</div>
{moduli}<script type="module">{SCRIPT_PDF}</script>"""
    return pagina(f"{titolo} - {nome}", "", corpo, gruppo, logo, accento, in_testa=in_testa)


def main():
    parser = argparse.ArgumentParser(description="Compila i documenti pubblicabili e genera il sito.")
    parser.add_argument("--out", required=True, type=Path, help="cartella di destinazione")
    parser.add_argument("--typst", default="typst", help="percorso dell'eseguibile typst")
    argomenti = parser.parse_args()
    for flusso in (sys.stdout, sys.stderr):
        flusso.reconfigure(encoding="utf-8", errors="replace")

    typst = shutil.which(argomenti.typst)
    if typst is None:
        sys.exit(f"errore: typst non trovato ({argomenti.typst}); installarlo o indicarne il percorso con --typst")

    out = argomenti.out.resolve()
    if out.exists():
        # si cancella solo un sito generato in precedenza, mai una cartella qualsiasi
        if any(out.iterdir()) and not (out / ".nojekyll").exists():
            sys.exit(f"errore: {out} non è vuota e non contiene un sito generato")
        shutil.rmtree(out)
    out.mkdir(parents=True)
    (out / ".nojekyll").write_text("", encoding="utf-8")

    gruppo = tomllib.loads((RADICE / "dati/gruppo.toml").read_text(encoding="utf-8-sig"))
    voci = tomllib.loads((RADICE / "dati/glossario.toml").read_text(encoding="utf-8-sig")).get("voce", [])
    periodi = leggi_ruoli()
    info = gruppo.get("gruppo", {})
    accento = info.get("colore") or ACCENTO_PREDEFINITO
    logo = None
    if info.get("logo") and (RADICE / info["logo"]).is_file():
        logo = "logo" + Path(info["logo"]).suffix.lower()
        shutil.copy(RADICE / info["logo"], out / logo)
    # caratteri del sito con le loro licenze OFL; senza la cartella restano i caratteri di sistema
    if (RADICE / "assets/font").is_dir():
        shutil.copytree(RADICE / "assets/font", out / "font")
    fasi, ore, oggi = leggi_pianificazione(), leggi_ore(), datetime.date.today()
    (out / "index.html").write_text(pagina_indice(gruppo, typst, out, logo, accento, fasi, oggi), encoding="utf-8")
    (out / "cruscotto.html").write_text(pagina_cruscotto(gruppo, logo, accento, fasi, ore, leggi_preventivo(), periodi, oggi),
                                        encoding="utf-8")
    (out / "glossario.html").write_text(pagina_glossario(gruppo, voci, logo, accento), encoding="utf-8")
    (out / "ruoli.html").write_text(pagina_ruoli(gruppo, logo, accento, periodi), encoding="utf-8")
    (out / "pianificazione.html").write_text(pagina_pianificazione(gruppo, logo, accento, fasi, ore, oggi), encoding="utf-8")
    for pdf in out.glob("*.pdf"):
        (out / f"{pdf.stem}.html").write_text(pagina_pdf(gruppo, logo, accento, pdf.name), encoding="utf-8")
    print(f"sito generato in {out}: {len(list(out.glob('*.pdf')))} PDF")


if __name__ == "__main__":
    main()
