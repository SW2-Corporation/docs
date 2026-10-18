import unittest

import sito

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

    def test_pagina_senza_logo_e_senza_laterale(self):
        html = sito.pagina("Titolo", sito.apertura("G", "k"), "<p>c</p>", {"gruppo": {}}, None, "#000000")
        self.assertNotIn("<img", html)
        self.assertNotIn('rel="icon"', html)
        self.assertNotIn("dati-ruoli", html)
        self.assertNotIn('class="colonne"', html)
        con = sito.pagina("T", "", "<p>c</p>", {"gruppo": {}}, None, "#000000", laterale=sito.indice([("#a", "01", "A")]))
        self.assertIn('<div class="colonne"><nav class="indice" aria-label="Sezioni">', con)

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
        self.assertIn("(si apre in una nuova scheda)", riga)
        self.assertIn('<span class="dettaglio">PDF</span>', sito.voce("a.pdf", "Doc"))
        self.assertNotIn('<span class="sr-only"> del', sito.voce("a.pdf", "Doc"))
        con_data = sito.voce("v.pdf", "Verbale interno", "2026-10-14", nascosto=" del 2026-10-14")
        self.assertIn('>Verbale interno<span class="sr-only"> del 2026-10-14</span><span class="sr-only"> (si apre', con_data)
        self.assertIn('<p class="vuoto">vuoto &amp; basta</p>', sito.elenco([], "vuoto & basta"))
        self.assertIn('<ol class="voci"><li class="voce">riga</li></ol>', sito.elenco(["riga"], "vuoto"))

    def test_sezione_e_indice(self):
        html = sito.sezione("id", "02", "A & B", "<p>c</p>", 3)
        self.assertIn('<section class="sezione" id="id" aria-labelledby="titolo-id">', html)
        self.assertIn('<h2 id="titolo-id"><span class="num" aria-hidden="true">02</span>A &amp; B', html)
        self.assertIn('<span class="sr-only">Elementi: </span>3</span>', html)
        nav = sito.indice([("#a", "01", "Uno")], [("altra.html", "Altra")])
        self.assertIn('<li><a href="#a"><span class="n">01</span><span>Uno</span></a></li>', nav)
        self.assertIn('<ul class="pagine"><li><a href="altra.html">Altra</a></li></ul>', nav)

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
        self.assertIn('<a href="#linea"><span class="n">02</span>', html)
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
        vuoto = sito.pagina_glossario(GRUPPO, [], None, "#000000")
        self.assertIn("Nessuna voce ancora presente", vuoto)

    def test_json_non_chiude_lo_script(self):
        html = sito.pagina("T", "", "", {"gruppo": {}}, None, "#000000", dati={"periodi": [{"membro": "</script>"}]})
        self.assertNotIn("</script>\"", html)
        self.assertIn('<\\/script>', html)


if __name__ == "__main__":
    unittest.main()
