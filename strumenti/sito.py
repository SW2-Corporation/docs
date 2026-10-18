"""Compila con typst i documenti pubblicabili e genera il sito statico.

Uso: python strumenti/sito.py --out site [--typst percorso]

Vanno sul sito i documenti rilasciati (prima riga del registro = approvazione),
tutte le lettere e tutti i verbali, più la pagina del glossario.
"""

import argparse
import html
import re
import shutil
import subprocess
import sys
import tomllib
import unicodedata
from pathlib import Path

from verifica import RADICE, data_iso, rilascio, slug

ACCENTO_PREDEFINITO = "#d7262f"
SOTTOTITOLO = "Progetto didattico di Ingegneria del Software, Università degli Studi di Padova"

# Tema scuro: usato sia quando il dispositivo lo preferisce sia quando l'utente lo sceglie.
TEMA_SCURO = """--sfondo: #0e0e10; --carta: #18181c; --testo: #f1f1f3; --muto: #9b9ba4; --bordo: #2a2a31;
  --accento-testo: var(--accento-chiaro); --ombra: 0 1px 2px rgba(0,0,0,.4); --sole: block; --luna: none; color-scheme: dark;"""

# {accento} e {scuro} vengono sostituiti dal colore del gruppo e dal blocco del tema scuro.
# --accento-testo è la variante dell'accento usata per il testo: sugli sfondi scuri è schiarita
# per tenere il contrasto sopra 4,5:1.
STILE = """
:root { --accento: {accento}; --accento-chiaro: #f0545b; --accento-chiaro: color-mix(in srgb, var(--accento) 72%, white);
        --accento-testo: var(--accento); --sfondo: #f5f5f7; --carta: #ffffff; --testo: #151517; --muto: #6b6b74;
        --bordo: #e3e3e8; --scuro: #0e0e10; --chiaro: #f4f4f6; --ombra: 0 1px 2px rgba(0,0,0,.05);
        --sole: none; --luna: block; color-scheme: light; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { {scuro} } }
:root[data-theme="dark"] { {scuro} }
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
body { margin: 0; font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
       background: var(--sfondo); color: var(--testo); line-height: 1.55; -webkit-font-smoothing: antialiased; }
a { color: inherit; }
:focus-visible { outline: 3px solid var(--accento-testo); outline-offset: 3px; border-radius: 4px; }
.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; border: 0; }
.salta { position: absolute; left: 1rem; top: -4rem; z-index: 10; padding: .6rem 1rem; border-radius: 8px;
         background: var(--carta); color: var(--testo); font-weight: 700; text-decoration: none; box-shadow: 0 4px 16px rgba(0,0,0,.3); }
.salta:focus { top: 1rem; }
.dentro { max-width: 68rem; margin: 0 auto; padding: 0 1.25rem; }

.hero { position: relative; background: var(--scuro); color: var(--chiaro); border-bottom: 4px solid var(--accento); --accento-testo: var(--accento-chiaro); }
.hero > .dentro { display: flex; align-items: center; gap: 2rem; padding-top: 3rem; padding-bottom: 2.25rem; flex-wrap: wrap; }
.hero.compatto > .dentro { padding-top: 1.75rem; padding-bottom: 1.5rem; gap: 1.25rem; }
.logo { width: 128px; height: 128px; border-radius: 50%; box-shadow: 0 12px 36px rgba(0,0,0,.5); flex: none; }
.hero.compatto .logo { width: 64px; height: 64px; }
.sopra { margin: 0 0 .35rem; font-size: .78rem; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; color: var(--accento-testo); }
.hero h1 { margin: 0; font-size: clamp(2rem, 4.5vw, 3rem); letter-spacing: -.02em; line-height: 1.1; }
.hero.compatto h1 { font-size: clamp(1.5rem, 3vw, 2rem); }
.hero p.sotto { margin: .5rem 0 0; color: #c7c7cf; font-size: 1.05rem; max-width: 40rem; }
.chips { display: flex; flex-wrap: wrap; gap: .5rem; margin-top: 1.1rem; }
.chip { display: inline-flex; align-items: center; gap: .45rem; min-height: 2.25rem; padding: .4rem .85rem; border-radius: 999px;
        border: 1px solid rgba(255,255,255,.18); background: rgba(255,255,255,.05); color: #ececf0;
        font-size: .86rem; font-weight: 500; text-decoration: none; }
a.chip:hover { border-color: var(--accento-chiaro); background: rgba(255,255,255,.09); }
.chip svg { width: 15px; height: 15px; color: var(--accento-testo); }
.tema { position: absolute; top: 1rem; right: 1.25rem; width: 2.75rem; height: 2.75rem; display: grid; place-items: center;
        border-radius: 50%; border: 1px solid rgba(255,255,255,.18); background: rgba(255,255,255,.05); color: #ececf0; cursor: pointer; }
.tema:hover { border-color: var(--accento-chiaro); background: rgba(255,255,255,.09); }
.tema svg { width: 20px; height: 20px; }
.tema .sole { display: var(--sole); }
.tema .luna { display: var(--luna); }
.menu { background: var(--scuro); border-top: 1px solid rgba(255,255,255,.08); --accento-testo: var(--accento-chiaro); }
.menu .dentro { display: flex; gap: 1.75rem; overflow-x: auto; scrollbar-width: none; }
.menu .dentro::-webkit-scrollbar { display: none; }
.menu a { padding: .85rem 0; color: #c7c7cf; font-size: .9rem; font-weight: 600; text-decoration: none;
          border-bottom: 3px solid transparent; margin-bottom: -4px; white-space: nowrap; }
.menu a:hover { color: #fff; border-color: var(--accento); }
.menu a:focus-visible { outline-offset: -3px; }

main.dentro { padding-top: 2rem; padding-bottom: 3rem; }
.griglia { display: grid; grid-template-columns: 1fr; gap: 1.25rem; }
@media (min-width: 46rem) { .griglia { grid-template-columns: 1fr 1fr; } }
.scheda { position: relative; overflow: hidden; background: var(--carta); border: 1px solid var(--bordo);
          border-radius: 14px; padding: 1.35rem 1.5rem 1.5rem; box-shadow: var(--ombra); }
.scheda::before { content: ""; position: absolute; inset: 0 auto 0 0; width: 4px; background: var(--accento); }
.larga { grid-column: 1 / -1; }
.scheda h2 { margin: 0; font-size: 1.2rem; display: flex; justify-content: space-between; align-items: baseline; gap: .75rem; }
.scheda h3 { margin: 1.1rem 0 .3rem; font-size: .76rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--muto); }
.scheda > p { margin: .6rem 0 0; }
.conta { font-size: .78rem; font-weight: 700; color: var(--muto); background: var(--sfondo); border: 1px solid var(--bordo);
         border-radius: 999px; padding: .1rem .65rem; white-space: nowrap; }
.due { display: grid; grid-template-columns: repeat(auto-fit, minmax(17rem, 1fr)); gap: 0 2rem; }
ul.voci { list-style: none; margin: .4rem 0 0; padding: 0; }
ul.voci li { display: flex; justify-content: space-between; align-items: baseline; gap: 1rem; padding: .55rem 0; border-top: 1px solid var(--bordo); }
ul.voci li:first-child { border-top: 0; }
ul.voci a { font-weight: 600; text-decoration: none; }
ul.voci a:hover { color: var(--accento-testo); text-decoration: underline; }
.meta { color: var(--muto); font-size: .82rem; white-space: nowrap; }
.pdf { display: inline-block; vertical-align: middle; margin-left: .45rem; padding: 0 .35rem; border: 1.5px solid var(--accento-testo);
       border-radius: 4px; color: var(--accento-testo); font-size: .7rem; font-weight: 800; letter-spacing: .06em; line-height: 1.35; }
.nota { color: var(--muto); margin: .6rem 0 0; font-size: .95rem; }
.pulsante { display: inline-flex; align-items: center; gap: .5rem; margin-top: 1rem; min-height: 2.75rem; padding: .6rem 1.1rem; border-radius: 10px;
            background: var(--accento); color: #fff; font-weight: 700; text-decoration: none; }
.pulsante:hover { filter: brightness(1.08); }
.persone { display: flex; flex-wrap: wrap; gap: .6rem; margin-top: .9rem; }
.persona { display: inline-flex; align-items: center; gap: .6rem; padding: .3rem .95rem .3rem .3rem; border-radius: 999px;
           border: 1px solid var(--bordo); background: var(--sfondo); font-weight: 600; font-size: .92rem; text-decoration: none; }
a.persona:hover { border-color: var(--accento-testo); }
.persona img, .persona .iniziali { width: 32px; height: 32px; border-radius: 50%; flex: none; }
.persona .iniziali { display: inline-grid; place-items: center; background: var(--accento); color: #fff; font-size: .78rem; font-weight: 800; }

.alfabeto { display: flex; flex-wrap: wrap; gap: .35rem; margin: .9rem 0 .4rem; }
.alfabeto a { min-width: 2.25rem; height: 2.25rem; display: inline-grid; place-items: center; border-radius: 8px; border: 1px solid var(--bordo);
              font-weight: 700; font-size: .85rem; text-decoration: none; }
.alfabeto a:hover { border-color: var(--accento-testo); color: var(--accento-testo); }
dl { margin: 0; }
dt { font-weight: 700; margin-top: .9rem; }
dd { margin: .15rem 0 0; color: var(--testo); }
dd .nota { display: block; margin-top: .15rem; }

footer { border-top: 1px solid var(--bordo); color: var(--muto); font-size: .85rem; }
footer .dentro { display: flex; justify-content: space-between; flex-wrap: wrap; gap: .5rem 1.5rem; padding-top: 1.25rem; padding-bottom: 1.5rem; }
footer a { color: inherit; }
"""

# Applica subito il tema salvato, prima del rendering, per evitare lo sfarfallio.
SCRIPT_TESTA = """(function(){try{var t=localStorage.getItem('tema');if(t==='light'||t==='dark'){document.documentElement.setAttribute('data-theme',t);}}catch(e){}})();"""

SCRIPT_TEMA = """(function(){
var b=document.querySelector('.tema');if(!b)return;
var mq=window.matchMedia('(prefers-color-scheme: dark)');
function attuale(){return document.documentElement.getAttribute('data-theme')||(mq.matches?'dark':'light');}
function aggiorna(){var scuro=attuale()==='dark';b.setAttribute('aria-pressed',scuro?'true':'false');
b.setAttribute('aria-label',scuro?'Passa al tema chiaro':'Passa al tema scuro');b.title=b.getAttribute('aria-label');}
b.addEventListener('click',function(){var nuovo=attuale()==='dark'?'light':'dark';
document.documentElement.setAttribute('data-theme',nuovo);try{localStorage.setItem('tema',nuovo);}catch(e){}aggiorna();});
if(mq.addEventListener){mq.addEventListener('change',aggiorna);}
aggiorna();})();"""

ICONE = {
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>',
    "repo": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="m8 6-6 6 6 6M16 6l6 6-6 6"/></svg>',
    "capitolato": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 12h18"/></svg>',
    "indietro": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M19 12H5m7-7-7 7 7 7"/></svg>',
    "sole": '<svg class="sole" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32 1.41 1.41M2 12h2m16 0h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>',
    "luna": '<svg class="luna" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>',
}

NUOVA_SCHEDA = '<span class="sr-only"> (si apre in una nuova scheda)</span>'


def e(testo):
    return html.escape(str(testo))


def link(href, testo):
    return f'<a href="{e(href)}" target="_blank" rel="noopener">{e(testo)}{NUOVA_SCHEDA}</a>'


def voce(href, testo, meta=""):
    """Riga di un elenco: link al PDF, etichetta PDF e dettaglio a destra."""
    dettaglio = f'<span class="meta">{e(meta)}</span>' if meta else ""
    return f'{link(href, testo)}<span class="pdf" aria-hidden="true">PDF</span>{dettaglio}'


def elenco(voci, vuoto):
    if not voci:
        return f'<p class="nota">{e(vuoto)}</p>'
    return '<ul class="voci">' + "".join(f"<li>{v}</li>" for v in voci) + "</ul>"


def chip(testo, icona, href=None):
    dentro = f'{ICONE[icona]}<span>{e(testo)}</span>'
    if href:
        esterno = href.startswith(("http://", "https://"))
        attributi = ' target="_blank" rel="noopener"' if esterno else ""
        return f'<a class="chip" href="{e(href)}"{attributi}>{dentro}{NUOVA_SCHEDA if esterno else ""}</a>'
    return f'<span class="chip">{dentro}</span>'


def scheda(identificatore, titolo, contenuto, conta=None, larga=False):
    badge = f'<span class="conta"><span class="sr-only">Elementi: </span>{e(conta)}</span>' if conta is not None else ""
    classe = "scheda larga" if larga else "scheda"
    return (f'<section class="{classe}" id="{e(identificatore)}" aria-labelledby="titolo-{e(identificatore)}">'
            f'<h2 id="titolo-{e(identificatore)}">{e(titolo)}{badge}</h2>{contenuto}</section>')


def intestazione(titolo, sottotitolo, logo, chips=(), menu=(), compatto=False, sopra="Documentazione di progetto"):
    immagine = f'<img class="logo" src="{e(logo)}" alt="">' if logo else ""
    testo_chips = f'<div class="chips">{"".join(chips)}</div>' if chips else ""
    voci_menu = "".join(f'<a href="{e(href)}">{e(testo)}</a>' for href, testo in menu)
    testo_menu = f'<nav class="menu" aria-label="Sezioni"><div class="dentro">{voci_menu}</div></nav>' if menu else ""
    classe = "hero compatto" if compatto else "hero"
    bottone = (f'<button class="tema" type="button" aria-pressed="false" aria-label="Passa al tema scuro">'
               f'{ICONE["sole"]}{ICONE["luna"]}</button>')
    return (f'<header class="{classe}">{bottone}<div class="dentro">{immagine}<div>'
            f'<p class="sopra">{e(sopra)}</p><h1>{e(titolo)}</h1><p class="sotto">{e(sottotitolo)}</p>{testo_chips}'
            f"</div></div>{testo_menu}</header>")


def pagina(titolo, testata, corpo, gruppo, logo, accento):
    info = gruppo.get("gruppo", {})
    nome = info.get("nome") or "Documentazione di progetto"
    icona = f'<link rel="icon" type="image/png" href="{e(logo)}">' if logo else ""
    repo = f' · {link(info["repo"], "Sorgenti su GitHub")}' if info.get("repo") else ""
    stile = STILE.replace("{accento}", accento).replace("{scuro}", TEMA_SCURO)
    return f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#0e0e10">
<title>{e(titolo)}</title>
{icona}
<script>{SCRIPT_TESTA}</script>
<style>{stile}</style>
</head>
<body>
<a class="salta" href="#contenuto">Vai al contenuto</a>
{testata}
<main class="dentro" id="contenuto" tabindex="-1">
{corpo}
</main>
<footer><div class="dentro"><span>{e(nome)} · Università degli Studi di Padova</span><span>Sito generato dai sorgenti del repository{repo}</span></div></footer>
<script>{SCRIPT_TEMA}</script>
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
            voci.append(voce(nome.replace(" ", "_") + ".pdf", f"Lettera di Presentazione del {sorgente.stem}"))
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
        if data_iso(sorgente.stem):
            nome = f"Verbale {tipo} {sorgente.stem}"
            compila(typst, RADICE / "modello/verbale.typ", out / (nome.replace(" ", "_") + ".pdf"),
                    dati=f"/documenti/verbali/{cartella}/{sorgente.name}")
            voci.append(voce(nome.replace(" ", "_") + ".pdf", f"Verbale {tipo} del {sorgente.stem}"))
    return voci


def persona(membro):
    nome = f"{membro.get('nome', '')} {membro.get('cognome', '')}".strip()
    utente = membro.get("github")
    if utente:
        return (f'<a class="persona" href="https://github.com/{e(utente)}" target="_blank" rel="noopener">'
                f'<img src="https://github.com/{e(utente)}.png?size=64" alt="" loading="lazy">{e(nome)}{NUOVA_SCHEDA}</a>')
    iniziali = "".join(parte[0] for parte in nome.split()[:2]).upper()
    return f'<span class="persona"><span class="iniziali" aria-hidden="true">{e(iniziali)}</span>{e(nome)}</span>'


def indice(gruppo, typst, out, logo, accento):
    info, progetto = gruppo.get("gruppo", {}), gruppo.get("progetto", {})
    nome = info.get("nome") or "Documentazione di progetto"

    chips = []
    if progetto.get("capitolato"):
        testo = f"Capitolato {progetto['capitolato']}"
        if progetto.get("proponente"):
            testo += f" · {progetto['proponente']}"
        chips.append(chip(testo, "capitolato"))
    if info.get("email"):
        chips.append(chip(info["email"], "mail", "mailto:" + info["email"]))
    if info.get("repo"):
        chips.append(chip("Repository", "repo", info["repo"]))
    menu = [("#lettere", "Lettere"), ("#documenti", "Documenti"), ("#verbali", "Verbali"),
            ("glossario.html", "Glossario"), ("#gruppo", "Il gruppo")]
    testata = intestazione(nome, SOTTOTITOLO, logo, chips, menu)

    voci_lettere = lettere(typst, out)
    gestionali = documenti(typst, out, "documenti/esterni/gestionali")
    tecnici = documenti(typst, out, "documenti/esterni/tecnici")
    interni = documenti(typst, out, "documenti/interni")
    verbali_esterni = verbali(typst, out, "esterni")
    verbali_interni = verbali(typst, out, "interni")
    membri = [persona(m) for m in gruppo.get("membro", [])]

    nessuno = "Nessun documento ancora pubblicato."
    nessun_verbale = "Nessun verbale ancora pubblicato."
    corpo = ['<div class="griglia">',
             scheda("lettere", "Lettere di presentazione",
                    elenco(voci_lettere, "Nessuna lettera ancora pubblicata."), len(voci_lettere), larga=True),
             scheda("documenti", "Documenti esterni",
                    "<h3>Gestionali</h3>" + elenco(gestionali, nessuno) + "<h3>Tecnici</h3>" + elenco(tecnici, nessuno),
                    len(gestionali) + len(tecnici)),
             scheda("interni", "Documenti interni", elenco(interni, nessuno), len(interni)),
             scheda("verbali", "Verbali",
                    '<div class="due"><div><h3>Esterni</h3>' + elenco(verbali_esterni, nessun_verbale)
                    + "</div><div><h3>Interni</h3>" + elenco(verbali_interni, nessun_verbale) + "</div></div>",
                    len(verbali_esterni) + len(verbali_interni), larga=True),
             scheda("glossario", "Glossario",
                    "<p>I termini del progetto, con definizioni e sinonimi, come sono usati nei documenti.</p>"
                    '<a class="pulsante" href="glossario.html">Apri il glossario</a>'),
             scheda("gruppo", "Il gruppo",
                    f'<div class="persone">{"".join(membri)}</div>' if membri else '<p class="nota">Membri non ancora indicati.</p>',
                    len(membri)),
             "</div>"]
    return pagina(nome, testata, "\n".join(corpo), gruppo, logo, accento)


def senza_accenti(testo):
    return "".join(c for c in unicodedata.normalize("NFD", testo) if not unicodedata.combining(c)).casefold()


def glossario(gruppo, voci, logo, accento):
    nome = gruppo.get("gruppo", {}).get("nome") or "Documentazione di progetto"
    per_iniziale = {}
    for voce_ in sorted(voci, key=lambda v: senza_accenti(v["termine"])):
        iniziale = senza_accenti(voce_["termine"])[:1].upper()
        per_iniziale.setdefault(iniziale if iniziale.isalpha() else "#", []).append(voce_)

    testata = intestazione("Glossario", SOTTOTITOLO, logo, [chip("Torna all'indice", "indietro", "index.html")],
                           compatto=True, sopra=nome)
    corpo = []
    if per_iniziale:
        alfabeto = "".join(f'<a href="#{e(slug(i)) or "altro"}">{e(i)}</a>' for i in per_iniziale)
        corpo.append(f'<nav class="alfabeto" aria-label="Iniziali">{alfabeto}</nav>')
        for iniziale, gruppo_voci in per_iniziale.items():
            righe = []
            for voce_ in gruppo_voci:
                sinonimi = voce_.get("sinonimi", [])
                ancore = "".join(f'<span id="{e(slug(s))}"></span>' for s in sinonimi)
                nota = f'<span class="nota">Sinonimi: {e(", ".join(sinonimi))}</span>' if sinonimi else ""
                righe.append(f'<dt id="{e(slug(voce_["termine"]))}">{ancore}{e(voce_["termine"])}</dt>'
                             f"<dd>{e(voce_['definizione'])}{nota}</dd>")
            corpo.append(scheda(slug(iniziale) or "altro", iniziale, "<dl>" + "".join(righe) + "</dl>", len(gruppo_voci), larga=True))
    else:
        corpo.append(scheda("vuoto", "Glossario", '<p class="nota">Nessuna voce ancora presente.</p>', 0, larga=True))
    return pagina(f"Glossario - {nome}", testata, '<div class="griglia">' + "\n".join(corpo) + "</div>", gruppo, logo, accento)


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
    info = gruppo.get("gruppo", {})
    accento = info.get("colore") or ACCENTO_PREDEFINITO
    logo = None
    if info.get("logo") and (RADICE / info["logo"]).is_file():
        logo = "logo" + Path(info["logo"]).suffix.lower()
        shutil.copy(RADICE / info["logo"], out / logo)
    (out / "index.html").write_text(indice(gruppo, typst, out, logo, accento), encoding="utf-8")
    (out / "glossario.html").write_text(glossario(gruppo, voci, logo, accento), encoding="utf-8")
    print(f"sito generato in {out}: {len(list(out.glob('*.pdf')))} PDF")


if __name__ == "__main__":
    main()
