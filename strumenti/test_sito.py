import unittest

import sito

GRUPPO = {"gruppo": {"nome": "Gruppo Prova", "repo": "https://github.com/prova/docs"},
          "membro": [{"nome": "Anna", "cognome": "Rossi", "github": "annarossi"},
                     {"nome": "Luca", "cognome": "Bianchi", "github": ""}]}
PERIODI = [{"inizio": "2026-10-16", "fine": "2026-11-02", "membro": "Anna Rossi", "ruolo": "Responsabile"},
           {"inizio": "2026-10-16", "fine": "2026-11-02", "membro": "Luca Bianchi", "ruolo": "Verificatore"},
           {"inizio": "2026-11-03", "fine": "2026-11-16", "membro": "Luca Bianchi", "ruolo": "Analista"}]


class TestSito(unittest.TestCase):
    def test_pagina_ha_logo_e_colore(self):
        testata = sito.intestazione("Gruppo Prova", "sotto", "logo.png", [sito.chip("x@y.it", "mail", "mailto:x@y.it")])
        html = sito.pagina("Titolo", testata, "<p>corpo</p>", GRUPPO, "logo.png", "#123456")
        self.assertIn('<img class="logo" src="logo.png" alt="">', html)
        self.assertIn('rel="icon" type="image/png" href="logo.png"', html)
        self.assertIn("--accento: #123456;", html)
        self.assertIn('href="mailto:x@y.it"', html)
        self.assertIn("Sorgenti su GitHub", html)

    def test_pagina_senza_logo(self):
        html = sito.pagina("Titolo", sito.intestazione("G", "s", None), "", {"gruppo": {}}, None, "#000000")
        self.assertNotIn("<img", html)
        self.assertNotIn('rel="icon"', html)
        self.assertNotIn("dati-ruoli", html)

    def test_accessibilita_e_temi(self):
        html = sito.pagina("Titolo", sito.intestazione("G", "s", None, menu=[("#a", "A")]), "", {"gruppo": {}}, None, "#000000")
        self.assertIn('<html lang="it">', html)
        self.assertIn('<a class="salta" href="#contenuto">', html)
        self.assertIn('<main class="dentro" id="contenuto" tabindex="-1">', html)
        self.assertIn('<nav class="menu" aria-label="Sezioni">', html)
        self.assertIn('<button class="tema" type="button" aria-pressed="false" aria-label="Passa al tema scuro">', html)
        self.assertIn("localStorage.getItem('tema')", html)
        self.assertIn('@media (prefers-color-scheme: dark) { :root:not([data-theme="light"])', html)
        self.assertIn(':root[data-theme="dark"]', html)
        self.assertNotIn("{scuro}", html)
        # la fascia in testa segue il tema: chiara nel tema chiaro, scura in quello scuro
        self.assertIn("--fascia: #ffffff;", html)
        self.assertIn("--fascia: #0e0e10;", html)
        self.assertIn(".hero { position: relative; background: var(--fascia);", html)
        self.assertIn('meta[name="theme-color"]', html)

    def test_persona_con_e_senza_github(self):
        con, senza = (sito.persona(m) for m in GRUPPO["membro"])
        self.assertIn('href="https://github.com/annarossi"', con)
        self.assertIn("annarossi.png", con)
        self.assertIn("nuova scheda", con)
        self.assertNotIn("data-membro", con)
        self.assertNotIn("<img", senza)
        self.assertIn('<span class="iniziali" aria-hidden="true">LB</span>', senza)
        con_ruolo = sito.persona(GRUPPO["membro"][0], con_ruolo=True)
        self.assertIn('data-membro="Anna Rossi"', con_ruolo)
        self.assertIn('<span class="ruolo" hidden></span>', con_ruolo)

    def test_voce_ed_elenco(self):
        riga = sito.voce("a.pdf", "Doc", "v1.0.0 · 2026-10-29")
        self.assertIn('<span class="meta">v1.0.0 · 2026-10-29</span>', riga)
        self.assertIn("(si apre in una nuova scheda)", riga)
        self.assertNotIn("meta", sito.voce("a.pdf", "Doc"))
        self.assertIn('class="nota"', sito.elenco([], "vuoto & basta"))
        self.assertIn("vuoto &amp; basta", sito.elenco([], "vuoto & basta"))
        self.assertIn("<li>riga</li>", sito.elenco(["riga"], "vuoto"))

    def test_chip_esterno_e_interno(self):
        self.assertIn('target="_blank"', sito.chip("Repo", "repo", "https://github.com/x"))
        interno = sito.chip("Indice", "indietro", "index.html")
        self.assertNotIn("target", interno)
        self.assertNotIn("nuova scheda", interno)

    def test_scheda_escapa_titolo_e_conta(self):
        html = sito.scheda("id", "A & B", "<p>c</p>", 3, larga=True)
        self.assertIn('class="scheda larga" id="id" aria-labelledby="titolo-id"', html)
        self.assertIn('<h2 id="titolo-id">A &amp; B', html)
        self.assertIn('<span class="sr-only">Elementi: </span>3</span>', html)

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
        html = sito.ruoli(GRUPPO, None, "#000000", PERIODI)
        self.assertIn('<script id="dati-ruoli" type="application/json">', html)
        self.assertIn('"membro": "Luca Bianchi"', html)
        self.assertIn('<table class="periodi">', html)
        self.assertIn('<li><i class="r-responsabile" aria-hidden="true"></i>Responsabile</li>', html)
        self.assertIn('id="nota-attuali"', html)
        self.assertIn("documenti/interni/ruoli.md", html)
        vuota = sito.ruoli(GRUPPO, None, "#000000", [])
        self.assertIn("Nessun periodo ancora registrato", vuota)
        self.assertNotIn('class="linea"', vuota)

    def test_json_non_chiude_lo_script(self):
        html = sito.pagina("T", "", "", {"gruppo": {}}, None, "#000000", dati={"periodi": [{"membro": "</script>"}]})
        self.assertNotIn("</script>\"", html)
        self.assertIn('<\\/script>', html)


if __name__ == "__main__":
    unittest.main()
