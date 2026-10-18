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

STILE = """
body { font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; max-width: 46rem;
       margin: 0 auto; padding: 1.5rem 1rem; line-height: 1.5; color: #1d1d1f; background: #fff; }
h1, h2, h3 { color: #1f3d6b; line-height: 1.25; }
h1 { font-size: 1.8rem; margin-bottom: 0.25rem; }
h2 { font-size: 1.3rem; margin-top: 2rem; padding-bottom: 0.25rem; border-bottom: 1px solid #d0d7e2; }
h3 { font-size: 1.05rem; margin-bottom: 0.25rem; }
a { color: #1f3d6b; }
ul { padding-left: 1.2rem; }
li { margin: 0.3rem 0; }
.nota { color: #666; }
dt { font-weight: 600; margin-top: 0.9rem; }
dd { margin: 0.2rem 0 0 0; }
"""


def e(testo):
    return html.escape(str(testo))


def link(href, testo):
    return f'<a href="{e(href)}" target="_blank" rel="noopener">{e(testo)}</a>'


def elenco(voci, vuoto):
    if not voci:
        return f'<p class="nota">{vuoto}</p>'
    return "<ul>\n" + "\n".join(f"<li>{v}</li>" for v in voci) + "\n</ul>"


def pagina(titolo, corpo):
    return f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titolo)}</title>
<style>{STILE}</style>
</head>
<body>
{corpo}
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
            voci.append(link(nome.replace(" ", "_") + ".pdf", nome))
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
        rilasciati.append((data, titolo, f'{link(pdf, titolo)} <span class="nota">v{e(versione)} ({e(data)})</span>'))
    # le ultime approvazioni in cima
    rilasciati.sort(key=lambda d: d[1])
    rilasciati.sort(key=lambda d: d[0], reverse=True)
    return [voce for _, _, voce in rilasciati]


def verbali(typst, out, cartella):
    tipo = {"interni": "interno", "esterni": "esterno"}[cartella]
    voci = []
    for sorgente in sorted((RADICE / "documenti/verbali" / cartella).glob("*.toml"), reverse=True):
        if data_iso(sorgente.stem):
            nome = f"Verbale {tipo} {sorgente.stem}"
            compila(typst, RADICE / "modello/verbale.typ", out / (nome.replace(" ", "_") + ".pdf"),
                    dati=f"/documenti/verbali/{cartella}/{sorgente.name}")
            voci.append(link(nome.replace(" ", "_") + ".pdf", nome))
    return voci


def indice(gruppo, typst, out):
    info, progetto = gruppo.get("gruppo", {}), gruppo.get("progetto", {})
    nome = info.get("nome") or "Documentazione di progetto"
    intestazione = [f"<h1>{e(nome)}</h1>",
                    "<p>Progetto didattico di Ingegneria del Software, Università degli Studi di Padova</p>"]
    if progetto.get("capitolato"):
        intestazione.append(f"<p>Capitolato {e(progetto['capitolato'])}, proposto da {e(progetto.get('proponente', ''))}</p>")
    if info.get("email"):
        intestazione.append(f"<p>Contatti: {e(info['email'])}</p>")

    membri = []
    for m in gruppo.get("membro", []):
        persona = e(f"{m.get('nome', '')} {m.get('cognome', '')}".strip())
        membri.append(f"{persona} ({link('https://github.com/' + m['github'], m['github'])})" if m.get("github") else persona)

    nessuno = "Nessun documento ancora pubblicato."
    corpo = [
        "<header>", *intestazione, "</header>",
        "<h2>Lettere di presentazione</h2>", elenco(lettere(typst, out), "Nessuna lettera ancora pubblicata."),
        "<h2>Documenti esterni</h2>",
        "<h3>Gestionali</h3>", elenco(documenti(typst, out, "documenti/esterni/gestionali"), nessuno),
        "<h3>Tecnici</h3>", elenco(documenti(typst, out, "documenti/esterni/tecnici"), nessuno),
        "<h2>Documenti interni</h2>", elenco(documenti(typst, out, "documenti/interni"), nessuno),
        "<h2>Verbali</h2>",
        "<h3>Esterni</h3>", elenco(verbali(typst, out, "esterni"), "Nessun verbale ancora pubblicato."),
        "<h3>Interni</h3>", elenco(verbali(typst, out, "interni"), "Nessun verbale ancora pubblicato."),
        "<h2>Glossario</h2>", f"<p>{link('glossario.html', 'Glossario dei termini del progetto')}</p>",
        "<h2>Il gruppo</h2>", elenco(membri, "Membri non ancora indicati."),
    ]
    return pagina(nome, "\n".join(corpo))


def senza_accenti(testo):
    return "".join(c for c in unicodedata.normalize("NFD", testo) if not unicodedata.combining(c)).casefold()


def glossario(gruppo, voci):
    nome = gruppo.get("gruppo", {}).get("nome") or "Documentazione di progetto"
    per_iniziale = {}
    for voce in sorted(voci, key=lambda v: senza_accenti(v["termine"])):
        iniziale = senza_accenti(voce["termine"])[:1].upper()
        per_iniziale.setdefault(iniziale if iniziale.isalpha() else "#", []).append(voce)
    corpo = ["<h1>Glossario</h1>", f"<p>{link('index.html', nome)}</p>"]
    for iniziale, gruppo_voci in per_iniziale.items():
        corpo += [f"<h2>{e(iniziale)}</h2>", "<dl>"]
        for voce in gruppo_voci:
            sinonimi = voce.get("sinonimi", [])
            ancore = "".join(f'<span id="{e(slug(s))}"></span>' for s in sinonimi)
            corpo.append(f'<dt id="{e(slug(voce["termine"]))}">{ancore}{e(voce["termine"])}</dt>')
            nota = f'<br><span class="nota">Sinonimi: {e(", ".join(sinonimi))}</span>' if sinonimi else ""
            corpo.append(f"<dd>{e(voce['definizione'])}{nota}</dd>")
        corpo.append("</dl>")
    if not per_iniziale:
        corpo.append('<p class="nota">Nessuna voce ancora presente.</p>')
    return pagina(f"Glossario - {nome}", "\n".join(corpo))


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
    (out / "index.html").write_text(indice(gruppo, typst, out), encoding="utf-8")
    (out / "glossario.html").write_text(glossario(gruppo, voci), encoding="utf-8")
    print(f"sito generato in {out}: {len(list(out.glob('*.pdf')))} PDF")


if __name__ == "__main__":
    main()
