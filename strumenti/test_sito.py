import datetime
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import sito

D = datetime.date
FASI = [{"nome": "Candidatura", "inizio": D(2026, 10, 1), "fine": D(2026, 10, 10), "inizio_effettivo": D(2026, 10, 1),
         "ore_previste": 0, "nota": "Ore non contabilizzate.",
         "attivita": [{"nome": "Capitolati", "inizio": D(2026, 10, 1), "fine": D(2026, 10, 5), "inizio_effettivo": D(2026, 10, 1)}],
         "milestone": [{"nome": "Invio", "data": D(2026, 10, 10)}]},
        {"nome": "RTB", "inizio": D(2026, 10, 11), "fine": D(2026, 10, 20)}]

GRUPPO = {"gruppo": {"nome": "Gruppo 42", "repo": "https://github.com/prova/docs"},
          "membro": [{"nome": "Anna", "cognome": "Rossi", "github": "annarossi"},
                     {"nome": "Luca", "cognome": "Bianchi", "github": ""}]}
PERIODI = [{"inizio": "2026-10-16", "fine": "2026-11-02", "membro": "Anna Rossi", "ruolo": "Responsabile"},
           {"inizio": "2026-10-16", "fine": "2026-11-02", "membro": "Luca Bianchi", "ruolo": "Verificatore"},
           {"inizio": "2026-11-03", "fine": "2026-11-16", "membro": "Luca Bianchi", "ruolo": "Analista"}]

# 90 ore e 1750 euro a testa
PREVENTIVO = {"tariffe": {"Responsabile": 30, "Amministratore": 20, "Analista": 25, "Progettista": 25, "Programmatore": 15,
                          "Verificatore": 15},
              "ripartizione": [{"membro": m, "Responsabile": 10, "Amministratore": 10, "Analista": 10, "Progettista": 10,
                                "Programmatore": 40, "Verificatore": 10} for m in ("Anna Rossi", "Luca Bianchi")]}
# la RTB dura 20 giorni con 180 ore previste: 9 al giorno, 90 al 2026-10-25
FASI_ORE = [{"nome": "Candidatura", "inizio": D(2026, 10, 1), "fine": D(2026, 10, 15), "inizio_effettivo": D(2026, 10, 1),
             "fine_effettiva": D(2026, 10, 15), "ore_previste": 0},
            {"nome": "RTB", "inizio": D(2026, 10, 16), "fine": D(2026, 11, 4), "inizio_effettivo": D(2026, 10, 16), "ore_previste": 180,
             "attivita": [{"nome": "Analisi", "inizio": D(2026, 10, 16), "fine": D(2026, 10, 20), "inizio_effettivo": D(2026, 10, 16)}],
             "milestone": [{"nome": "Revisione", "data": D(2026, 11, 4)}]}]
ORE = [(D(2026, 10, 20), 40.0, "Anna Rossi", "Responsabile"), (D(2026, 10, 22), 45.0, "Luca Bianchi", "Verificatore")]
OGGI = D(2026, 10, 25)


class TestSito(unittest.TestCase):
    def test_pagina_ha_logo_colore_e_marchio(self):
        html = sito.pagina("Titolo", sito.apertura("G", "k"), "<p>corpo</p>", GRUPPO, "logo.png", "#123456")
        self.assertIn('<a class="marchio" href="index.html"><img src="logo.png" alt="">', html)
        self.assertIn("<b>Gruppo 42</b>", html)
        self.assertIn('rel="icon" type="image/png" href="logo.png"', html)
        self.assertIn("--accento: #123456;", html)
        self.assertIn("Sorgenti su GitHub", html)
        self.assertIn('src: url("font/atkinson-hyperlegible-next.woff2") format("woff2")', html)
        self.assertIn('--sans: "Atkinson Hyperlegible Next",', html)
        self.assertIn('<link rel="preload" href="font/atkinson-hyperlegible-mono.woff2" as="font" type="font/woff2" crossorigin>', html)

    def test_pagina_senza_logo_e_senza_laterale(self):
        html = sito.pagina("Titolo", sito.apertura("G", "k"), "<p>c</p>", {"gruppo": {}}, None, "#000000")
        self.assertNotIn("<img", html)
        self.assertNotIn('rel="icon"', html)
        self.assertNotIn("dati-ruoli", html)
        self.assertNotIn('class="colonne"', html)
        con = sito.pagina("T", "", "<p>c</p>", {"gruppo": {}}, None, "#000000", laterale=sito.indice([("#a", "A")]))
        self.assertIn('<div class="colonne"><nav class="indice" aria-label="In questa pagina">', con)

    def test_menu_delle_pagine(self):
        html = sito.pagina("T", "", "", GRUPPO, None, "#000000", corrente="ruoli.html")
        self.assertIn('<nav class="menu" aria-label="Pagine del sito"><ul><li><a href="index.html">Documenti</a></li>'
                      '<li><a href="cruscotto.html">Cruscotto</a></li>', html)
        self.assertIn('<li><a href="ruoli.html" aria-current="page">Gruppo</a></li>', html)
        self.assertEqual(html.count(' aria-current="page">'), 1)  # il CSS ne contiene un'altra
        self.assertNotIn(' aria-current="page">', sito.pagina("T", "", "", GRUPPO, None, "#000000"))

    def test_accessibilita_e_temi(self):
        html = sito.pagina("Titolo", sito.apertura("G", "k"), "", {"gruppo": {}}, None, "#000000")
        self.assertIn('<html lang="it">', html)
        self.assertIn('<a class="salta" href="#contenuto">', html)
        self.assertIn('<main id="contenuto" tabindex="-1">', html)
        self.assertIn('<button class="tema" type="button" aria-pressed="false" aria-label="Passa al tema scuro">', html)
        self.assertIn("localStorage.getItem('tema')", html)
        self.assertIn('@media (prefers-color-scheme: dark) { :root:not([data-theme="light"])', html)
        self.assertIn(':root[data-theme="dark"]', html)
        self.assertNotIn("{scuro}", html)
        self.assertIn("--carta: #faf9f6;", html)
        self.assertIn("--carta: #0f0f0f;", html)
        self.assertIn('meta[name="theme-color"]', html)
        self.assertIn("IntersectionObserver", html)

    def test_apertura_e_cifre_in_evidenza(self):
        self.assertEqual(sito.evidenzia_cifre("SW2 Corporation & co"), 'SW<span class="accento">2</span> Corporation &amp; co')
        html = sito.apertura(sito.evidenzia_cifre("Gruppo 42"), "Kicker", "Sotto", ["<a href=\"x\">x</a>", "Aggiornato"], compatta=True)
        self.assertIn('<section class="apertura compatta"><p class="kicker">Kicker</p>', html)
        self.assertIn('<h1 class="titolone">Gruppo <span class="accento">42</span></h1>', html)
        self.assertIn('<p class="sotto">Sotto</p>', html)
        self.assertIn('<ul class="meta"><li><a href="x">x</a></li><li>Aggiornato</li></ul>', html)

    def test_persona_con_e_senza_github(self):
        con, senza = (sito.persona(m) for m in GRUPPO["membro"])
        self.assertIn('<a class="utente" href="https://github.com/annarossi"', con)
        self.assertIn("@annarossi", con)
        self.assertIn("annarossi.png", con)
        self.assertIn("nuova scheda", con)
        self.assertNotIn("data-membro", con)
        self.assertNotIn("<img", senza)
        self.assertNotIn("<a ", senza)
        self.assertIn('<span class="iniziali" aria-hidden="true">LB</span>', senza)
        con_ruolo = sito.persona(GRUPPO["membro"][0], con_ruolo=True)
        self.assertIn('<li class="persona" data-membro="Anna Rossi">', con_ruolo)
        self.assertIn('<span class="ruolo" hidden></span>', con_ruolo)

    def test_voce_ed_elenco(self):
        riga = sito.voce("a.pdf", "Doc", "v1.0.0", sotto="aggiornato il 2026-10-29")
        # il titolo apre la pagina di lettura del PDF, nella stessa scheda; il PDF si scarica dal suo link
        self.assertIn('<a class="titolo" href="a.html">Doc</a>', riga)
        self.assertIn('<span class="dettaglio"><span class="mono">v1.0.0</span> · aggiornato il 2026-10-29</span>', riga)
        self.assertIn('<a class="pdf" href="a.pdf" download>PDF<span class="sr-only"> di Doc</span></a>', riga)
        self.assertNotIn("nuova scheda", riga)
        self.assertNotIn("dettaglio", sito.voce("a.pdf", "Doc"))
        con_data = sito.voce("v.pdf", "Verbale interno", "2026-10-14", nascosto=" del 2026-10-14")
        self.assertIn('<a class="titolo" href="v.html">Verbale interno<span class="sr-only"> del 2026-10-14</span></a>', con_data)
        self.assertIn('PDF<span class="sr-only"> di Verbale interno del 2026-10-14</span>', con_data)
        self.assertIn('<p class="vuoto">vuoto &amp; basta</p>', sito.elenco([], "vuoto & basta"))
        self.assertIn('<ol class="voci"><li class="voce">riga</li></ol>', sito.elenco(["riga"], "vuoto"))

    def test_pagina_pdf(self):
        html = sito.pagina_pdf(GRUPPO, "logo.png", "#123456", "Verbale_esterno_2026-10-20-c7.pdf")
        self.assertIn("<title>Verbale esterno 2026-10-20-c7 - Gruppo 42</title>", html)
        self.assertIn('data-pdf="Verbale_esterno_2026-10-20-c7.pdf"', html)
        self.assertIn('<a class="scarica" href="Verbale_esterno_2026-10-20-c7.pdf" download>', html)
        self.assertIn('<a href="Verbale_esterno_2026-10-20-c7.pdf">scaricalo</a>', html)
        # pdf.js con versione e impronte fissate: CSS e due moduli dai tag, il worker dal fetch
        self.assertEqual(html.count('integrity="sha384-'), 3)
        self.assertIn(f'data-worker="{sito.SRI_PDFJS["build/pdf.worker.min.mjs"]}"', html)
        # il CSS di pdf.js prima dello stile del sito, che decide il tema
        self.assertLess(html.index("pdf_viewer.css"), html.index("@font-face"))

    def test_verbali_con_titolo_e_approvazione(self):
        esterno = {"tipo": "esterno", "esterni": [{"azienda": "Ergon"}, {"azienda": "Ergon"}], "ordine_del_giorno": ["Dati"],
                   "verificatore": "Anna Rossi", "approvazione_esterna": ""}
        self.assertEqual(sito.titolo_verbale(esterno), "Incontro con Ergon")
        self.assertEqual(sito.titolo_verbale({**esterno, "titolo": "Avvio"}), "Avvio")
        self.assertEqual(sito.titolo_verbale({"tipo": "interno", "ordine_del_giorno": ["Logo", "Ruoli", "Calendario"]}),
                         "Logo e altri 2 punti")
        self.assertEqual(sito.titolo_verbale({"tipo": "interno", "ordine_del_giorno": ["Logo", "Ruoli"]}), "Logo e Ruoli")
        self.assertIn("In attesa di approvazione del proponente", sito.stato_verbale(esterno))
        self.assertIn("✓</span> Approvato via email il 2026-10-21",
                      sito.stato_verbale({**esterno, "approvazione_esterna": "Approvato via email il 2026-10-21"}))
        self.assertIn("Approvato: per email", sito.stato_verbale({**esterno, "approvazione_esterna": "per email"}))
        self.assertIn("Verificato da Anna Rossi", sito.stato_verbale({**esterno, "tipo": "interno"}))
        riga = sito.voce("v.pdf", "Incontro con Ergon", "2026-10-20 C7", sotto="<b>stato</b>")
        self.assertIn('<span class="dettaglio"><span class="mono">2026-10-20 C7</span> · <b>stato</b></span>', riga)

    def test_verbale_firmato_pubblicato_com_e(self):
        with tempfile.TemporaryDirectory() as tmp:
            radice, out = Path(tmp), Path(tmp) / "site"
            cartella = radice / "documenti/verbali/esterni"
            cartella.mkdir(parents=True)
            out.mkdir()
            (cartella / "2026-10-20-c7.toml").write_text('tipo = "esterno"\n', encoding="utf-8")
            (cartella / "2026-10-21.toml").write_text('tipo = "esterno"\nversione = "1.0.1"\naggiornato = 2026-10-23\n', encoding="utf-8")
            (cartella / "2026-10-20-c7.firmato.pdf").write_bytes(b"%PDF firmato")
            compilati = []
            with mock.patch.object(sito, "RADICE", radice), \
                    mock.patch.object(sito, "compila", lambda typst, sorgente, pdf, dati=None: compilati.append(pdf.name)):
                voci = sito.verbali("typst", out, "esterni")
            self.assertEqual((out / "Verbale_esterno_2026-10-20-c7.pdf").read_bytes(), b"%PDF firmato")
            self.assertEqual(compilati, ["Verbale_esterno_2026-10-21.pdf"])
            self.assertEqual(len(voci), 2)
            # versione accanto alla data della riunione, ultimo aggiornamento dopo lo stato
            self.assertIn('<span class="dettaglio"><span class="mono">2026-10-21 · v1.0.1</span> · '
                          '<span class="approvazione a-attesa">', voci[0])
            self.assertIn("proponente</span> · aggiornato\u00a0il\u00a02026-10-23</span>", voci[0])
            self.assertIn('<span class="dettaglio"><span class="mono">2026-10-20 C7</span> · ', voci[1])

    def test_diari_con_versione_e_aggiornamento(self):
        with tempfile.TemporaryDirectory() as tmp:
            radice, out = Path(tmp), Path(tmp) / "site"
            cartella = radice / "presentazioni/diari"
            cartella.mkdir(parents=True)
            out.mkdir()
            (cartella / "2026-10-26.typ").write_text(
                '#show: presentazione.with(evento: "Diario di bordo", data: "2026-10-26", versione: "1.0.1",\n'
                '  aggiornato: "2026-10-27", titolo: "Settimana dal 2026-10-19 al 2026-10-25")\n'
                '#slide(titolo: "Fatto e da fare")[]\n', encoding="utf-8")
            (cartella / "2026-11-02.typ").write_text('#show: presentazione.with(data: "2026-11-02")\n', encoding="utf-8")
            compilati = []
            with mock.patch.object(sito, "RADICE", radice), \
                    mock.patch.object(sito, "compila", lambda typst, sorgente, pdf, dati=None: compilati.append(pdf.name)):
                voci = sito.diari("typst", out)
            # data e versione nel nome del PDF, il più recente in cima
            self.assertEqual(compilati, ["Diario_di_bordo_2026-11-02.pdf", "Diario_di_bordo_2026-10-26_v1.0.1.pdf"])
            self.assertIn('<a class="titolo" href="Diario_di_bordo_2026-10-26_v1.0.1.html">Settimana dal 2026-10-19 al 2026-10-25'
                          '<span class="sr-only">, diario di bordo del 2026-10-26</span></a>', voci[1])
            self.assertIn('<span class="dettaglio"><span class="mono">2026-10-26 · v1.0.1</span> · '
                          'aggiornato\u00a0il\u00a02026-10-27</span>', voci[1])
            self.assertIn('<a class="pdf" href="Diario_di_bordo_2026-10-26_v1.0.1.pdf" download>', voci[1])
            self.assertIn('<span class="dettaglio"><span class="mono">2026-11-02</span></span>', voci[0])

    def test_sezione_e_indice(self):
        html = sito.sezione("id", "A & B", "<p>c</p>", 3)
        self.assertIn('<section class="sezione" id="id" aria-labelledby="titolo-id">', html)
        self.assertIn('<h2 id="titolo-id">A &amp; B<span class="conta"><span class="sr-only">Elementi: </span>3</span></h2>', html)
        self.assertNotIn('class="conta"', sito.sezione("id", "Vuota", "", 0))
        nav = sito.indice([("#a", "Uno")])
        self.assertIn('<p class="titoletto" aria-hidden="true">In questa pagina</p><ol><li><a href="#a">Uno</a></li></ol>', nav)

    def test_sottogruppi(self):
        self.assertEqual(sito.sottogruppi([("Esterni", []), ("Interni", [])], "Niente"), '<p class="vuoto">Niente</p>')
        html = sito.sottogruppi([("Esterni", []), ("Interni", ["riga"])], "Niente")
        self.assertEqual(html, '<h3>Interni</h3><ol class="voci"><li class="voce">riga</li></ol>')

    def test_linea_del_tempo(self):
        html = sito.linea_del_tempo(PERIODI, ["Anna Rossi", "Luca Bianchi"])
        # scala dal 2026-10-16 al 2026-11-16 incluso: 32 giorni
        self.assertIn('data-inizio="2026-10-16" data-fine="2026-11-17"', html)
        self.assertIn('class="barra r-responsabile" style="left:0%;width:56.25%"', html)
        self.assertIn('class="barra r-analista" style="left:56.25%;width:43.75%"', html)
        self.assertIn('title="Analista dal 2026-11-03 al 2026-11-16"', html)
        self.assertIn('<span class="inizio" style="left:0%">2026-10-16</span>', html)
        self.assertIn('<span class="fine" style="left:100%">2026-11-16</span>', html)
        self.assertIn('<span class="mese" style="left:50%">nov 2026</span>', html)
        self.assertIn('aria-hidden="true"', html)

    def test_pagina_ruoli(self):
        html = sito.pagina_ruoli(GRUPPO, None, "#000000", PERIODI)
        self.assertIn('<script id="dati-ruoli" type="application/json">', html)
        self.assertIn('"membro": "Luca Bianchi"', html)
        self.assertIn('<table class="periodi">', html)
        self.assertIn('<li><i class="r-responsabile" aria-hidden="true"></i>Responsabile</li>', html)
        self.assertIn('id="nota-attuali"', html)
        self.assertIn("documenti/interni/ruoli.md", html)
        self.assertIn('<li><a href="#linea">Linea del tempo</a></li>', html)
        self.assertIn('<a href="ruoli.html" aria-current="page">Gruppo</a>', html)
        self.assertIn("<title>Gruppo - Gruppo 42</title>", html)
        self.assertIn("Membri e ruoli attuali", html)
        vuota = sito.pagina_ruoli(GRUPPO, None, "#000000", [])
        self.assertIn("Nessun periodo ancora registrato", vuota)
        self.assertNotIn('class="linea"', vuota)

    def test_pagina_glossario(self):
        voci = [{"termine": "Zeta", "definizione": "ultima"}, {"termine": "alfa", "definizione": "prima", "sinonimi": ["a"]}]
        html = sito.pagina_glossario(GRUPPO, voci, None, "#000000")
        self.assertIn('<ul class="alfabeto"><li><a href="#a">A</a></li><li><a href="#z">Z</a></li></ul>', html)
        self.assertIn('class="sezione lettera" id="a"', html)
        self.assertIn('<dt id="alfa"><span id="a"></span>alfa</dt>', html)
        self.assertIn("Sinonimi: a", html)
        self.assertIn("<li>2 voci</li>", html)
        self.assertIn('<input id="cerca" type="search" autocomplete="off" spellcheck="false">', html)
        self.assertIn("getElementById('cerca')", html)
        self.assertIn('aria-live="polite"', html)
        self.assertIn("<li>1 voce</li>", sito.pagina_glossario(GRUPPO, voci[:1], None, "#000000"))
        vuoto = sito.pagina_glossario(GRUPPO, [], None, "#000000")
        self.assertIn("Nessuna voce ancora presente", vuoto)

    def test_tempo_e_stato(self):
        voce = {"inizio": D(2026, 10, 1), "fine": D(2026, 10, 5)}
        self.assertEqual(sito.tempo(voce, D(2026, 9, 30))["stato"], "Da iniziare")
        self.assertEqual(sito.tempo(voce, D(2026, 10, 2))["dettaglio"], "non iniziata, prevista dal 2026-10-01")
        in_corso = sito.tempo({**voce, "inizio_effettivo": D(2026, 10, 2)}, D(2026, 10, 4))
        self.assertEqual((in_corso["stato"], in_corso["usati"], in_corso["previsti"]), ("In corso", 3, 5))
        tardi = sito.tempo({**voce, "inizio_effettivo": D(2026, 10, 2)}, D(2026, 10, 8))
        self.assertEqual((tardi["stato"], tardi["dettaglio"]), ("In ritardo", "3 giorni oltre la fine prevista"))
        fatta = sito.tempo({**voce, "inizio_effettivo": D(2026, 10, 1), "fine_effettiva": D(2026, 10, 6)}, D(2026, 10, 20))
        self.assertEqual((fatta["stato"], fatta["usati"], fatta["dettaglio"]), ("Conclusa", 6, "1 giorno di ritardo"))
        self.assertEqual(sito.tempo_milestone({"data": D(2026, 10, 5), "data_effettiva": D(2026, 10, 3)}, D(2026, 10, 9)),
                         ("Raggiunta", "2 giorni di anticipo"))
        self.assertEqual(sito.tempo_milestone({"data": D(2026, 10, 5)}, D(2026, 10, 4)), ("Prevista", ""))

    def test_ore_per_fase(self):
        ore = [(D(2026, 10, 1), 2.0), (D(2026, 10, 10), 1.5), (D(2026, 10, 12), 4.0)]
        self.assertEqual(sito.ore_fase(FASI[0], ore), 7.5)  # in corso: conta anche dopo la fine prevista
        self.assertEqual(sito.ore_fase(FASI[1], ore), 0)  # non iniziata
        self.assertEqual(sito.ore_fase({**FASI[0], "fine_effettiva": D(2026, 10, 5)}, ore), 2.0)

    def test_gantt(self):
        # scala dal 2026-10-01 al 2026-10-10 incluso: 10 giorni, 10% al giorno
        html = sito.gantt(FASI[:1], D(2026, 10, 3))
        self.assertIn('<span class="piano" style="left:0%;width:50%" title="Previsto dal 2026-10-01 al 2026-10-05">', html)
        self.assertIn('<span class="reale b-in-corso" style="left:0%;width:30%" title="Effettivo dal 2026-10-01 a oggi">', html)
        self.assertIn('<span class="rombo m-prevista" style="left:95%" title="Invio: 2026-10-10">', html)
        self.assertIn('<span class="oggi-e" style="left:25%">Oggi</span>', html)
        self.assertIn('<span class="oggi-l" style="left:25%"></span>', html)
        # tacca al primo lunedì, il 2026-10-05
        self.assertIn('<span style="left:40%">5 ott</span>', html)
        self.assertIn('<li><div class="chi"><span class="nome">Capitolati</span><span class="info"><span class="stato s-in-corso">'
                      '<span class="icona" aria-hidden="true">●</span> In corso</span> · 3 di 5 giorni</span></div>', html)
        self.assertIn("Prevista</span> · 2026-10-10 · fra 7 giorni", html)
        self.assertIn('<div class="traccia" aria-hidden="true">', html)
        self.assertNotIn('class="fase"', html)
        panoramica = sito.gantt(FASI, D(2026, 12, 1), attivita=False)
        self.assertNotIn("Capitolati", panoramica)
        self.assertIn('<li class="fase"><div class="chi"><span class="nome">RTB</span>', panoramica)
        # milestone non raggiunta e già passata, sulla riga della sua fase
        self.assertIn('<span class="rombo m-in-ritardo"', panoramica)
        self.assertIn('class="oggi-e"', panoramica)

    def test_pagina_pianificazione(self):
        html = sito.pagina_pianificazione(GRUPPO, None, "#000000", FASI, [(D(2026, 10, 2), 2.5)], D(2026, 10, 3))
        self.assertIn('<span class="valore">Candidatura</span><span class="dopo">Giorno 3 di 10, fine prevista il 2026-10-10</span>', html)
        self.assertIn('<i style="width:30%"></i>', html)
        self.assertIn('<span class="valore">Fra 7 giorni</span><span class="dopo">Invio, 2026-10-10</span>', html)
        self.assertIn('<span class="valore">0 di 1 concluse</span><span class="dopo">1 in corso</span>', html)
        self.assertIn('<span class="valore">2,5 h</span><span class="dopo">Ore previste da definire</span>', html)
        self.assertIn("Nessuna attività né milestone in ritardo.", html)
        self.assertIn('<td class="numeri">3 di 10</td><td class="numeri">2,5 di 0</td>', html)
        self.assertIn('<td>Totale</td>', html)
        self.assertIn('<li><a href="#fase-2">RTB</a></li>', html)
        self.assertIn('<a href="pianificazione.html" aria-current="page">Pianificazione</a>', html)
        self.assertIn('<span class="nota-fase">Ore non contabilizzate.</span>', html)
        self.assertIn("<summary>Date previste ed effettive</summary>", html)
        self.assertEqual(sito.stato_progetto(FASI, D(2026, 10, 3)),
                         '<p class="stato-progetto"><span>Fase in corso: <b>Candidatura</b></span>'
                         '<span>Prossima milestone: <b>Invio</b>, 2026-10-10 (fra 7 giorni)</span>'
                         '<a href="cruscotto.html">Cruscotto</a></p>')
        self.assertEqual(sito.stato_progetto([], D(2026, 10, 3)), "")
        in_ritardo = sito.pagina_pianificazione(GRUPPO, None, "#000000", FASI, [], D(2026, 10, 12))
        self.assertIn("<li><b>Capitolati</b> (Candidatura): 7 giorni oltre la fine prevista</li>", in_ritardo)
        self.assertIn("<li><b>Invio</b> (Candidatura): 2 giorni oltre la data prevista</li>", in_ritardo)
        self.assertIn("Nessuna fase ancora pianificata", sito.pagina_pianificazione(GRUPPO, None, "#000000", [], [], D(2026, 10, 3)))
        self.assertIn('<a href="pianificazione.html">Pianificazione</a>', sito.pagina_ruoli(GRUPPO, None, "#000000", PERIODI))

    def test_pagina_documenti(self):
        testata = sito.apertura("G", "k")
        html = sito.pagina_documenti(GRUPPO, None, "#000000", testata, ["lettera"], ([], [], []), (["esterno"], ["interno"]), [])
        # la lettera in cima e in evidenza; le sezioni vuote non compaiono e una riga le elenca
        self.assertLess(html.index('id="lettere"'), html.index('id="verbali"'))
        self.assertIn('<section class="sezione in-evidenza" id="lettere"', html)
        self.assertNotIn('id="documenti"', html)
        self.assertNotIn('id="diari"', html)
        self.assertIn('<p class="nota">Ancora da pubblicare: documenti e diari di bordo.</p>', html)
        self.assertIn('<p class="titoletto" aria-hidden="true">In questa pagina</p>'
                      '<ol><li><a href="#lettere">Lettere</a></li><li><a href="#verbali">Verbali</a></li></ol>', html)
        self.assertIn('<h3>Esterni</h3><ol class="voci"><li class="voce">esterno</li></ol><h3>Interni</h3>', html)
        # la ricerca compare solo con lo script
        self.assertIn('<div class="cerca" hidden><label for="cerca">Cerca tra i documenti</label>', html)
        self.assertIn("getElementById('cerca')", html)
        # i membri stanno nella pagina Gruppo
        self.assertNotIn("data-membro", html)
        vuota = sito.pagina_documenti(GRUPPO, None, "#000000", testata, [], ([], [], []), ([], []), [])
        self.assertIn("Ancora da pubblicare: lettere di presentazione, documenti, verbali e diari di bordo.", vuota)
        self.assertNotIn('class="cerca"', vuota)
        self.assertNotIn('class="colonne"', vuota)

    def test_numeri_e_tacche(self):
        self.assertEqual(sito.euro(12600.5), "12.600,50\u00a0€")
        self.assertEqual(sito.euro(0), "0,00\u00a0€")
        self.assertEqual(sito.ore_h(12.345), "12,3\u00a0h")
        self.assertEqual(sito.percento(-500 / 90, segno=True), "\u22125,6%")
        self.assertEqual(sito.percento(1875 / 3500 * 100), "54%")
        self.assertEqual(sito.tacche(180), [0, 50, 100, 150, 200])
        self.assertEqual(sito.tacche(12.5), [0, 5, 10, 15])
        self.assertEqual(sito.tacche(540), [0, 200, 400, 600])

    def test_ore_previste_e_conti(self):
        self.assertEqual(sito.ore_previste_al(FASI_ORE, D(2026, 10, 15)), 0)
        self.assertEqual(sito.ore_previste_al(FASI_ORE, OGGI), 90)
        self.assertEqual(sito.ore_previste_al(FASI_ORE, D(2026, 12, 1)), 180)
        # una fase già iniziata senza ore previste rende ignoto il previsto da quel giorno
        con_pb = FASI_ORE + [{"nome": "PB", "inizio": D(2026, 11, 5), "fine": D(2026, 11, 30)}]
        self.assertEqual(sito.ore_previste_al(con_pb, D(2026, 11, 4)), 180)
        self.assertIsNone(sito.ore_previste_al(con_pb, D(2026, 11, 5)))
        c = sito.conti(ORE, PREVENTIVO)
        self.assertEqual((c["ore_preventivo"], c["costo_preventivo"], c["ore_consuntivo"], c["costo_consuntivo"]), (180, 3500, 85, 1875))
        self.assertEqual(c["preventivo_membro"], {"Anna Rossi": 90, "Luca Bianchi": 90})
        self.assertEqual(c["consuntivo_ruolo"]["Verificatore"], 45)
        vuoto = sito.conti([], {})
        self.assertEqual((vuoto["ore_preventivo"], vuoto["costo_consuntivo"]), (0, 0))

    def test_controlli_ed_esito(self):
        risultati = sito.controlli(GRUPPO, FASI_ORE, ORE, sito.conti(ORE, PREVENTIVO), OGGI)
        self.assertEqual([(n, s) for n, s, _, _ in risultati],
                         [("Costo", "Sotto controllo"), ("Ore rispetto al previsto", "Sotto controllo"), ("Tempi", "Fuori soglia"),
                          ("Ore per membro", "Sotto controllo")])
        valori = [v for _, _, v, _ in risultati]
        self.assertEqual(valori[0], "1.875,00\u00a0€ di 3.500,00\u00a0€, il 54%.")
        self.assertEqual(valori[1], "85\u00a0h consumate e 90\u00a0h previste a oggi: \u22125,6%.")
        self.assertIn('1 voce in ritardo: Analisi. <a href="pianificazione.html#situazione">', valori[2])
        self.assertEqual(valori[3], "Al massimo 45\u00a0h per membro.")
        self.assertEqual(risultati[1][3], "scostamento entro ±10% dalle ore previste a oggi.")
        self.assertIn("Fuori soglia</span>: 1 indicatore su 4 (tempi).", sito.esito(risultati))
        # costo aggiudicato superato, soglia più stretta, un membro oltre la sua ripartizione
        gruppo = {**GRUPPO, "progetto": {"costo_aggiudicato": 1800.0}, "soglie": {"scostamento_ore": 5}}
        troppe = ORE + [(D(2026, 10, 23), 60.0, "Anna Rossi", "Responsabile")]
        risultati = sito.controlli(gruppo, FASI_ORE, troppe, sito.conti(troppe, PREVENTIVO), OGGI)
        self.assertEqual({s for _, s, _, _ in risultati}, {"Fuori soglia"})
        self.assertEqual(risultati[0][3], "il costo consuntivo non supera il costo aggiudicato.")
        self.assertEqual(risultati[3][2], "Oltre il limite: Anna Rossi.")
        self.assertIn("4 indicatori su 4 (costo, ore rispetto al previsto, tempi, ore per membro).", sito.esito(risultati))
        vuoti = sito.controlli({"gruppo": {}}, [], [], sito.conti([], {}), OGGI)
        self.assertEqual({s for _, s, _, _ in vuoti}, {"Da misurare"})
        self.assertIn("Da misurare</span>: nessun indicatore ha ancora i dati che servono.", sito.esito(vuoti))
        self.assertIn("tutti e 2 gli indicatori sono nella soglia.", sito.esito([("A", "Sotto controllo", "", "")] * 2))
        self.assertIn("1 indicatore su 2 nella soglia, 1 ancora da misurare.",
                      sito.esito([("A", "Sotto controllo", "", ""), ("B", "Da misurare", "", "")]))

    def test_grafico_ore(self):
        html = sito.grafico_ore(FASI_ORE, ORE, 180, OGGI)
        # 20 giorni dal 2026-10-16 e asse fino a 200 ore: x = giorni / 20, y = ore / 200; un punto ogni 7 giorni più oggi
        self.assertIn('<polyline class="l-previste" points="0,100 35,68.5 50,55 70,37 100,10"', html)
        self.assertIn('<polyline class="l-consumate" points="0,100 35,57.5 50,57.5"', html)
        self.assertIn('<span class="tacca-y" style="bottom:25%"><b>50</b></span>', html)
        self.assertIn('<span class="rif-g" style="bottom:90%"><span>Preventivo 180\u00a0h</span></span>', html)
        self.assertIn('<span class="oggi-g" style="left:50%"></span><span class="punto-g" style="left:50%;bottom:42.5%"></span>', html)
        self.assertIn("&quot;al&quot;: &quot;Al 2026-10-22&quot;, &quot;p&quot;: &quot;63\u00a0h&quot;, &quot;c&quot;: &quot;85\u00a0h&quot;", html)
        self.assertIn("&quot;al&quot;: &quot;Al 2026-10-29&quot;, &quot;p&quot;: &quot;126\u00a0h&quot;, &quot;c&quot;: null", html)
        self.assertIn("Al 2026-10-25: 85\u00a0h consumate e 90\u00a0h previste, su 180\u00a0h del preventivo.", html)
        self.assertIn('<td class="data">2026-11-04</td><td class="numeri">180\u00a0h</td><td class="numeri">—</td>', html)
        self.assertEqual(sito.grafico_ore(FASI[:1], [], 0, OGGI), "")

    def test_consuntivo_periodi(self):
        ore = ORE + [(D(2026, 11, 5), 6.0, "Luca Bianchi", "Analista")]
        html = sito.consuntivo_periodi(PERIODI, ore, PREVENTIVO["tariffe"], OGGI)
        self.assertIn('<td class="data"><span>2026-10-16</span> <span>→ 2026-11-02</span></td><td><span class="stato s-in-corso">', html)
        self.assertIn('In corso</span></td><td class="numeri">85\u00a0h</td><td class="numeri">1.875,00\u00a0€</td>', html)
        # l'ora del 2026-11-05 conta nel periodo di Luca Bianchi da Analista
        self.assertIn('Da iniziare</span></td><td class="numeri">6\u00a0h</td><td class="numeri">150,00\u00a0€</td>', html)

    def test_pagina_cruscotto(self):
        html = sito.pagina_cruscotto(GRUPPO, None, "#000000", FASI_ORE, ORE, PREVENTIVO, PERIODI, OGGI)
        self.assertIn('<a href="cruscotto.html" aria-current="page">Cruscotto</a>', html)
        for identificatore in ("controllo", "ore-e-costi", "andamento", "avanzamento", "periodi"):
            self.assertIn(f'<li><a href="#{identificatore}">', html)
        self.assertIn('<span class="etichetta">Tempi</span><span class="valore"><span class="stato s-fuori-soglia">', html)
        self.assertIn('<span class="soglia">Soglia: il costo consuntivo non supera il costo preventivato.</span>', html)
        self.assertIn('<td><span class="ruolo r-responsabile">Responsabile</span></td><td class="numeri">30 €/h</td>'
                      '<td class="numeri">20\u00a0h</td><td class="numeri">40\u00a0h</td>', html)
        self.assertIn('<tr><td>Anna Rossi</td><td class="numeri">90\u00a0h</td><td class="numeri">40\u00a0h</td>'
                      '<td class="numeri">50\u00a0h</td><td class="numeri">44%', html)
        self.assertIn('<td>RTB</td><td class="numeri">0 di 1</td><td class="numeri">0 di 1</td>', html)
        self.assertIn("getAttribute('data-punti')", html)
        vuota = sito.pagina_cruscotto(GRUPPO, None, "#000000", [], [], {}, [], OGGI)
        self.assertIn("Il grafico compare quando", vuota)
        self.assertIn("La ripartizione delle ore di dati/preventivo.toml è ancora vuota", vuota)
        self.assertNotIn("<h3>Per ruolo</h3>", vuota)  # senza preventivo né ore le tabelle sarebbero solo zeri
        self.assertIn("Nessun periodo ancora registrato in dati/ruoli.csv", vuota)
        self.assertNotIn("data-punti", vuota)

    def test_json_non_chiude_lo_script(self):
        html = sito.pagina("T", "", "", {"gruppo": {}}, None, "#000000", dati={"periodi": [{"membro": "</script>"}]})
        self.assertNotIn("</script>\"", html)
        self.assertIn('<\\/script>', html)


if __name__ == "__main__":
    unittest.main()
