"""Controlli automatici sui sorgenti del repo documentale.

Uso: python strumenti/verifica.py [percorsi...]

Senza argomenti controlla tutto il repo, altrimenti solo i file e le cartelle
indicati. Stampa una riga per problema, "percorso:riga: CODICE messaggio", ed
esce con 1 se c'è almeno un errore (E-); gli avvisi (W-) non bloccano.
"""

import csv
import datetime as dt
import re
import sys
import tomllib
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent

RUOLI = ("Responsabile", "Amministratore", "Analista", "Progettista", "Programmatore", "Verificatore")
INTESTAZIONE_REGISTRO = ["versione", "data", "autore", "verificatore", "descrizione"]
INTESTAZIONE_RUOLI = ["inizio", "fine", "membro", "ruolo"]
INTESTAZIONE_ORE = ["data", "membro", "ruolo", "ore", "riferimento"]

# Date in formati diversi da AAAA-MM-GG. Le ISO valide si scartano dopo; i punti
# valgono solo con l'anno a quattro cifre, così 1.0.10 non è una data.
DATA_SOSPETTA = re.compile(
    r"(?<![\d.])(?:"
    r"\d{1,2}([/_-])\d{1,2}\1\d{2,4}"
    r"|\d{1,2}\.\d{1,2}\.\d{4}"
    r"|\d{4}([/._-])\d{1,2}\2\d{1,2}"
    r")(?!\d)"
)
MESI = "gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre"
DATA_ESTESA = re.compile(rf"\b\d{{1,2}}\s+(?:{MESI})\s+\d{{4}}\b", re.IGNORECASE)
URL = re.compile(r"https?://[^\s\"'<>()\[\]]+")
VERSIONE = re.compile(r"(\d+)\.(\d+)\.(\d+)")
STRINGA = re.compile(r'"(?:[^"\\\n]|\\.)*"')
COMMENTO = re.compile(r"/\*.*?\*/|(?<!:)//[^\n]*", re.DOTALL)
TITOLO_TYP = re.compile(r"^[ \t]*(=+)[ \t]+(.*?)[ \t]*$", re.MULTILINE)
TERMINE = re.compile(r'(?<![\w.-])g\(\s*"((?:[^"\\]|\\.)*)"\s*\)')
CHIAMATA = re.compile(r"#([A-Za-z_][\w-]*(?:\.[A-Za-z_][\w-]*)*)?")
SEGNAPOSTO = re.compile(r"\bTODO\b|\bXXX\b|<\.\.\.>|<…>|<[^\s<>][^<>\n]*\s[^<>\n]*[^\s<>]>")

LESSICO = [
    (r"\b(?:è|sono)\s+quell[oaie]\s+di\b", 'togliere "quello di": "lo scopo è definire", non "lo scopo è quello di definire"'),
    (r"\bfortunatamente\b", "togliere l'avverbio"),
    (r"\bfare?\s+girare\b", 'usare "eseguire"'),
    (r"\blettera\s+di\s+candidatura\b", 'usare "Lettera di Presentazione"'),
    (r"\bresoconto\s+degli\s+impegni\b", 'usare "Dichiarazione degli impegni"'),
    (r"\bdecisioni\s+intraprese\b", 'usare "decisioni prese"'),
    (r"\briorganizzazione\s+operativa\b", 'usare "misure di mitigazione"'),
]
LESSICO = [(re.compile(espressione, re.IGNORECASE), correzione) for espressione, correzione in LESSICO]
SPRINT = re.compile(r"\b(la|una|della|nella|alla|dalla)\s+sprint\b", re.IGNORECASE)
SPRINT_MASCHILE = {"la": "lo", "una": "uno", "della": "dello", "nella": "nello", "alla": "allo", "dalla": "dallo"}

CAMPI_VERBALE = {
    "tipo": str, "data": dt.date, "inizio": str, "fine": str, "luogo": str,
    "redattore": str, "verificatore": str, "partecipanti": list, "assenti": list,
    "esterni": list, "approvazione_esterna": str, "ordine_del_giorno": list, "titolo": str,
    "punto": list, "decisione": list, "azione": list,
}
OBBLIGATORI_VERBALE = ("tipo", "data", "inizio", "fine", "luogo", "redattore", "verificatore",
                       "partecipanti", "ordine_del_giorno")
TABELLE_VERBALE = {
    "esterni": {"nome": str, "ruolo": str, "azienda": str},
    "punto": {"titolo": str, "sintesi": str},
    "decisione": {"id": str, "testo": str, "motivazione": str},
    "azione": {"decisione": str, "descrizione": str, "assegnatario": str, "scadenza": dt.date, "issue": str},
}

# dati/pianificazione.toml: inizio e fine (o data) previsti obbligatori, gli effettivi solo quando accadono
CAMPI_PERIODO = {"nome": str, "inizio": dt.date, "fine": dt.date, "inizio_effettivo": dt.date, "fine_effettiva": dt.date}
CAMPI_PIANO = {
    "fase": {**CAMPI_PERIODO, "nota": str, "ore_previste": (int, float), "attivita": list, "milestone": list},
    "fase.attivita": CAMPI_PERIODO,
    "fase.milestone": {"nome": str, "data": dt.date, "data_effettiva": dt.date},
}
OBBLIGATORI_PIANO = {"fase": ("nome", "inizio", "fine"), "fase.attivita": ("nome", "inizio", "fine"),
                     "fase.milestone": ("nome", "data")}


def data_iso(testo):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", testo):
        return None
    try:
        return dt.date.fromisoformat(testo)
    except ValueError:
        return None


def nome_verbale(nome):
    """(data, suffisso) dal nome di un verbale senza estensione, AAAA-MM-GG o AAAA-MM-GG-suffisso.

    Il suffisso, in minuscolo, distingue più verbali dello stesso tipo nello stesso giorno:
    per gli esterni è il codice del capitolato (2026-10-20-c7). None se il nome non è valido.
    """
    m = re.fullmatch(r"(\d{4}-\d{2}-\d{2})(?:-([a-z0-9]+))?", nome)
    return (data_iso(m[1]), m[2] or "") if m and data_iso(m[1]) else None


def numero(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def di_tipo(valore, tipo):
    # tomllib restituisce datetime (sottoclasse di date) per data e ora: qui serve la sola data
    if tipo is dt.date:
        return isinstance(valore, dt.date) and not isinstance(valore, dt.datetime)
    return isinstance(valore, tipo)


def slug(termine):
    return termine.lower().replace(" ", "-")


def leggi_csv(percorso):
    """Righe non vuote come (numero di riga, campi); la prima è l'intestazione."""
    with open(percorso, encoding="utf-8-sig", newline="") as f:
        lettore = csv.reader(f)
        return [(lettore.line_num, riga) for riga in lettore if riga]


def rilascio(percorso):
    """(versione, data) se la prima riga del registro è un'approvazione, altrimenti None."""
    righe = leggi_csv(percorso)[1:]
    if righe and len(righe[0][1]) == 5:
        versione, data, _, verificatore, descrizione = (c.strip() for c in righe[0][1])
        if not verificatore and descrizione.startswith("Approvazione"):
            return versione, data
    return None


def riga_di(testo, posizione):
    return testo.count("\n", 0, posizione) + 1


def riga_valore(testo, valore):
    for n, riga in enumerate(testo.splitlines(), start=1):
        if valore and valore in riga:
            return n
    return 0


def riga_voce(testo, tabella, i):
    """Riga dell'i-esimo [[tabella]] (da 1), altrimenti della chiave tabella = ..."""
    righe = [n for n, riga in enumerate(testo.splitlines(), start=1) if riga.strip() == f"[[{tabella}]]"]
    if len(righe) >= i:
        return righe[i - 1]
    m = re.search(rf"^\s*{re.escape(tabella)}\s*=", testo, re.MULTILINE)
    return riga_di(testo, m.start()) if m else 0


def riga_errore_toml(errore):
    m = re.search(r"line (\d+)", str(errore))
    return int(m[1]) if m else 0


def senza_commenti(testo):
    # i commenti diventano spazi: posizioni e numeri di riga restano validi
    return COMMENTO.sub(lambda m: re.sub(r"[^\n]", " ", m.group()), testo)


def chiusura(testo, i):
    """Indice della parentesi che chiude quella in testo[i] (ultimo carattere se manca)."""
    profondita, j = 0, i
    while j < len(testo):
        c = testo[j]
        if c == '"' and (m := STRINGA.match(testo, j)):
            j = m.end()
            continue
        if c in "([{":
            profondita += 1
        elif c in ")]}":
            profondita -= 1
            if profondita == 0:
                return j
        j += 1
    return len(testo) - 1


def chiamate(testo, nome):
    """(inizio, fine, argomenti) di ogni chiamata nome(...), compresi i blocchi [...] che la seguono."""
    trovate = []
    for m in re.finditer(rf"(?<![\w.-]){re.escape(nome)}(?=[(\[])", testo):
        fine = chiusura(testo, m.end())
        argomenti = testo[m.end() + 1:fine] if testo[m.end()] == "(" else ""
        while fine + 1 < len(testo) and testo[fine + 1] == "[":
            fine = chiusura(testo, fine + 1)
        trovate.append((m.start(), fine + 1, argomenti))
    return trovate


def argomenti(testo):
    parti, profondita, inizio, j = [], 0, 0, 0
    while j < len(testo):
        c = testo[j]
        if c == '"' and (m := STRINGA.match(testo, j)):
            j = m.end()
            continue
        if c in "([{":
            profondita += 1
        elif c in ")]}":
            profondita -= 1
        elif c == "," and profondita == 0:
            parti.append(testo[inizio:j].strip())
            inizio = j + 1
        j += 1
    parti.append(testo[inizio:].strip())
    return [p for p in parti if p]


def blocchi_contenuto(testo):
    i = 0
    while (j := testo.find("[", i)) != -1:
        fine = chiusura(testo, j)
        yield testo[j + 1:fine]
        i = fine + 1


def espandi(testo):
    # #f(...) lascia solo i blocchi [...] tra gli argomenti, #g("x") lascia x, #{...} sparisce
    pezzi, i = [], 0
    while m := CHIAMATA.search(testo, i):
        pezzi.append(testo[i:m.start()])
        i = m.end()
        if i < len(testo) and testo[i] in "({":
            fine = chiusura(testo, i)
            interno = testo[i + 1:fine]
            if m[1] == "g":
                stringa = STRINGA.search(interno)
                pezzi.append(stringa.group()[1:-1] if stringa else "")
            elif m[1] and testo[i] == "(":
                pezzi.append(" ".join(espandi(b) for b in blocchi_contenuto(interno)))
            i = fine + 1
    pezzi.append(testo[i:])
    return "".join(pezzi)


def testo_leggibile(sorgente):
    """Testo approssimato di un sorgente Typst, senza commenti, istruzioni e markup."""
    tenute, aperte = [], 0
    for riga in senza_commenti(sorgente).split("\n"):
        if aperte > 0 or re.match(r"[ \t]*#(?:let|set|show|import|include)\b", riga):
            aperte = max(0, aperte + sum(map(riga.count, "([{")) - sum(map(riga.count, ")]}")))
            tenute.append("")
        else:
            tenute.append(riga)
    return espandi(URL.sub(" ", "\n".join(tenute)))


def unita_di_testo(testo):
    """Titoli, voci di elenco e paragrafi: la fine di ognuno chiude una frase."""
    corrente = []
    for riga in testo.split("\n"):
        r = riga.strip()
        if not r or r.startswith("=") or re.match(r"(?:[-+]|\d+\.)\s", r):
            if corrente:
                yield " ".join(corrente)
            corrente = []
            if r.startswith("="):
                yield r
                continue
        if r:
            corrente.append(r)
    if corrente:
        yield " ".join(corrente)


def gulpease(testo):
    frasi = parole = lettere = 0
    for unita in unita_di_testo(testo):
        unita = re.sub(r"<[\w:.-]+>|@[\w:.-]+", " ", unita)
        unita = re.sub(r"[=*_`$\\#\[\](){}\"~]", " ", unita).strip()
        token = [t for t in unita.split() if any(c.isalpha() for c in t)]
        if not token:
            continue
        parole += len(token)
        lettere += sum(c.isalpha() for t in token for c in t)
        frasi += len(re.findall(r"[.!?;](?=\s|$)", unita)) + (0 if re.search(r"[.!?;]$", unita) else 1)
    if parole == 0:
        return None
    return 89 + (300 * frasi - 10 * lettere) / parole


class Verifica:
    def __init__(self, radice=RADICE):
        self.radice = Path(radice).resolve()
        self.problemi = []
        self.carica_contesto()

    def segnala(self, percorso, riga, codice, messaggio):
        self.problemi.append((percorso, riga, codice, messaggio))

    def leggi(self, rel):
        return (self.radice / rel).read_text(encoding="utf-8-sig")

    def carica_toml(self, rel):
        if not (self.radice / rel).exists():
            return {}, None
        try:
            return tomllib.loads(self.leggi(rel)), None
        except tomllib.TOMLDecodeError as e:
            return {}, (riga_errore_toml(e), f"TOML non valido: {e}")

    def carica_contesto(self):
        # dati letti sempre, anche quando si controllano solo alcuni file
        self.gruppo, self.errore_gruppo = self.carica_toml("dati/gruppo.toml")
        self.membri = [f"{m.get('nome', '')} {m.get('cognome', '')}".strip()
                       for m in self.gruppo.get("membro", []) if isinstance(m, dict)]
        costo = self.gruppo.get("progetto", {}).get("costo_aggiudicato", 0)
        soglia = self.gruppo.get("soglie", {}).get("gulpease", 40)
        self.costo_aggiudicato = costo if numero(costo) else 0
        self.soglia_gulpease = soglia if numero(soglia) else 40

        self.glossario, self.errore_glossario = self.carica_toml("dati/glossario.toml")
        self.voci = set()
        for voce in self.glossario.get("voce", []):
            for nome in [voce.get("termine", ""), *voce.get("sinonimi", [])]:
                if isinstance(nome, str) and nome:
                    self.voci.add(slug(nome))

        self.preventivo, self.errore_preventivo = self.carica_toml("dati/preventivo.toml")
        tariffe = self.preventivo.get("tariffe", {})
        self.tariffe = tariffe if isinstance(tariffe, dict) else {}

        maiuscole = self.radice / "dati/maiuscole.txt"
        voci = maiuscole.read_text(encoding="utf-8-sig").splitlines() if maiuscole.exists() else []
        self.maiuscole = sorted({v.strip() for v in voci if v.strip()}, key=len, reverse=True)

        self.periodi = []
        ruoli = self.radice / "dati/ruoli.csv"
        for n, campi in leggi_csv(ruoli)[1:] if ruoli.exists() else []:
            if len(campi) == 4:
                inizio, fine = data_iso(campi[0].strip()), data_iso(campi[1].strip())
                if inizio and fine and inizio <= fine:
                    self.periodi.append((n, inizio, fine, campi[2].strip(), campi[3].strip()))

    def ruolo_di(self, membro, giorno):
        for _, inizio, fine, chi, ruolo in self.periodi:
            if chi == membro and inizio <= giorno <= fine:
                return ruolo
        return None

    def coperta(self, giorno):
        return any(inizio <= giorno <= fine for _, inizio, fine, _, _ in self.periodi)

    # --- esecuzione ---

    def esegui(self, percorsi=None):
        for rel in self.bersagli(percorsi):
            self.controlla_file(rel)
        unici = list(dict.fromkeys(self.problemi))
        return sorted(unici, key=lambda p: (p[0], p[1]))

    def bersagli(self, percorsi):
        if not percorsi:
            percorsi = [self.radice / c for c in ("dati", "documenti", "modello", "presentazioni")]
            percorsi = [p for p in percorsi if p.exists()]
        file = []
        for p in map(Path, percorsi):
            p = p.resolve()
            if not p.exists():
                raise SystemExit(f"{p}: percorso inesistente")
            if not p.is_relative_to(self.radice):
                raise SystemExit(f"{p}: fuori dal repo")
            file += [f for f in p.rglob("*") if f.is_file()] if p.is_dir() else [p]
        return sorted({f.relative_to(self.radice).as_posix() for f in file})

    def controlla_file(self, rel):
        parti = rel.split("/")
        if parti[0] in ("documenti", "dati", "presentazioni"):
            self.controlla_nome(rel)
        suffisso = Path(rel).suffix
        # con un altro nome il sito ignorerebbe la copia firmata e pubblicherebbe quella compilata
        if suffisso == ".pdf" and parti[:2] == ["documenti", "verbali"] and not (
                rel.endswith(".firmato.pdf") and (self.radice / (rel.removesuffix(".firmato.pdf") + ".toml")).is_file()):
            self.segnala(rel, 0, "E-VERBALE-FIRMATO",
                         "la copia firmata va accanto al suo verbale, con lo stesso nome e l'estensione .firmato.pdf")
        if suffisso not in (".typ", ".toml", ".csv"):
            return
        testo = self.leggi(rel)
        if suffisso in (".typ", ".toml"):
            self.controlla_date(rel, testo)
        if parti[0] == "documenti":
            senza_registro = len(parti) > 2 and parti[1] in ("lettere", "verbali")
            if rel.endswith(".registro.csv"):
                if senza_registro:
                    self.segnala(rel, 0, "E-REGISTRO-VIETATO", "lettere e verbali non hanno registro delle modifiche")
                else:
                    self.controlla_registro(rel)
            elif suffisso == ".typ":
                self.controlla_documento(rel, testo, senza_registro)
            elif suffisso == ".toml" and parti[1] == "verbali":
                self.controlla_verbale(rel, testo)
        elif parti[0] == "presentazioni" and suffisso == ".typ":
            self.controlla_presentazione(rel, testo)
        elif rel == "dati/gruppo.toml":
            self.controlla_gruppo(testo)
        elif rel == "dati/glossario.toml":
            self.controlla_glossario(testo)
        elif rel == "dati/ruoli.csv":
            self.controlla_ruoli()
        elif rel == "dati/ore.csv":
            self.controlla_ore()
        elif rel == "dati/preventivo.toml":
            self.controlla_preventivo(testo)
        elif rel == "dati/pianificazione.toml":
            self.controlla_pianificazione(testo)

    # --- controlli comuni ---

    def controlla_nome(self, rel):
        parti = rel.split("/")
        sospetta = False
        for i in range(1, len(parti)):
            for m in DATA_SOSPETTA.finditer(parti[i]):
                if not data_iso(m.group()):
                    sospetta = True
                    self.segnala("/".join(parti[:i + 1]), 0, "E-DATA-FILE",
                                 f'"{parti[i]}": data non nel formato AAAA-MM-GG')
        cartella, nome = "/".join(parti[:-1]), parti[-1]
        verbale = cartella in ("documenti/verbali/interni", "documenti/verbali/esterni") and nome.endswith(".toml")
        datato = verbale or cartella in ("documenti/lettere", "presentazioni/diari") and nome.endswith(".typ")
        base = nome.rsplit(".", 1)[0]
        if datato and not sospetta and not (nome_verbale(base) if verbale else data_iso(base)):
            suffisso = ", con un eventuale suffisso in minuscolo (AAAA-MM-GG-c7)" if verbale else ""
            self.segnala(rel, 0, "E-DATA-FILE", f'"{nome}": il nome deve essere la data AAAA-MM-GG{suffisso}')

    def controlla_date(self, rel, testo):
        for n, riga in enumerate(testo.splitlines(), start=1):
            riga = URL.sub(" ", riga)
            for m in DATA_SOSPETTA.finditer(riga):
                if not data_iso(m.group()):
                    self.segnala(rel, n, "E-DATA-TESTO", f'data "{m.group()}" non nel formato AAAA-MM-GG')
            for m in DATA_ESTESA.finditer(riga):
                self.segnala(rel, n, "E-DATA-TESTO", f'data "{m.group()}" non nel formato AAAA-MM-GG')

    def controlla_lessico(self, rel, testo):
        for regola, correzione in LESSICO:
            for m in regola.finditer(testo):
                self.segnala(rel, riga_di(testo, m.start()), "E-LESSICO", f'"{m.group()}": {correzione}')
        for m in SPRINT.finditer(testo):
            corretto = SPRINT_MASCHILE[m[1].lower()]
            self.segnala(rel, riga_di(testo, m.start()), "E-LESSICO", f'"{m.group()}": usare "{corretto} sprint"')

    def controlla_titolo(self, rel, riga, titolo):
        testo = re.sub(r"<[\w:.-]+>\s*$", "", titolo)
        testo = re.sub(r"#[\w.-]+", " ", testo)
        esenti = [m.span() for voce in self.maiuscole
                  for m in re.finditer(rf"(?<!\w){re.escape(voce)}(?!\w)", testo)]
        parole = [m for m in re.finditer(r"\w+", testo) if m.group()[0].isalpha()]
        if not parole:
            return
        if not parole[0].group()[0].isupper():
            self.segnala(rel, riga, "E-MAIUSCOLE", f'titolo "{titolo}": la prima parola va con l\'iniziale maiuscola')
        for m in parole[1:]:
            parola = m.group()
            acronimo_o_nome = parola.isupper() or any(c.isupper() for c in parola[1:])
            if not parola[0].isupper() or acronimo_o_nome:
                continue
            if any(a <= m.start() and m.end() <= b for a, b in esenti):
                continue
            self.segnala(rel, riga, "E-MAIUSCOLE",
                         f'titolo "{titolo}": "{parola}" va con l\'iniziale minuscola (nomi propri in dati/maiuscole.txt)')

    def controlla_registro_vietato(self, rel, testo):
        for m in re.finditer(r"registro delle modifiche", testo, re.IGNORECASE):
            self.segnala(rel, riga_di(testo, m.start()), "E-REGISTRO-VIETATO",
                         "lettere e verbali non hanno registro delle modifiche")

    def controlla_segnaposto(self, rel, testo):
        for m in SEGNAPOSTO.finditer(testo):
            self.segnala(rel, riga_di(testo, m.start()), "E-SEGNAPOSTO",
                         f'segnaposto "{m.group()}" in un documento pubblicato')

    # --- documenti Typst ---

    def controlla_documento(self, rel, testo, senza_registro):
        codice = senza_commenti(testo)
        titoli = [(riga_di(codice, m.start()), len(m[1]), m[2]) for m in TITOLO_TYP.finditer(codice)]
        for riga, _, titolo in titoli:
            self.controlla_titolo(rel, riga, titolo)
        self.controlla_lessico(rel, codice)
        self.controlla_riferimenti(rel, codice, titoli)
        self.controlla_figure(rel, codice)
        self.controlla_termini(rel, codice, {riga for riga, _, _ in titoli})
        indice = gulpease(testo_leggibile(testo))
        if indice is not None and indice < self.soglia_gulpease:
            self.segnala(rel, 0, "W-GULPEASE", f"indice Gulpease {indice:.0f} sotto la soglia {self.soglia_gulpease}")

        if senza_registro:
            self.controlla_registro_vietato(rel, testo)
            self.controlla_segnaposto(rel, testo)
            data = re.search(r'\bdata:\s*"([^"]*)"', codice)
            if rel.startswith("documenti/lettere/") and data and data[1] != Path(rel).stem:
                self.segnala(rel, riga_di(codice, data.start()), "E-DATA-FILE",
                             f"la data della lettera ({data[1]}) differisce dal nome del file")
        elif "documento.with(" in codice:
            registro = rel[:-len(".typ")] + ".registro.csv"
            if not (self.radice / registro).exists():
                self.segnala(rel, 0, "E-REGISTRO-MANCANTE", f"manca {registro}")
                return
            if f'"{Path(registro).name}"' not in codice:
                self.segnala(rel, 0, "E-REGISTRO-MANCANTE", f'il documento deve caricare csv("{Path(registro).name}")')
            self.controlla_registro(registro)
            if rilascio(self.radice / registro):
                self.controlla_segnaposto(rel, testo)

    def controlla_riferimenti(self, rel, codice, titoli):
        livelli = {riga: (livello, titolo.lower()) for riga, livello, titolo in titoli}
        aperti, in_riferimenti, in_normativi = [], {}, {}
        for n in range(1, codice.count("\n") + 2):
            if n in livelli:
                while aperti and aperti[-1][0] >= livelli[n][0]:
                    aperti.pop()
                aperti.append(livelli[n])
            in_riferimenti[n] = any("riferiment" in t for _, t in aperti)
            in_normativi[n] = in_riferimenti[n] and any("normativ" in t for _, t in aperti)

        rif_web = chiamate(codice, "rif-web")
        for m in URL.finditer(codice):
            n = riga_di(codice, m.start())
            if in_riferimenti[n] and not any(a <= m.start() < b for a, b, _ in rif_web):
                self.segnala(rel, n, "E-RIFERIMENTI", "URL scritto a mano: usare rif-web(titolo, url, accesso)")
        for inizio, _, testo in rif_web:
            parti = argomenti(testo)
            if len(parti) < 3 or parti[2] in ('""', "none"):
                self.segnala(rel, riga_di(codice, inizio), "E-RIFERIMENTI", "rif-web senza data di ultimo accesso")
        for m in re.finditer(r"12207", codice):
            n = riga_di(codice, m.start())
            if in_normativi[n]:
                self.segnala(rel, n, "E-RIFERIMENTI", "ISO/IEC 12207 va tra i riferimenti informativi, non normativi")

    def controlla_figure(self, rel, codice):
        figure = chiamate(codice, "figure")
        for m in re.finditer(r"(?<![\w.-])(?<!set )(image|table)\(", codice):
            if not any(a <= m.start() < b for a, b, _ in figure):
                self.segnala(rel, riga_di(codice, m.start()), "E-FIGURA",
                             f"{m[1]}() fuori da una figure: tabelle e immagini vanno numerate con didascalia")

    def controlla_termini(self, rel, codice, righe_titoli):
        marcati = {}
        for m in TERMINE.finditer(codice):
            n, termine = riga_di(codice, m.start()), m[1]
            if n in righe_titoli:
                self.segnala(rel, n, "E-GLOSSARIO", f'g("{termine}") in un titolo: i titoli non marcano termini')
            if slug(termine) not in self.voci:
                self.segnala(rel, n, "E-GLOSSARIO", f'termine "{termine}" assente da dati/glossario.toml')
            if slug(termine) in marcati:
                self.segnala(rel, n, "W-GLOSSARIO", f'termine "{termine}" già marcato alla riga {marcati[slug(termine)]}')
            else:
                marcati[slug(termine)] = n

    # --- presentazioni ---

    def controlla_presentazione(self, rel, testo):
        codice = senza_commenti(testo)
        titoli = [(m.start(), m[2]) for m in TITOLO_TYP.finditer(codice)]
        titoli += [(m.start(), m[1]) for m in re.finditer(r'\btitolo:\s*"([^"]*)"', codice)]
        for inizio, titolo in titoli:
            self.controlla_titolo(rel, riga_di(codice, inizio), titolo)
        self.controlla_lessico(rel, codice)
        self.controlla_segnaposto(rel, testo)
        data = re.search(r'\bdata:\s*"([^"]*)"', codice)
        nome = Path(rel).stem
        if rel.startswith("presentazioni/diari/") and data and data_iso(nome) and data[1] != nome:
            self.segnala(rel, riga_di(codice, data.start()), "E-DATA-FILE",
                         f"la data del diario ({data[1]}) differisce dal nome del file")

    # --- registro delle modifiche ---

    def controlla_registro(self, rel):
        righe = leggi_csv(self.radice / rel)
        if not righe or [c.strip() for c in righe[0][1]] != INTESTAZIONE_REGISTRO:
            self.segnala(rel, 1, "E-REGISTRO-INTESTAZIONE", "intestazione attesa: " + ",".join(INTESTAZIONE_REGISTRO))
            return
        voci = []
        for n, campi in righe[1:]:
            if len(campi) != 5:
                self.segnala(rel, n, "E-REGISTRO-RIGA", f"attesi 5 campi, trovati {len(campi)}")
                continue
            versione, data, autore, verificatore, descrizione = (c.strip() for c in campi)
            numeri, giorno = VERSIONE.fullmatch(versione), data_iso(data)
            if not numeri:
                self.segnala(rel, n, "E-REGISTRO-VERSIONE", f'versione "{versione}" non nel formato X.Y.Z')
            if not giorno:
                self.segnala(rel, n, "E-REGISTRO-DATA", f'data "{data}" non nel formato AAAA-MM-GG')
            approvazione = descrizione.startswith("Approvazione")
            if approvazione:
                if verificatore:
                    self.segnala(rel, n, "E-REGISTRO-APPROVAZIONE", "un'approvazione non ha verificatore")
                if not autore:
                    self.segnala(rel, n, "E-REGISTRO-APPROVAZIONE", "approvazione senza approvatore")
                elif giorno and self.coperta(giorno) and self.ruolo_di(autore, giorno) != "Responsabile":
                    self.segnala(rel, n, "W-REGISTRO-RUOLO", f"{autore} non è il Responsabile in carica il {data}")
            elif not autore or not verificatore:
                self.segnala(rel, n, "E-REGISTRO-AUTORE",
                             'autore e verificatore obbligatori (le approvazioni iniziano con "Approvazione")')
            elif autore == verificatore:
                self.segnala(rel, n, "E-REGISTRO-AUTORE", f"{autore} è sia autore sia verificatore della modifica")
            elif giorno and self.coperta(giorno) and self.ruolo_di(verificatore, giorno) != "Verificatore":
                self.segnala(rel, n, "W-REGISTRO-RUOLO", f"{verificatore} non è Verificatore in carica il {data}")
            voci.append((n, tuple(map(int, numeri.groups())) if numeri else None, giorno, approvazione))

        def testo(v):
            return ".".join(map(str, v))

        # ogni riga si confronta con la successiva, che è la precedente nel tempo
        for (n, versione, giorno, approvazione), (_, prima, giorno_prima, approvazione_prima) in zip(voci, voci[1:]):
            if giorno and giorno_prima and giorno < giorno_prima:
                self.segnala(rel, n, "E-REGISTRO-ORDINE", "data anteriore a quella della riga successiva: l'ordine è LIFO")
            if not versione or not prima:
                continue
            x, y, z = prima
            if approvazione:
                attese = [(x + 1, 0, 0)]
                if approvazione_prima:
                    self.segnala(rel, n, "E-REGISTRO-APPROVAZIONE",
                                 "nessuna modifica verificata dopo l'approvazione precedente")
            else:
                attese = [(x, y + 1, 0), (x, y, z + 1)]
            if versione not in attese:
                self.segnala(rel, n, "E-REGISTRO-VERSIONE",
                             f"dopo {testo(prima)} è attesa {' o '.join(map(testo, attese))}, non {testo(versione)}")
        if voci:
            n, versione, _, approvazione = voci[-1]
            if versione and versione != (0, 1, 0):
                self.segnala(rel, n, "E-REGISTRO-INIZIO", "la riga più vecchia deve avere versione 0.1.0")
            if approvazione:
                self.segnala(rel, n, "E-REGISTRO-APPROVAZIONE", "la riga più vecchia non può essere un'approvazione")

    # --- verbali ---

    def controlla_verbale(self, rel, testo):
        self.controlla_lessico(rel, testo)
        self.controlla_registro_vietato(rel, testo)
        self.controlla_segnaposto(rel, testo)
        try:
            v = tomllib.loads(testo)
        except tomllib.TOMLDecodeError as e:
            self.segnala(rel, riga_errore_toml(e), "E-VERBALE-SCHEMA", f"TOML non valido: {e}")
            return
        if not self.schema_verbale(rel, testo, v):
            return

        def errore(codice, messaggio, riga=0):
            self.segnala(rel, riga, codice, messaggio)

        data, tipo = v["data"], v["tipo"]
        cartella = Path(rel).parent.name
        atteso = {"interni": "interno", "esterni": "esterno"}.get(cartella)
        if tipo not in ("interno", "esterno"):
            errore("E-VERBALE-TIPO", f'tipo "{tipo}" non ammesso: "interno" o "esterno"', riga_valore(testo, "tipo"))
        elif atteso is None:
            errore("E-VERBALE-TIPO", "i verbali vanno in documenti/verbali/interni o documenti/verbali/esterni")
        elif tipo != atteso:
            errore("E-VERBALE-TIPO", f'tipo "{tipo}" incoerente con la cartella {cartella}', riga_valore(testo, "tipo"))
        nome = nome_verbale(Path(rel).stem)
        if not nome or nome[0] != data:
            errore("E-VERBALE-DATA", f"data {data} diversa dal nome del file", riga_valore(testo, data.isoformat()))

        orari = {}
        for campo in ("inizio", "fine"):
            valore = v[campo]
            try:
                orari[campo] = dt.time.fromisoformat(valore) if re.fullmatch(r"\d{2}:\d{2}", valore) else None
            except ValueError:
                orari[campo] = None
            if orari[campo] is None:
                errore("E-VERBALE-ORARIO", f'{campo} "{valore}" non nel formato HH:MM', riga_valore(testo, valore))
        if orari["inizio"] and orari["fine"] and orari["fine"] <= orari["inizio"]:
            errore("E-VERBALE-ORARIO", "la fine deve seguire l'inizio", riga_valore(testo, v["fine"]))

        if not v["ordine_del_giorno"]:
            errore("E-VERBALE-ODG", "ordine del giorno vuoto", riga_valore(testo, "ordine_del_giorno"))
        for voce in v["ordine_del_giorno"]:
            self.controlla_titolo(rel, riga_valore(testo, voce), voce)
        if v.get("titolo"):
            self.controlla_titolo(rel, riga_valore(testo, v["titolo"]), v["titolo"])
        for punto in v.get("punto", []):
            self.controlla_titolo(rel, riga_valore(testo, punto["titolo"]), punto["titolo"])

        # il suffisso del nome del file entra nell'id: 2026-10-20-c7.toml ha VE-2026-10-20-C7.n
        suffisso = f"-{nome[1].upper()}" if nome and nome[1] else ""
        prefisso = ("VI" if tipo == "interno" else "VE") + f"-{data}{suffisso}"
        decisioni = set()
        if not v.get("decisione"):
            errore("E-VERBALE-DECISIONE", "serve almeno una decisione")
        for d in v.get("decisione", []):
            riga = riga_valore(testo, d["id"])
            if not re.fullmatch(rf"{re.escape(prefisso)}\.\d+", d["id"]):
                errore("E-VERBALE-DECISIONE", f'id "{d["id"]}" non nel formato {prefisso}.n', riga)
            if d["id"] in decisioni:
                errore("E-VERBALE-DECISIONE", f'id "{d["id"]}" ripetuto', riga)
            decisioni.add(d["id"])

        for a in v.get("azione", []):
            riga = riga_valore(testo, a["descrizione"])
            if a["decisione"] not in decisioni:
                errore("E-VERBALE-AZIONE", f'azione riferita a una decisione inesistente: "{a["decisione"]}"', riga)
            if a["assegnatario"] not in self.membri:
                errore("E-VERBALE-AZIONE", f'assegnatario "{a["assegnatario"]}" non è un membro del gruppo', riga)
            if a["scadenza"] < data:
                errore("E-VERBALE-AZIONE", f"scadenza {a['scadenza']} precedente alla riunione", riga)
            if not a.get("issue"):
                errore("W-VERBALE-ISSUE", "azione senza URL della issue", riga)

        if v["redattore"] == v["verificatore"]:
            errore("E-VERBALE-REDATTORE", "redattore e verificatore devono essere persone diverse",
                   riga_valore(testo, "verificatore"))
        if not v["partecipanti"]:
            errore("E-VERBALE-PARTECIPANTI", "nessun partecipante", riga_valore(testo, "partecipanti"))
        persone = [v["redattore"], v["verificatore"], *v["partecipanti"], *v.get("assenti", [])]
        for persona in dict.fromkeys(persone):
            if persona not in self.membri:
                errore("E-VERBALE-PARTECIPANTI", f'"{persona}" non è un membro del gruppo', riga_valore(testo, persona))

        if tipo == "esterno":
            if not v.get("esterni"):
                errore("E-VERBALE-ESTERNI", "un verbale esterno indica gli esterni presenti")
            if not v.get("approvazione_esterna"):
                errore("W-VERBALE-APPROVAZIONE", "manca l'approvazione esterna del verbale")

    def schema_verbale(self, rel, testo, v):
        problemi = []
        for campo, valore in v.items():
            if campo not in CAMPI_VERBALE:
                problemi.append((riga_valore(testo, campo), f'campo sconosciuto "{campo}"'))
            elif not di_tipo(valore, CAMPI_VERBALE[campo]):
                problemi.append((riga_valore(testo, campo), f'"{campo}" di tipo errato'))
        for campo in OBBLIGATORI_VERBALE:
            if campo not in v:
                problemi.append((0, f'campo obbligatorio "{campo}" mancante'))
        for campo in ("partecipanti", "assenti", "ordine_del_giorno"):
            if isinstance(v.get(campo), list) and not all(isinstance(x, str) for x in v[campo]):
                problemi.append((riga_valore(testo, campo), f'"{campo}" contiene valori che non sono stringhe'))
        for tabella, campi in TABELLE_VERBALE.items():
            voci = v.get(tabella, [])
            for i, voce in enumerate(voci if isinstance(voci, list) else [], start=1):
                riga = riga_voce(testo, tabella, i)
                if not isinstance(voce, dict):
                    problemi.append((riga, f"{tabella} {i}: atteso un elenco di tabelle"))
                    continue
                for chiave, valore in voce.items():
                    if chiave not in campi:
                        problemi.append((riga, f'{tabella} {i}: campo sconosciuto "{chiave}"'))
                    elif not di_tipo(valore, campi[chiave]):
                        problemi.append((riga, f'{tabella} {i}: "{chiave}" di tipo errato'))
                for chiave in campi:
                    if chiave != "issue" and not voce.get(chiave):
                        problemi.append((riga, f'{tabella} {i}: "{chiave}" mancante o vuoto'))
        for riga, messaggio in problemi:
            self.segnala(rel, riga, "E-VERBALE-SCHEMA", messaggio)
        return not problemi

    # --- dati ---

    def controlla_gruppo(self, testo):
        rel = "dati/gruppo.toml"
        if self.errore_gruppo:
            self.segnala(rel, self.errore_gruppo[0], "E-DATI", self.errore_gruppo[1])
            return
        for sezione in ("gruppo", "progetto", "soglie"):
            if not isinstance(self.gruppo.get(sezione), dict):
                self.segnala(rel, 0, "E-DATI", f"sezione [{sezione}] mancante")
        progetto, soglie = self.gruppo.get("progetto", {}), self.gruppo.get("soglie", {})
        if not numero(progetto.get("costo_aggiudicato", 0)):
            self.segnala(rel, riga_valore(testo, "costo_aggiudicato"), "E-DATI", "costo_aggiudicato deve essere un numero")
        if not numero(soglie.get("gulpease", 40)):
            self.segnala(rel, riga_valore(testo, "gulpease"), "E-DATI", "la soglia gulpease deve essere un numero")
        for i, membro in enumerate(self.gruppo.get("membro", []), start=1):
            if not isinstance(membro, dict) or not membro.get("nome") or not membro.get("cognome"):
                self.segnala(rel, riga_voce(testo, "membro", i), "E-DATI", "membro senza nome o cognome")
        for membro in {m for m in self.membri if self.membri.count(m) > 1}:
            self.segnala(rel, 0, "E-DATI", f"{membro} compare più volte")

    def controlla_glossario(self, testo):
        rel = "dati/glossario.toml"
        if self.errore_glossario:
            self.segnala(rel, self.errore_glossario[0], "E-GLOSSARIO", self.errore_glossario[1])
            return
        visti = {}
        for i, voce in enumerate(self.glossario.get("voce", []), start=1):
            riga = riga_voce(testo, "voce", i)
            termine, definizione = voce.get("termine"), voce.get("definizione")
            if not (isinstance(termine, str) and termine.strip() and isinstance(definizione, str) and definizione.strip()):
                self.segnala(rel, riga, "E-GLOSSARIO", "voce senza termine o definizione")
                continue
            sinonimi = voce.get("sinonimi", [])
            if not isinstance(sinonimi, list) or not all(isinstance(s, str) for s in sinonimi):
                self.segnala(rel, riga, "E-GLOSSARIO", "sinonimi deve essere un elenco di stringhe")
                sinonimi = []
            for nome in [termine, *sinonimi]:
                if slug(nome) in visti:
                    self.segnala(rel, riga, "E-GLOSSARIO", f'"{nome}" ripete la voce della riga {visti[slug(nome)]}')
                else:
                    visti[slug(nome)] = riga
        self.controlla_lessico(rel, testo)

    def controlla_ruoli(self):
        rel = "dati/ruoli.csv"
        righe = leggi_csv(self.radice / rel)
        if not righe or [c.strip() for c in righe[0][1]] != INTESTAZIONE_RUOLI:
            self.segnala(rel, 1, "E-RUOLI", "intestazione attesa: " + ",".join(INTESTAZIONE_RUOLI))
            return
        for n, campi in righe[1:]:
            if len(campi) != 4:
                self.segnala(rel, n, "E-RUOLI", f"attesi 4 campi, trovati {len(campi)}")
                continue
            inizio, fine, membro, ruolo = (c.strip() for c in campi)
            if not data_iso(inizio) or not data_iso(fine):
                self.segnala(rel, n, "E-RUOLI", "date non nel formato AAAA-MM-GG")
            elif data_iso(fine) < data_iso(inizio):
                self.segnala(rel, n, "E-RUOLI", "la fine precede l'inizio")
            if membro not in self.membri:
                self.segnala(rel, n, "E-RUOLI", f'membro "{membro}" sconosciuto')
            if ruolo not in RUOLI:
                self.segnala(rel, n, "E-RUOLI", f'ruolo "{ruolo}" non ammesso')
        per_membro = {}
        for n, inizio, fine, membro, _ in self.periodi:
            per_membro.setdefault(membro, []).append((inizio, fine, n))
        for membro, periodi in per_membro.items():
            ultimo = None  # (fine più lontana vista finora, sua riga)
            for inizio, fine, n in sorted(periodi):
                if ultimo and inizio <= ultimo[0]:
                    self.segnala(rel, n, "E-RUOLI", f"{membro}: periodo sovrapposto a quello della riga {ultimo[1]}")
                if not ultimo or fine > ultimo[0]:
                    ultimo = (fine, n)

    def controlla_ore(self):
        rel = "dati/ore.csv"
        righe = leggi_csv(self.radice / rel)
        if not righe or [c.strip() for c in righe[0][1]] != INTESTAZIONE_ORE:
            self.segnala(rel, 1, "E-ORE", "intestazione attesa: " + ",".join(INTESTAZIONE_ORE))
            return
        totali, costo = {}, 0.0
        for n, campi in righe[1:]:
            if len(campi) != 5:
                self.segnala(rel, n, "E-ORE", f"attesi 5 campi, trovati {len(campi)}")
                continue
            data, membro, ruolo, ore, _ = (c.strip() for c in campi)
            giorno = data_iso(data)
            if not giorno:
                self.segnala(rel, n, "E-ORE", f'data "{data}" non nel formato AAAA-MM-GG')
            if membro not in self.membri:
                self.segnala(rel, n, "E-ORE", f'membro "{membro}" sconosciuto')
            if ruolo not in RUOLI:
                self.segnala(rel, n, "E-ORE", f'ruolo "{ruolo}" non ammesso')
            try:
                valore = float(ore)
            except ValueError:
                self.segnala(rel, n, "E-ORE", f'ore "{ore}" non numeriche (decimali con il punto)')
                continue
            if valore <= 0:
                self.segnala(rel, n, "E-ORE", "le ore devono essere positive")
            if giorno and membro in self.membri and ruolo in RUOLI:
                atteso = self.ruolo_di(membro, giorno)
                if atteso is None:
                    self.segnala(rel, n, "E-ORE", f"{membro} non ha un ruolo in dati/ruoli.csv il {data}")
                elif atteso != ruolo:
                    self.segnala(rel, n, "E-ORE", f"il {data} {membro} è {atteso}, non {ruolo}")
            totali[membro] = totali.get(membro, 0) + valore
            costo += valore * self.tariffe.get(ruolo, 0)
        for membro, totale in totali.items():
            if totale > 95:
                self.segnala(rel, 0, "E-ORE", f"{membro}: {totale:g} ore, oltre il massimo di 95")
        if self.costo_aggiudicato > 0 and costo > self.costo_aggiudicato:
            self.segnala(rel, 0, "E-ORE",
                         f"costo consuntivo {costo:.2f} € oltre il costo aggiudicato di {self.costo_aggiudicato:.2f} €")

    def controlla_preventivo(self, testo):
        rel = "dati/preventivo.toml"
        if self.errore_preventivo:
            self.segnala(rel, self.errore_preventivo[0], "E-PREVENTIVO", self.errore_preventivo[1])
            return
        if any(not numero(self.tariffe.get(r)) for r in RUOLI):
            self.segnala(rel, riga_valore(testo, "[tariffe]"), "E-PREVENTIVO", "[tariffe] deve indicare la tariffa di ogni ruolo")
            return
        ripartizione = self.preventivo.get("ripartizione", [])
        if not ripartizione:
            return
        costo, visti = 0.0, set()
        for i, voce in enumerate(ripartizione, start=1):
            riga, membro = riga_voce(testo, "ripartizione", i), voce.get("membro", "")
            if membro not in self.membri:
                self.segnala(rel, riga, "E-PREVENTIVO", f'membro "{membro}" sconosciuto')
            if membro in visti:
                self.segnala(rel, riga, "E-PREVENTIVO", f"{membro} compare in più ripartizioni")
            visti.add(membro)
            for chiave in voce:
                if chiave != "membro" and chiave not in RUOLI:
                    self.segnala(rel, riga, "E-PREVENTIVO", f'ruolo "{chiave}" non ammesso')
            ore = {r: voce.get(r, 0) for r in RUOLI}
            if not all(numero(x) and x >= 0 for x in ore.values()):
                self.segnala(rel, riga, "E-PREVENTIVO", f"{membro}: le ore devono essere numeri non negativi")
                continue
            for ruolo, x in ore.items():
                if x == 0:
                    self.segnala(rel, riga, "E-PREVENTIVO", f"{membro}: 0 ore da {ruolo}, ogni membro ricopre tutti i ruoli")
            totale = sum(ore.values())
            if not 80 <= totale <= 95:
                self.segnala(rel, riga, "E-PREVENTIVO", f"{membro}: {totale:g} ore, fuori dall'intervallo 80-95")
            costo += sum(x * self.tariffe[r] for r, x in ore.items())
        for membro in self.membri:
            if membro not in visti:
                self.segnala(rel, 0, "E-PREVENTIVO", f"{membro} non ha ore preventivate")
        minimo = 12000 * len(self.membri) / 7
        if costo < minimo:
            self.segnala(rel, 0, "E-PREVENTIVO",
                         f"costo totale {costo:.2f} € sotto il minimo di {minimo:.2f} € (12000 € x {len(self.membri)}/7)")
        elif costo > minimo * 1.07:
            self.segnala(rel, 0, "W-PREVENTIVO",
                         f"costo totale {costo:.2f} € oltre il 107% del minimo di {minimo:.2f} €: conforme ma elevato")

    def controlla_pianificazione(self, testo):
        rel = "dati/pianificazione.toml"
        try:
            piano = tomllib.loads(testo)
        except tomllib.TOMLDecodeError as e:
            self.segnala(rel, riga_errore_toml(e), "E-PIANO", f"TOML non valido: {e}")
            return
        for chiave in piano.keys() - {"fase"}:
            self.segnala(rel, riga_valore(testo, chiave), "E-PIANO", f'chiave "{chiave}" non ammessa')
        fasi = piano.get("fase")
        if not isinstance(fasi, list) or not fasi:
            self.segnala(rel, 0, "E-PIANO", "nessuna [[fase]]")
            return
        oggi = dt.date.today()
        # attività e milestone si numerano su tutto il file, per ritrovarne la riga
        conta = {"attivita": 0, "milestone": 0}
        precedente = None
        for i, fase in enumerate(fasi, start=1):
            valida = self.voce_piano(rel, riga_voce(testo, "fase", i), "fase", fase, oggi)
            for tabella in conta:
                voci = fase.get(tabella, []) if isinstance(fase, dict) else []
                for voce in voci if isinstance(voci, list) else []:
                    conta[tabella] += 1
                    riga = riga_voce(testo, f"fase.{tabella}", conta[tabella])
                    if not (self.voce_piano(rel, riga, f"fase.{tabella}", voce, oggi) and valida):
                        continue
                    inizio, fine = (voce["data"], voce["data"]) if tabella == "milestone" else (voce["inizio"], voce["fine"])
                    if inizio < fase["inizio"] or fine > fase["fine"]:
                        self.segnala(rel, riga, "W-PIANO", f'"{voce["nome"]}" è prevista fuori dalla fase "{fase["nome"]}"')
            if valida and precedente:
                # le fasi si susseguono: così ogni ora di dati/ore.csv cade in una fase sola
                if fase["inizio"] <= precedente["fine"]:
                    self.segnala(rel, riga_voce(testo, "fase", i), "E-PIANO",
                                 f'fase "{fase["nome"]}": inizio previsto non successivo alla fine della fase precedente')
                fine_precedente = precedente.get("fine_effettiva")
                if "inizio_effettivo" in fase and (fine_precedente is None or fase["inizio_effettivo"] <= fine_precedente):
                    self.segnala(rel, riga_voce(testo, "fase", i), "E-PIANO",
                                 f'fase "{fase["nome"]}": iniziata prima della fine effettiva della fase precedente')
            precedente = fase if valida else None
        self.controlla_lessico(rel, testo)

    def voce_piano(self, rel, riga, tabella, voce, oggi):
        """Campi, tipi e date di una fase, attività o milestone; True se è utilizzabile."""
        if not isinstance(voce, dict):
            self.segnala(rel, riga, "E-PIANO", f"[[{tabella}]] non valida")
            return False
        campi, problemi = CAMPI_PIANO[tabella], []
        for chiave, valore in voce.items():
            if chiave not in campi:
                problemi.append(f'chiave "{chiave}" non ammessa')
            elif chiave == "ore_previste":
                if not (numero(valore) and valore >= 0):
                    problemi.append("ore_previste deve essere un numero non negativo")
            elif not di_tipo(valore, campi[chiave]):
                problemi.append(f"{chiave}: atteso {'una data AAAA-MM-GG' if campi[chiave] is dt.date else 'un altro tipo'}")
        problemi += [f"{chiave} mancante" for chiave in OBBLIGATORI_PIANO[tabella] if chiave not in voce]
        if not problemi and not voce["nome"].strip():
            problemi.append("nome vuoto")
        if not problemi and tabella != "fase.milestone":
            if voce["fine"] < voce["inizio"]:
                problemi.append("la fine prevista precede l'inizio")
            if "fine_effettiva" in voce and "inizio_effettivo" not in voce:
                problemi.append("fine_effettiva senza inizio_effettivo")
            elif "fine_effettiva" in voce and voce["fine_effettiva"] < voce["inizio_effettivo"]:
                problemi.append("la fine effettiva precede l'inizio effettivo")
        for chiave in ("inizio_effettivo", "fine_effettiva", "data_effettiva"):
            if di_tipo(voce.get(chiave), dt.date) and voce[chiave] > oggi:
                problemi.append(f"{chiave} {voce[chiave]} nel futuro: gli effettivi si scrivono quando accadono")
        nome = voce.get("nome") if isinstance(voce.get("nome"), str) else ""
        for problema in problemi:
            self.segnala(rel, riga, "E-PIANO", f'{tabella} "{nome}": {problema}' if nome else problema)
        return not problemi


def main(argomenti_riga):
    # su Windows l'output rediretto non sarebbe UTF-8
    for flusso in (sys.stdout, sys.stderr):
        flusso.reconfigure(encoding="utf-8", errors="replace")
    try:
        problemi = Verifica().esegui(argomenti_riga)
    except (AttributeError, KeyError, TypeError, ValueError) as e:
        # un valore del tipo sbagliato in dati/ non deve diventare un traceback
        print(f"dati:0: E-DATI dati non validi in dati/ ({type(e).__name__}: {e})")
        return 1
    for percorso, riga, codice, messaggio in problemi:
        print(f"{percorso}:{riga}: {codice} {messaggio}")
    return 1 if any(codice.startswith("E-") for _, _, codice, _ in problemi) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
