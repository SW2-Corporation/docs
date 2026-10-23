import datetime
import unittest

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
        self.assertIn('<nav class="menu" aria-label="Pagine del sito"><ul><li><a href="index.html">Documenti</a></li>', html)
        self.assertIn('<li><a href="ruoli.html" aria-current="page">Ruoli</a></li>', html)
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
        riga = sito.voce("a.pdf", "Doc", "v1.0.0 · 2026-10-29")
        self.assertIn('<span class="dettaglio">v1.0.0 · 2026-10-29 · PDF</span>', riga)
        self.assertIn('<span class="puntini" aria-hidden="true"></span>', riga)
        # il titolo apre la pagina di lettura del PDF, nella stessa scheda
        self.assertIn('<a href="a.html">Doc</a>', riga)
        self.assertNotIn("nuova scheda", riga)
        self.assertIn('<span class="dettaglio">PDF</span>', sito.voce("a.pdf", "Doc"))
        self.assertNotIn('<span class="sr-only"> del', sito.voce("a.pdf", "Doc"))
        con_data = sito.voce("v.pdf", "Verbale interno", "2026-10-14", nascosto=" del 2026-10-14")
        self.assertIn('<a href="v.html">Verbale interno<span class="sr-only"> del 2026-10-14</span></a>', con_data)
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
        self.assertTrue(riga.endswith('<span class="sotto-voce"><b>stato</b></span>'))
        self.assertNotIn("sotto-voce", sito.voce("v.pdf", "Doc"))

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
        self.assertIn('<a href="ruoli.html" aria-current="page">Ruoli</a>', html)
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
                         '<a href="pianificazione.html">Pianificazione</a></p>')
        self.assertEqual(sito.stato_progetto([], D(2026, 10, 3)), "")
        in_ritardo = sito.pagina_pianificazione(GRUPPO, None, "#000000", FASI, [], D(2026, 10, 12))
        self.assertIn("<li><b>Capitolati</b> (Candidatura): 7 giorni oltre la fine prevista</li>", in_ritardo)
        self.assertIn("<li><b>Invio</b> (Candidatura): 2 giorni oltre la data prevista</li>", in_ritardo)
        self.assertIn("Nessuna fase ancora pianificata", sito.pagina_pianificazione(GRUPPO, None, "#000000", [], [], D(2026, 10, 3)))
        self.assertIn('<a href="pianificazione.html">Pianificazione</a>', sito.pagina_ruoli(GRUPPO, None, "#000000", PERIODI))

    def test_json_non_chiude_lo_script(self):
        html = sito.pagina("T", "", "", {"gruppo": {}}, None, "#000000", dati={"periodi": [{"membro": "</script>"}]})
        self.assertNotIn("</script>\"", html)
        self.assertIn('<\\/script>', html)


if __name__ == "__main__":
    unittest.main()
