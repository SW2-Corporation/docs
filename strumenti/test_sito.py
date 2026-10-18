import unittest

import sito

GRUPPO = {"gruppo": {"nome": "Gruppo Prova", "repo": "https://github.com/prova/docs"},
          "membro": [{"nome": "Anna", "cognome": "Rossi", "github": "annarossi"},
                     {"nome": "Luca", "cognome": "Bianchi", "github": ""}]}


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

    def test_accessibilita_della_pagina(self):
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

    def test_persona_con_e_senza_github(self):
        con, senza = (sito.persona(m) for m in GRUPPO["membro"])
        self.assertIn('href="https://github.com/annarossi"', con)
        self.assertIn("annarossi.png", con)
        self.assertIn("nuova scheda", con)
        self.assertNotIn("<img", senza)
        self.assertIn('<span class="iniziali" aria-hidden="true">LB</span>', senza)

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


if __name__ == "__main__":
    unittest.main()
