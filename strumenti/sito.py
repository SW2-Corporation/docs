"""Compila con typst i documenti pubblicabili e genera il sito statico.

Uso: python strumenti/sito.py --out site [--typst percorso]

Vanno sul sito i documenti rilasciati (prima riga del registro = approvazione),
tutte le lettere e tutti i verbali, più le pagine del glossario e dei ruoli.
"""

import argparse
import csv
import datetime
import html
import json
import re
import shutil
import subprocess
import sys
import tomllib
import unicodedata
from pathlib import Path

from verifica import RADICE, RUOLI, data_iso, nome_verbale, rilascio, slug

ACCENTO_PREDEFINITO = "#d7262f"
SOTTOTITOLO = "Progetto didattico di Ingegneria del Software, Università degli Studi di Padova"
MESI = ("gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic")

# Tema scuro: usato sia quando il dispositivo lo preferisce sia quando l'utente lo sceglie.
TEMA_SCURO = """--carta: #0f0f0f; --inchiostro: #ece9e2; --tenue: #9c9992; --filetto: #2b2b2b; --superficie: #181818;
  --accento-testo: var(--accento-chiaro); --sole: block; --luna: none; color-scheme: dark;"""

# {accento} e {scuro} vengono sostituiti dal colore del gruppo e dal blocco del tema scuro.
# Carta e inchiostro; serif per i titoli, monospazio per date ed etichette.
# --accento-testo è la variante dell'accento usata per il testo: sugli sfondi scuri è schiarita
# per tenere il contrasto sopra 4,5:1. I colori dei ruoli reggono il testo bianco in entrambi i temi.
STILE = """
:root { --accento: {accento}; --accento-chiaro: #f0545b; --accento-chiaro: color-mix(in srgb, var(--accento) 72%, white);
        --accento-testo: var(--accento); --carta: #faf9f6; --inchiostro: #141414; --tenue: #6a6a66; --filetto: #dcd9d2;
        --superficie: #f0eee8; --sole: none; --luna: block; color-scheme: light;
        --serif: "Iowan Old Style", "Palatino Linotype", Palatino, "Book Antiqua", Georgia, "Times New Roman", serif;
        --sans: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        --mono: ui-monospace, "Cascadia Code", "SF Mono", Menlo, Consolas, "Liberation Mono", monospace; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { {scuro} } }
:root[data-theme="dark"] { {scuro} }
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
body { margin: 0; font-family: var(--sans); font-size: 1rem; line-height: 1.6; background: var(--carta); color: var(--inchiostro);
       -webkit-font-smoothing: antialiased; border-top: 3px solid var(--accento); }
a { color: inherit; }
:focus-visible { outline: 2px solid var(--accento-testo); outline-offset: 3px; }
.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; border: 0; }
.salta { position: absolute; left: 1rem; top: -4rem; z-index: 10; padding: .6rem 1rem; background: var(--inchiostro); color: var(--carta);
         font-family: var(--mono); font-size: .8rem; text-decoration: none; }
.salta:focus { top: 1rem; }
.mono, .kicker, .meta, .nota, .vuoto, .conta, .dettaglio, .utente, .indice, .sezione h3, .asse, .legenda, .periodi th, .periodi .data, .freccia, .alfabeto {
  font-family: var(--mono); font-size: .76rem; letter-spacing: .05em; text-transform: uppercase; }
.pagina { max-width: 74rem; margin: 0 auto; padding: 0 clamp(1rem, 4vw, 3rem); }

.testa { display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: 1rem 0; border-bottom: 1px solid var(--filetto); }
.marchio { display: inline-flex; align-items: center; gap: .8rem; text-decoration: none; color: var(--tenue); }
.marchio img { width: 34px; height: 34px; border-radius: 50%; }
.marchio b { color: var(--inchiostro); font-weight: 600; }
.marchio .sep { padding: 0 .4rem; }
.marchio .sep, .marchio .sotto-marchio { display: none; }
@media (min-width: 40rem) { .marchio .sep, .marchio .sotto-marchio { display: inline; } }
.tema { width: 2.75rem; height: 2.75rem; display: grid; place-items: center; border: 0; border-radius: 50%; background: transparent;
        color: var(--inchiostro); cursor: pointer; }
.tema:hover { background: var(--superficie); }
.tema svg { width: 20px; height: 20px; }
.tema .sole { display: var(--sole); }
.tema .luna { display: var(--luna); }

.apertura { padding: clamp(3rem, 8vw, 6rem) 0 2.5rem; border-bottom: 1px solid var(--inchiostro); }
.apertura.compatta { padding-top: clamp(2rem, 5vw, 3.5rem); padding-bottom: 2rem; }
.kicker { margin: 0 0 1rem; color: var(--accento-testo); }
.titolone { margin: 0; font-family: var(--serif); font-weight: 400; font-size: clamp(2.8rem, 8vw, 6rem); line-height: .96; letter-spacing: -.025em; text-wrap: balance; }
.compatta .titolone { font-size: clamp(2.2rem, 5vw, 3.6rem); }
.titolone .accento { color: var(--accento-testo); }
.sotto { margin: 1.25rem 0 0; max-width: 38rem; font-size: 1.1rem; color: var(--tenue); }
.meta { list-style: none; margin: 1.75rem 0 0; padding: 0; display: flex; flex-wrap: wrap; gap: .4rem 0; color: var(--tenue); text-transform: none; letter-spacing: .02em; font-size: .82rem; }
.meta li + li::before { content: "·"; padding: 0 .7rem; }
.meta a { color: var(--inchiostro); text-decoration: none; border-bottom: 1px solid var(--filetto); }
.meta a:hover { border-color: var(--accento-testo); color: var(--accento-testo); }

.colonne { display: grid; grid-template-columns: minmax(0, 1fr); }
/* su mobile l'indice è una barra fissa a tutta larghezza che scorre in orizzontale */
.indice { position: sticky; top: 0; z-index: 5; min-width: 0; display: flex; align-items: center; gap: 1.25rem;
          margin: 0 calc(-1 * clamp(1rem, 4vw, 3rem)); padding: 0 clamp(1rem, 4vw, 3rem); overflow-x: auto; scrollbar-width: none;
          background: var(--carta); border-bottom: 1px solid var(--filetto); }
.indice::-webkit-scrollbar { display: none; }
.indice ol, .indice ul { display: flex; gap: 1.25rem; list-style: none; margin: 0; padding: 0; }
.indice ul.pagine { padding-left: 1.25rem; border-left: 1px solid var(--filetto); }
.indice li { flex: none; }
.indice a { display: flex; gap: .6rem; padding: .9rem 0; color: var(--tenue); text-decoration: none; border-bottom: 2px solid transparent; white-space: nowrap; }
.indice a:hover, .indice a[aria-current="true"] { color: var(--inchiostro); }
.indice a[aria-current="true"] { border-bottom-color: var(--accento); }
.indice a[aria-current="true"] .n { color: var(--accento-testo); }
.indice .n { color: var(--tenue); }
.indice .pagine a { gap: .4rem; }
.indice .pagine a::after { content: "→"; color: var(--accento-testo); }
@media (min-width: 60rem) {
  .colonne { grid-template-columns: 13rem minmax(0, 1fr); gap: 0 5rem; }
  .indice { top: 1.5rem; align-self: start; display: block; margin: 0; padding: 2.5rem 0 0; overflow: visible; background: transparent; border-bottom: 0; }
  .indice ol, .indice ul { display: block; }
  .indice ul.pagine { margin-top: 1.25rem; padding-left: 0; border-left: 0; }
  .indice a { padding: .7rem 0; border-bottom: 1px solid var(--filetto); }
  .indice a[aria-current="true"] { border-bottom-color: var(--filetto); }
}

.sezioni { min-width: 0; }
.sezione { padding: 2.5rem 0; border-bottom: 1px solid var(--filetto); scroll-margin-top: 4rem; }
@media (min-width: 60rem) { .sezione { scroll-margin-top: 1rem; } }
.sezione:last-child { border-bottom: 0; }
.sezione h2 { margin: 0; font-family: var(--serif); font-weight: 400; font-size: clamp(1.7rem, 3vw, 2.3rem); line-height: 1.1; letter-spacing: -.01em; }
.sezione h2 .num { display: block; margin-bottom: .6rem; font-family: var(--mono); font-size: .76rem; letter-spacing: .05em; color: var(--accento-testo); }
.sezione h2 .conta { margin-left: .6rem; color: var(--tenue); vertical-align: .35em; }
.sezione h3 { margin: 2rem 0 .25rem; color: var(--tenue); font-weight: 600; }
.sezione > p { margin: 1rem 0 0; max-width: 40rem; }
.vuoto, .nota { margin: 1rem 0 0; color: var(--tenue); }
.vuoto::before { content: "— "; }
ol.voci { list-style: none; margin: .75rem 0 0; padding: 0; }
.voce { display: flex; align-items: baseline; gap: .8rem; padding: .7rem 0; }
.voce .titolo a { font-family: var(--serif); font-size: 1.2rem; text-decoration: none; }
.voce .titolo a:hover { color: var(--accento-testo); text-decoration: underline; text-underline-offset: .18em; }
.voce .puntini { flex: 1 1 2rem; min-width: 2rem; border-bottom: 1px dotted var(--tenue); transform: translateY(-.35em); }
.voce .dettaglio { flex: none; color: var(--tenue); text-align: right; }
.freccia { display: inline-block; margin-top: 1.5rem; color: var(--inchiostro); text-decoration: none; border-bottom: 1px solid var(--inchiostro); padding-bottom: .15rem; }
.freccia::after { content: " →"; color: var(--accento-testo); }
.freccia:hover { color: var(--accento-testo); border-color: var(--accento-testo); }

ul.persone { list-style: none; margin: .75rem 0 0; padding: 0; }
.persona { display: flex; align-items: center; flex-wrap: wrap; gap: .5rem 1rem; padding: .8rem 0; border-top: 1px dotted var(--filetto); }
.persona:first-child { border-top: 0; }
.persona img, .persona .iniziali { width: 36px; height: 36px; border-radius: 50%; flex: none; }
.persona img { filter: grayscale(1); }
.persona:hover img { filter: none; }
.persona .iniziali { display: inline-grid; place-items: center; background: var(--inchiostro); color: var(--carta); font-family: var(--mono); font-size: .72rem; }
.persona .nome { font-family: var(--serif); font-size: 1.2rem; flex: 1 1 10rem; }
.persona .utente { color: var(--tenue); text-decoration: none; text-transform: none; }
.persona .utente:hover { color: var(--accento-testo); }
/* su schermi stretti l'utente va a capo, allineato al nome */
@media (max-width: 40rem) { .persona .utente { flex-basis: 100%; padding-left: calc(36px + 1rem); margin-top: -.4rem; } }
.ruolo { display: inline-block; padding: .22rem .55rem; border-radius: 2px; color: #fff; font-family: var(--mono); font-size: .64rem; letter-spacing: .08em; text-transform: uppercase; line-height: 1.2; white-space: nowrap; }
.r-responsabile { background: var(--accento); } .r-amministratore { background: #1d4ed8; } .r-analista { background: #047857; }
.r-progettista { background: #b45309; } .r-programmatore { background: #6d28d9; } .r-verificatore { background: #0e7490; }

.legenda { display: flex; flex-wrap: wrap; gap: .5rem 1.4rem; list-style: none; margin: 1.25rem 0 0; padding: 0; color: var(--tenue); }
.legenda i { display: inline-block; width: .7rem; height: .7rem; margin-right: .5rem; vertical-align: -.05rem; }
.linea { --colonna: 12rem; position: relative; margin-top: 1.5rem; }
.asse { position: relative; height: 2.6rem; margin-left: var(--colonna); color: var(--tenue); }
.asse span { position: absolute; bottom: 0; transform: translateX(-50%); white-space: nowrap; }
.asse span::before { content: ""; display: block; width: 1px; height: .45rem; margin: 0 auto .2rem; background: var(--filetto); }
.asse span.inizio { transform: none; } .asse span.inizio::before { margin-left: 0; }
.asse span.fine { transform: translateX(-100%); } .asse span.fine::before { margin-right: 0; }
.riga { display: grid; grid-template-columns: var(--colonna) 1fr; align-items: center; border-top: 1px dotted var(--filetto); }
.chi { font-family: var(--serif); font-size: 1.05rem; padding: .6rem .75rem .6rem 0; }
.traccia { position: relative; height: 2.4rem; }
.barra { position: absolute; top: .55rem; bottom: .55rem; display: flex; align-items: center; padding: 0 .5rem; border-radius: 2px; color: #fff;
         font-family: var(--mono); font-size: .62rem; letter-spacing: .08em; text-transform: uppercase; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.con-oggi .traccia::after { content: ""; position: absolute; top: 0; bottom: 0; left: var(--oggi); width: 0; border-left: 1px dashed var(--inchiostro); opacity: .75; }
.con-oggi .asse::after { content: "Oggi"; position: absolute; top: 0; left: var(--oggi); transform: translateX(-50%); color: var(--inchiostro); font-weight: 700; }
@media (max-width: 40rem) { .linea { --colonna: 0px; } .riga { grid-template-columns: 1fr; } .chi { padding: .6rem 0 0; } .asse span.mese { display: none; } }
.scorri { overflow-x: auto; }
table.periodi { width: 100%; border-collapse: collapse; margin-top: 1rem; }
.periodi th { text-align: left; padding: .5rem .5rem .5rem 0; color: var(--tenue); font-weight: 600; border-bottom: 1px solid var(--inchiostro); }
.periodi td { padding: .65rem .5rem .65rem 0; border-top: 1px dotted var(--filetto); vertical-align: middle; }
.periodi td:first-child { font-family: var(--serif); font-size: 1.05rem; white-space: nowrap; }
.periodi .data { color: var(--tenue); white-space: nowrap; }

.alfabeto { display: flex; flex-wrap: wrap; gap: .3rem; margin: 0; padding: 0 0 1rem; list-style: none; border-bottom: 1px solid var(--filetto); }
.alfabeto a { display: inline-grid; place-items: center; min-width: 2rem; height: 2rem; text-decoration: none; color: var(--tenue); }
.alfabeto a:hover { color: var(--accento-testo); }
.lettera h2 { font-size: clamp(2.4rem, 5vw, 3.4rem); }
dl { margin: 1rem 0 0; }
dt { font-family: var(--serif); font-size: 1.2rem; margin-top: 1.1rem; }
dd { margin: .2rem 0 0; max-width: 42rem; }
dd .nota { display: block; margin-top: .25rem; }

footer { margin-top: 3rem; padding: 1.25rem 0 3rem; border-top: 1px solid var(--inchiostro); display: flex; justify-content: space-between; flex-wrap: wrap; gap: .5rem 2rem; color: var(--tenue); }
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

ICONE = {
    "sole": '<svg class="sole" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32 1.41 1.41M2 12h2m16 0h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>',
    "luna": '<svg class="luna" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>',
}

NUOVA_SCHEDA = '<span class="sr-only"> (si apre in una nuova scheda)</span>'


def e(testo):
    return html.escape(str(testo))


def link(href, testo):
    return f'<a href="{e(href)}" target="_blank" rel="noopener">{e(testo)}{NUOVA_SCHEDA}</a>'


def evidenzia_cifre(nome):
    """Le cifre del nome nel colore d'accento, come il 2 del logo."""
    return re.sub(r"(\d+)", r'<span class="accento">\1</span>', e(nome))


def voce(href, testo, meta="", nascosto=""):
    """Riga di un sommario: titolo, puntini guida e dettaglio (versione, data, PDF).

    `nascosto` completa il nome del link per chi usa uno screen reader quando più voci
    hanno lo stesso titolo visibile, per esempio " del 2026-10-14".
    """
    dettaglio = " · ".join(p for p in (meta, "PDF") if p)
    extra = f'<span class="sr-only">{e(nascosto)}</span>' if nascosto else ""
    collegamento = f'<a href="{e(href)}" target="_blank" rel="noopener">{e(testo)}{extra}{NUOVA_SCHEDA}</a>'
    return (f'<span class="titolo">{collegamento}</span><span class="puntini" aria-hidden="true"></span>'
            f'<span class="dettaglio">{e(dettaglio)}</span>')


def elenco(voci, vuoto):
    if not voci:
        return f'<p class="vuoto">{e(vuoto)}</p>'
    return '<ol class="voci">' + "".join(f'<li class="voce">{v}</li>' for v in voci) + "</ol>"


def sezione(identificatore, numero, titolo, contenuto, conta=None):
    badge = f'<span class="conta"><span class="sr-only">Elementi: </span>{e(conta)}</span>' if conta is not None else ""
    return (f'<section class="sezione" id="{e(identificatore)}" aria-labelledby="titolo-{e(identificatore)}">'
            f'<h2 id="titolo-{e(identificatore)}"><span class="num" aria-hidden="true">{e(numero)}</span>{e(titolo)}{badge}</h2>'
            f"{contenuto}</section>")


def indice(sezioni, pagine=()):
    """Indice laterale: sezioni numerate della pagina e link alle altre pagine."""
    voci = "".join(f'<li><a href="{e(href)}"><span class="n">{e(numero)}</span><span>{e(testo)}</span></a></li>' for href, numero, testo in sezioni)
    altre = "".join(f'<li><a href="{e(href)}">{e(testo)}</a></li>' for href, testo in pagine)
    altre = f'<ul class="pagine">{altre}</ul>' if altre else ""
    return f'<nav class="indice" aria-label="Sezioni"><ol>{voci}</ol>{altre}</nav>'


def apertura(titolo_html, kicker, sotto="", meta=(), compatta=False):
    classe = "apertura compatta" if compatta else "apertura"
    testo_sotto = f'<p class="sotto">{e(sotto)}</p>' if sotto else ""
    testo_meta = f'<ul class="meta">{"".join(f"<li>{m}</li>" for m in meta)}</ul>' if meta else ""
    return f'<section class="{classe}"><p class="kicker">{e(kicker)}</p><h1 class="titolone">{titolo_html}</h1>{testo_sotto}{testo_meta}</section>'


def pagina(titolo, testata, corpo, gruppo, logo, accento, dati=None, laterale=""):
    info = gruppo.get("gruppo", {})
    nome = info.get("nome") or "Documentazione di progetto"
    icona = f'<link rel="icon" type="image/png" href="{e(logo)}">' if logo else ""
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
    return f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#faf9f6">
<title>{e(titolo)}</title>
{icona}
<script>{SCRIPT_TESTA}</script>
<style>{stile}</style>
</head>
<body>
<a class="salta" href="#contenuto">Vai al contenuto</a>
<div class="pagina">
<header class="testa"><a class="marchio" href="index.html">{immagine}<span class="mono"><b>{e(nome)}</b><span class="sep">·</span><span class="sotto-marchio">Documentazione di progetto</span></span></a>{bottone}</header>
<main id="contenuto" tabindex="-1">
{testata}
{colonne}
</main>
<footer class="mono"><span>{e(nome)} · Università degli Studi di Padova</span><span>Sito generato dai sorgenti del repository{repo}</span></footer>
</div>
<script>{SCRIPT_TEMA}</script>
{script_dati}
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
        rilasciati.append((data, titolo, voce(pdf, titolo, f"v{versione} · {data}")))
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
            compila(typst, RADICE / "modello/verbale.typ", out / (nome.replace(" ", "_") + ".pdf"),
                    dati=f"/documenti/verbali/{cartella}/{sorgente.name}")
            # due verbali dello stesso giorno si distinguono per il suffisso: "2026-10-20 C7"
            quando = f"{parti[0]} {parti[1].upper()}".strip()
            voci.append(voce(nome.replace(" ", "_") + ".pdf", f"Verbale {tipo}", quando, nascosto=f" del {quando}"))
    return voci


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


def linea_del_tempo(periodi, nomi):
    """Barre per membro su una scala comune; l'ultimo giorno di ogni periodo è incluso."""
    giorno = datetime.date.fromisoformat
    un_giorno = datetime.timedelta(days=1)
    inizio = min(giorno(p["inizio"]) for p in periodi)
    fine = max(giorno(p["fine"]) for p in periodi) + un_giorno
    totale = max((fine - inizio).days, 1)

    def pos(d):
        # percentuale con al più due decimali, senza ".0" finale
        return float(f"{(d - inizio).days / totale * 100:.2f}")

    def pct(x):
        return f"{x:g}"

    tacche = [f'<span class="inizio" style="left:0%">{inizio.isoformat()}</span>']
    mese = inizio.replace(day=1)
    while True:
        mese = (mese.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
        if mese >= fine:
            break
        # niente mesi troppo vicini alle date di inizio e fine: le etichette si sovrapporrebbero
        if 12 < pos(mese) < 88:
            tacche.append(f'<span class="mese" style="left:{pct(pos(mese))}%">{MESI[mese.month - 1]} {mese.year}</span>')
    tacche.append(f'<span class="fine" style="left:100%">{(fine - un_giorno).isoformat()}</span>')

    righe = []
    for nome in nomi:
        barre = []
        for p in periodi:
            if p["membro"] != nome:
                continue
            a, b = pos(giorno(p["inizio"])), pos(giorno(p["fine"]) + un_giorno)
            barre.append(f'<span class="barra r-{e(slug(p["ruolo"]))}" style="left:{pct(a)}%;width:{pct(round(b - a, 2))}%" '
                         f'title="{e(p["ruolo"])} dal {p["inizio"]} al {p["fine"]}">{e(p["ruolo"])}</span>')
        righe.append(f'<div class="riga"><div class="chi">{e(nome)}</div><div class="traccia">{"".join(barre)}</div></div>')
    return (f'<div class="linea" aria-hidden="true" data-inizio="{inizio.isoformat()}" data-fine="{fine.isoformat()}">'
            f'<div class="asse">{"".join(tacche)}</div>{"".join(righe)}</div>')


def tabella_periodi(periodi):
    righe = "".join(f'<tr><td>{e(p["membro"])}</td><td><span class="ruolo r-{e(slug(p["ruolo"]))}">{e(p["ruolo"])}</span></td>'
                    f'<td class="data">{e(p["inizio"])}</td><td class="data">{e(p["fine"])}</td></tr>' for p in periodi)
    # la regione scorrevole deve essere raggiungibile da tastiera
    return ('<div class="scorri" role="region" aria-label="Tabella dei periodi" tabindex="0">'
            '<table class="periodi"><thead><tr><th scope="col">Membro</th><th scope="col">Ruolo</th>'
            f'<th scope="col">Dal</th><th scope="col">Al</th></tr></thead><tbody>{righe}</tbody></table></div>')


def pagina_indice(gruppo, typst, out, logo, accento, periodi):
    info, progetto = gruppo.get("gruppo", {}), gruppo.get("progetto", {})
    nome = info.get("nome") or "Documentazione di progetto"

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
    meta.append(f"Aggiornato il {datetime.date.today().isoformat()}")
    testata = apertura(evidenzia_cifre(nome), "Documentazione di progetto", SOTTOTITOLO, meta)

    voci_lettere = lettere(typst, out)
    gestionali = documenti(typst, out, "documenti/esterni/gestionali")
    tecnici = documenti(typst, out, "documenti/esterni/tecnici")
    interni = documenti(typst, out, "documenti/interni")
    verbali_esterni = verbali(typst, out, "esterni")
    verbali_interni = verbali(typst, out, "interni")
    membri = [persona(m, con_ruolo=True) for m in gruppo.get("membro", [])]

    nessuno = "Nessun documento ancora pubblicato"
    nessun_verbale = "Nessun verbale ancora pubblicato"
    gruppo_html = (f'<p class="nota" id="nota-attuali">Ruoli in carica alla data di oggi.</p><ul class="persone">{"".join(membri)}</ul>'
                   '<a class="freccia" href="ruoli.html">Ruoli e rotazione nel tempo</a>'
                   if membri else '<p class="vuoto">Membri non ancora indicati</p>')
    corpo = [
        sezione("lettere", "01", "Lettere di presentazione", elenco(voci_lettere, "Nessuna lettera ancora pubblicata"), len(voci_lettere)),
        sezione("documenti", "02", "Documenti esterni",
                "<h3>Gestionali</h3>" + elenco(gestionali, nessuno) + "<h3>Tecnici</h3>" + elenco(tecnici, nessuno),
                len(gestionali) + len(tecnici)),
        sezione("interni", "03", "Documenti interni", elenco(interni, nessuno), len(interni)),
        sezione("verbali", "04", "Verbali",
                "<h3>Esterni</h3>" + elenco(verbali_esterni, nessun_verbale) + "<h3>Interni</h3>" + elenco(verbali_interni, nessun_verbale),
                len(verbali_esterni) + len(verbali_interni)),
        sezione("gruppo", "05", "Il gruppo", gruppo_html, len(membri)),
    ]
    laterale = indice([("#lettere", "01", "Lettere"), ("#documenti", "02", "Documenti esterni"), ("#interni", "03", "Documenti interni"),
                       ("#verbali", "04", "Verbali"), ("#gruppo", "05", "Il gruppo")],
                      [("glossario.html", "Glossario"), ("ruoli.html", "Ruoli")])
    return pagina(nome, testata, "\n".join(corpo), gruppo, logo, accento, dati={"periodi": periodi}, laterale=laterale)


def pagina_ruoli(gruppo, logo, accento, periodi):
    info = gruppo.get("gruppo", {})
    nome = info.get("nome") or "Documentazione di progetto"
    membri = gruppo.get("membro", [])
    nomi = [nome_membro(m) for m in membri]
    nomi += sorted({p["membro"] for p in periodi} - set(nomi))
    meta = ['<a href="index.html">Indice</a>']
    if info.get("repo"):
        meta.append(link(info["repo"].rstrip("/") + "/blob/main/documenti/interni/ruoli.md", "Regole di rotazione"))
    testata = apertura(e("Ruoli"), nome, "Chi ricopre quale ruolo, oggi e nel tempo.", meta, compatta=True)

    attuali = [persona(m, con_ruolo=True) for m in membri]
    presenti = [r for r in RUOLI if any(p["ruolo"] == r for p in periodi)]
    legenda = '<ul class="legenda">' + "".join(f'<li><i class="r-{e(slug(r))}" aria-hidden="true"></i>{e(r)}</li>' for r in presenti) + "</ul>"
    corpo = [sezione("attuali", "01", "Ruoli attuali",
                     '<p class="nota" id="nota-attuali">Ruoli in carica alla data di oggi.</p>'
                     + (f'<ul class="persone">{"".join(attuali)}</ul>' if attuali else '<p class="vuoto">Membri non ancora indicati</p>'))]
    voci_indice = [("#attuali", "01", "Ruoli attuali")]
    if periodi:
        corpo += [sezione("linea", "02", "Linea del tempo", legenda + linea_del_tempo(periodi, nomi)),
                  sezione("periodi", "03", "Periodi", tabella_periodi(periodi)
                          + '<p class="nota">I periodi futuri compaiono quando il gruppo li conferma in dati/ruoli.csv.</p>', len(periodi))]
        voci_indice += [("#linea", "02", "Linea del tempo"), ("#periodi", "03", "Periodi")]
    else:
        corpo.append(sezione("periodi", "02", "Periodi", '<p class="vuoto">Nessun periodo ancora registrato in dati/ruoli.csv</p>', 0))
        voci_indice.append(("#periodi", "02", "Periodi"))
    laterale = indice(voci_indice, [("index.html", "Indice"), ("glossario.html", "Glossario")])
    return pagina(f"Ruoli - {nome}", testata, "\n".join(corpo), gruppo, logo, accento, dati={"periodi": periodi}, laterale=laterale)


def senza_accenti(testo):
    return "".join(c for c in unicodedata.normalize("NFD", testo) if not unicodedata.combining(c)).casefold()


def pagina_glossario(gruppo, voci, logo, accento):
    nome = gruppo.get("gruppo", {}).get("nome") or "Documentazione di progetto"
    per_iniziale = {}
    for voce_ in sorted(voci, key=lambda v: senza_accenti(v["termine"])):
        iniziale = senza_accenti(voce_["termine"])[:1].upper()
        per_iniziale.setdefault(iniziale if iniziale.isalpha() else "#", []).append(voce_)

    testata = apertura(e("Glossario"), nome, "I termini del progetto, con definizioni e sinonimi, come sono usati nei documenti.",
                       ['<a href="index.html">Indice</a>', f"{len(voci)} voci"], compatta=True)
    corpo = []
    if per_iniziale:
        for numero, (iniziale, gruppo_voci) in enumerate(per_iniziale.items(), start=1):
            righe = []
            for voce_ in gruppo_voci:
                sinonimi = voce_.get("sinonimi", [])
                ancore = "".join(f'<span id="{e(slug(s))}"></span>' for s in sinonimi)
                nota = f'<span class="nota">Sinonimi: {e(", ".join(sinonimi))}</span>' if sinonimi else ""
                righe.append(f'<dt id="{e(slug(voce_["termine"]))}">{ancore}{e(voce_["termine"])}</dt>'
                             f"<dd>{e(voce_['definizione'])}{nota}</dd>")
            blocco = sezione(slug(iniziale) or "altro", f"{numero:02d}", iniziale, "<dl>" + "".join(righe) + "</dl>", len(gruppo_voci))
            corpo.append(blocco.replace('class="sezione"', 'class="sezione lettera"', 1))
        alfabeto = "".join(f'<li><a href="#{e(slug(i)) or "altro"}">{e(i)}</a></li>' for i in per_iniziale)
        laterale = (f'<nav class="indice" aria-label="Iniziali"><ul class="alfabeto">{alfabeto}</ul>'
                    '<ul class="pagine"><li><a href="index.html">Indice</a></li><li><a href="ruoli.html">Ruoli</a></li></ul></nav>')
    else:
        corpo.append(sezione("vuoto", "01", "Nessuna voce", '<p class="vuoto">Nessuna voce ancora presente</p>'))
        laterale = indice([("#vuoto", "01", "Glossario")], [("index.html", "Indice"), ("ruoli.html", "Ruoli")])
    return pagina(f"Glossario - {nome}", testata, "\n".join(corpo), gruppo, logo, accento, laterale=laterale)


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
    (out / "index.html").write_text(pagina_indice(gruppo, typst, out, logo, accento, periodi), encoding="utf-8")
    (out / "glossario.html").write_text(pagina_glossario(gruppo, voci, logo, accento), encoding="utf-8")
    (out / "ruoli.html").write_text(pagina_ruoli(gruppo, logo, accento, periodi), encoding="utf-8")
    print(f"sito generato in {out}: {len(list(out.glob('*.pdf')))} PDF")


if __name__ == "__main__":
    main()
