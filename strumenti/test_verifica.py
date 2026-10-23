import shutil
import tempfile
import textwrap
import unittest
from pathlib import Path

from verifica import Verifica, gulpease, testo_leggibile

GRUPPO = """\
[gruppo]
nome = "Gruppo di prova"
email = "gruppo@example.com"
logo = ""
sito = "https://gruppo.github.io/docs/"
repo = ""

[progetto]
capitolato = ""
proponente = ""
costo_aggiudicato = 0.0
consegna_prevista = ""

[soglie]
gulpease = 40

[[membro]]
nome = "Anna"
cognome = "Bianchi"
github = "abianchi"

[[membro]]
nome = "Marco"
cognome = "Rossi"
github = "mrossi"

[[membro]]
nome = "Luca"
cognome = "Verdi"
github = "lverdi"
"""

RUOLI = """\
inizio,fine,membro,ruolo
2026-10-01,2026-10-31,Anna Bianchi,Responsabile
2026-10-01,2026-10-31,Marco Rossi,Verificatore
2026-10-01,2026-10-31,Luca Verdi,Analista
"""

TARIFFE = """\
[tariffe]
Responsabile = 30
Amministratore = 20
Analista = 25
Progettista = 25
Programmatore = 15
Verificatore = 15
"""

GLOSSARIO = """\
[[voce]]
termine = "Proof of Concept"
definizione = "Prototipo che dimostra la fattibilità delle tecnologie."
sinonimi = ["PoC"]

[[voce]]
termine = "Sprint"
definizione = "Periodo di lavoro di durata fissa."
"""

VERBALE = """\
tipo = "interno"
data = 2026-10-14
inizio = "18:00"
fine = "19:00"
luogo = "Discord"
redattore = "Anna Bianchi"
verificatore = "Marco Rossi"
partecipanti = ["Anna Bianchi", "Marco Rossi", "Luca Verdi"]
ordine_del_giorno = ["Scelta del capitolato", "Organizzazione dei ruoli"]

[[punto]]
titolo = "Scelta del capitolato"
sintesi = "Il gruppo confronta i capitolati."

[[decisione]]
id = "VI-2026-10-14.1"
testo = "Candidatura per il capitolato C9."
motivazione = "Interesse comune per il dominio."

[[azione]]
decisione = "VI-2026-10-14.1"
descrizione = "Preparare la valutazione dei capitolati."
assegnatario = "Luca Verdi"
scadenza = 2026-10-20
issue = "https://github.com/gruppo/docs/issues/1"
"""


def documento(corpo, nome="prova"):
    return (
        '#import "/modello/documento.typ": documento\n'
        f'#show: documento.with(titolo: "Prova", registro: csv("{nome}.registro.csv"))\n\n'
        + textwrap.dedent(corpo)
    )


def registro(*righe):
    return "versione,data,autore,verificatore,descrizione\n" + "".join(r + "\n" for r in righe)


RILASCIATO = registro(
    "1.0.0,2026-10-28,Anna Bianchi,,Approvazione per il rilascio",
    "0.2.0,2026-10-25,Luca Verdi,Marco Rossi,Stesura della sezione 2",
    "0.1.0,2026-10-20,Luca Verdi,Marco Rossi,Prima stesura",
)


class Base(unittest.TestCase):
    def setUp(self):
        self.radice = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.radice)
        self.scrivi("dati/gruppo.toml", GRUPPO)
        self.scrivi("dati/ruoli.csv", RUOLI)
        self.scrivi("dati/ore.csv", "data,membro,ruolo,ore,riferimento\n")
        self.scrivi("dati/preventivo.toml", TARIFFE)
        self.scrivi("dati/glossario.toml", GLOSSARIO)
        self.scrivi("dati/maiuscole.txt", "Norme di Progetto\nPadova\n")

    def scrivi(self, rel, testo):
        percorso = self.radice / rel
        percorso.parent.mkdir(parents=True, exist_ok=True)
        percorso.write_text(testo, encoding="utf-8")

    def problemi(self, *percorsi):
        return Verifica(self.radice).esegui([self.radice / p for p in percorsi] or None)

    def codici(self, *percorsi):
        return [codice for _, _, codice, _ in self.problemi(*percorsi)]

    def doc(self, corpo, registro_csv=registro("0.1.0,2026-10-20,Luca Verdi,Marco Rossi,Prima stesura")):
        self.scrivi("documenti/interni/prova.typ", documento(corpo))
        self.scrivi("documenti/interni/prova.registro.csv", registro_csv)


class TestBase(Base):
    def test_repo_minimo_senza_problemi(self):
        self.doc("= Introduzione\nTesto del documento.\n")
        self.scrivi("documenti/verbali/interni/2026-10-14.toml", VERBALE)
        self.assertEqual(self.problemi(), [])

    def test_formato_e_percorsi_indicati(self):
        self.doc("= Introduzione\nIl 14/10/2026 il gruppo si riunisce.\n")
        self.scrivi("documenti/interni/altro.typ", "= Altro\nTesto.\n")
        self.assertEqual(self.codici("documenti/interni/altro.typ"), [])
        percorso, riga, codice, _ = self.problemi("documenti/interni/prova.typ")[0]
        self.assertEqual((percorso, riga, codice), ("documenti/interni/prova.typ", 5, "E-DATA-TESTO"))


class TestDate(Base):
    def test_date_iso_e_versioni_ammesse(self):
        self.doc("= Introduzione\nIl 2026-10-14 esce la versione 1.0.10 (a.a. 2026/27).\n")
        self.assertEqual(self.codici(), [])

    def test_date_in_altri_formati(self):
        self.doc("= Introduzione\nRiunione del 14/10/2026, poi del 15-10-26 e del 16 ottobre 2026.\n")
        self.assertEqual(self.codici().count("E-DATA-TESTO"), 3)

    def test_nomi_di_file(self):
        self.scrivi("documenti/verbali/interni/14-10-2026.toml", VERBALE)
        self.scrivi("documenti/lettere/presentazione.typ", "Testo.\n")
        codici = self.codici()
        self.assertEqual(codici.count("E-DATA-FILE"), 2)


class TestMaiuscole(Base):
    def test_titoli_corretti(self):
        self.doc("= Uso di GitHub e delle Norme di Progetto\n== Analisi CI/CD a Padova\n")
        self.assertEqual(self.codici(), [])

    def test_titoli_errati(self):
        self.doc("= Analisi Dei rischi\n== analisi dei costi\n")
        self.assertEqual(self.codici().count("E-MAIUSCOLE"), 2)

    def test_ordine_del_giorno(self):
        self.scrivi("documenti/verbali/interni/2026-10-14.toml",
                    VERBALE.replace('"Organizzazione dei ruoli"', '"Organizzazione Dei Ruoli"'))
        self.assertEqual(self.codici().count("E-MAIUSCOLE"), 2)


class TestLessico(Base):
    def test_testo_corretto(self):
        self.doc("= Introduzione\nLo scopo è definire i requisiti dello sprint.\n")
        self.assertEqual(self.codici(), [])

    def test_espressioni_vietate(self):
        self.doc("= Introduzione\nLo scopo è quello di far girare il codice nella sprint.\n")
        problemi = [m for _, _, c, m in self.problemi() if c == "E-LESSICO"]
        self.assertEqual(len(problemi), 3)
        self.assertTrue(any('"nello sprint"' in m for m in problemi))


class TestRegistro(Base):
    def test_registro_corretto(self):
        self.doc("= Introduzione\nTesto.\n", registro(
            "1.0.1,2026-10-29,Luca Verdi,Marco Rossi,Correzione della sezione 1",
            "1.0.0,2026-10-28,Anna Bianchi,,Approvazione per il rilascio",
            "0.2.0,2026-10-25,Luca Verdi,Marco Rossi,Stesura della sezione 2",
            "0.1.1,2026-10-22,Anna Bianchi,Marco Rossi,Correzioni",
            "0.1.0,2026-10-20,Luca Verdi,Marco Rossi,Prima stesura",
        ))
        self.assertEqual(self.codici(), [])

    def test_incrementi_errati(self):
        self.doc("Testo.\n", registro(
            "0.3.1,2026-10-25,Luca Verdi,Marco Rossi,Seconda modifica",
            "0.1.0,2026-10-20,Luca Verdi,Marco Rossi,Prima stesura",
        ))
        self.assertIn("E-REGISTRO-VERSIONE", self.codici())

    def test_approvazioni_errate(self):
        self.doc("Testo.\n", registro(
            "2.0.0,2026-10-28,Anna Bianchi,,Approvazione ripetuta",
            "1.0.0,2026-10-27,Anna Bianchi,Marco Rossi,Approvazione con verificatore",
            "0.1.0,2026-10-20,Luca Verdi,Marco Rossi,Prima stesura",
        ))
        self.assertEqual(self.codici().count("E-REGISTRO-APPROVAZIONE"), 2)

    def test_autore_uguale_al_verificatore(self):
        self.doc("Testo.\n", registro("0.1.0,2026-10-20,Marco Rossi,Marco Rossi,Prima stesura"))
        self.assertIn("E-REGISTRO-AUTORE", self.codici())

    def test_ordine_non_lifo(self):
        self.doc("Testo.\n", registro(
            "0.1.0,2026-10-20,Luca Verdi,Marco Rossi,Prima stesura",
            "0.2.0,2026-10-25,Luca Verdi,Marco Rossi,Seconda stesura",
        ))
        codici = self.codici()
        self.assertIn("E-REGISTRO-ORDINE", codici)
        self.assertIn("E-REGISTRO-INIZIO", codici)

    def test_intestazione_e_date(self):
        self.doc("Testo.\n", "versione,data,autore,descrizione\n")
        self.assertEqual(self.codici(), ["E-REGISTRO-INTESTAZIONE"])
        self.doc("Testo.\n", registro("0.1.0,20/10/2026,Luca Verdi,Marco Rossi,Prima stesura"))
        self.assertIn("E-REGISTRO-DATA", self.codici())

    def test_ruoli_in_carica(self):
        self.doc("Testo.\n", registro(
            "1.0.0,2026-10-28,Luca Verdi,,Approvazione per il rilascio",
            "0.1.0,2026-10-20,Anna Bianchi,Luca Verdi,Prima stesura",
        ))
        self.assertEqual(self.codici(), ["W-REGISTRO-RUOLO", "W-REGISTRO-RUOLO"])

    def test_registro_mancante(self):
        self.scrivi("documenti/interni/prova.typ", documento("Testo.\n"))
        self.assertEqual(self.codici(), ["E-REGISTRO-MANCANTE"])


class TestRegistroVietato(Base):
    def test_lettera_senza_registro(self):
        self.scrivi("documenti/lettere/2026-10-30.typ", '#show: lettera.with(data: "2026-10-30")\nTesto.\n')
        self.assertEqual(self.codici(), [])

    def test_registro_in_lettere_e_verbali(self):
        self.scrivi("documenti/lettere/2026-10-30.typ", "= Registro delle modifiche\n")
        self.scrivi("documenti/verbali/interni/2026-10-14.registro.csv", registro())
        self.assertEqual(self.codici().count("E-REGISTRO-VIETATO"), 2)


class TestRiferimenti(Base):
    def test_riferimenti_corretti(self):
        self.doc("""\
            = Riferimenti
            == Riferimenti normativi
            - #rif-web(
                "Regolamento del progetto didattico",
                "https://www.math.unipd.it/~tullio/IS-1/2026/Dispense/PD1.pdf",
                "2026-10-14",
              )
            == Riferimenti informativi
            - Standard ISO/IEC 12207:1995.
            """)
        self.assertEqual(self.codici(), [])

    def test_riferimenti_errati(self):
        self.doc("""\
            = Riferimenti normativi
            - Regolamento: https://www.math.unipd.it/~tullio/IS-1/2026/Dispense/PD1.pdf
            - #rif-web("Capitolato C9", "https://www.math.unipd.it/~tullio/IS-1/2026/Progetto/C9.pdf")
            - Standard ISO/IEC 12207:1995.
            """)
        self.assertEqual(self.codici().count("E-RIFERIMENTI"), 3)


class TestFigura(Base):
    def test_tabelle_e_immagini_in_figure(self):
        self.doc("""\
            = Introduzione
            #figure(table(columns: 2, [a], [b]), caption: [Prova])
            #figure(caption: [Schema])[#image("schema.png")]
            """)
        self.scrivi("modello/stile.typ", "#table(columns: 1, [x])\n")
        self.assertEqual(self.codici(), [])

    def test_tabella_fuori_da_figure(self):
        self.doc("= Introduzione\n#table(columns: 2, [a], [b])\n")
        self.assertEqual(self.codici(), ["E-FIGURA"])


class TestGlossario(Base):
    def test_termini_noti(self):
        self.doc('= Introduzione\nIl #g("Proof of Concept") precede lo #g("sprint").\n')
        self.assertEqual(self.codici(), [])

    def test_termini_errati(self):
        self.doc('= Uso del #g("PoC")\nIl #g("Kanban") e il #g("Proof of Concept") e il #g("PoC").\n')
        codici = self.codici()
        self.assertEqual(codici.count("E-GLOSSARIO"), 2)
        self.assertEqual(codici.count("W-GLOSSARIO"), 1)


class TestVerbale(Base):
    def verbale(self, testo, cartella="interni", nome="2026-10-14"):
        self.scrivi(f"documenti/verbali/{cartella}/{nome}.toml", testo)
        return self.codici()

    def test_verbale_esterno_corretto(self):
        testo = (VERBALE.replace('"interno"', '"esterno"').replace("VI-", "VE-")
                 .replace('ordine_del_giorno', 'esterni = [{ nome = "Mario Neri", ruolo = "Referente", azienda = "Zucchetti" }]\n'
                          'approvazione_esterna = "Approvato via email il 2026-10-16"\nordine_del_giorno'))
        self.assertEqual(self.verbale(testo, "esterni"), [])

    def test_titolo_facoltativo(self):
        con_titolo = VERBALE.replace('tipo = "interno"', 'tipo = "interno"\ntitolo = "Scelta del capitolato"')
        self.assertEqual(self.verbale(con_titolo), [])
        errato = con_titolo.replace('titolo = "Scelta del capitolato"', 'titolo = "Scelta del Capitolato"')
        self.assertEqual(self.verbale(errato), ["E-MAIUSCOLE"])

    def test_schema(self):
        codici = self.verbale(VERBALE.replace('luogo = "Discord"', 'sede = "Discord"'))
        self.assertEqual(codici.count("E-VERBALE-SCHEMA"), 2)

    def test_tipo_data_orari(self):
        testo = VERBALE.replace('fine = "19:00"', 'fine = "17:30"')
        codici = self.verbale(testo, "esterni", "2026-10-15")
        for codice in ("E-VERBALE-TIPO", "E-VERBALE-DATA", "E-VERBALE-ORARIO"):
            self.assertIn(codice, codici)

    def test_decisioni_e_azioni(self):
        testo = (VERBALE.replace('decisione = "VI-2026-10-14.1"', 'decisione = "VI-2026-10-14.2"')
                 .replace('"Luca Verdi"\nscadenza = 2026-10-20', '"tutti"\nscadenza = 2026-10-10')
                 .replace('issue = "https://github.com/gruppo/docs/issues/1"', 'issue = ""'))
        codici = self.verbale(testo)
        self.assertEqual(codici.count("E-VERBALE-AZIONE"), 3)
        self.assertIn("W-VERBALE-ISSUE", codici)
        senza_decisioni = VERBALE.split("[[decisione]]")[0]
        self.assertEqual(self.verbale(senza_decisioni), ["E-VERBALE-DECISIONE"])

    def test_persone(self):
        testo = (VERBALE.replace('verificatore = "Marco Rossi"', 'verificatore = "Anna Bianchi"')
                 .replace('"Luca Verdi"]', '"Giulia Gialli"]'))
        codici = self.verbale(testo)
        self.assertIn("E-VERBALE-REDATTORE", codici)
        self.assertIn("E-VERBALE-PARTECIPANTI", codici)

    def test_piu_verbali_nello_stesso_giorno(self):
        testo = VERBALE.replace("VI-2026-10-14.", "VI-2026-10-14-B.")
        self.assertEqual(self.verbale(testo, nome="2026-10-14-b"), [])
        # l'id deve riportare il suffisso del nome del file
        self.assertEqual(self.verbale(VERBALE, nome="2026-10-14-b"), ["E-VERBALE-DECISIONE"])

    def test_suffisso_non_valido(self):
        codici = self.verbale(VERBALE, nome="2026-10-14_b")
        self.assertIn("E-DATA-FILE", codici)
        self.assertIn("E-VERBALE-DATA", codici)

    def test_copia_firmata(self):
        self.scrivi("documenti/verbali/interni/2026-10-14.firmato.pdf", "%PDF")
        self.assertEqual(self.verbale(VERBALE), [])
        # senza verbale accanto, oppure con un altro nome, il sito non la pubblicherebbe
        self.scrivi("documenti/verbali/interni/2026-10-15.firmato.pdf", "%PDF")
        self.scrivi("documenti/verbali/interni/2026-10-14_firmato.pdf", "%PDF")
        self.assertEqual(self.codici(), ["E-VERBALE-FIRMATO", "E-VERBALE-FIRMATO"])

    def test_esterno_senza_esterni(self):
        testo = VERBALE.replace('"interno"', '"esterno"').replace("VI-", "VE-")
        codici = self.verbale(testo, "esterni")
        self.assertIn("E-VERBALE-ESTERNI", codici)
        self.assertIn("W-VERBALE-APPROVAZIONE", codici)


class TestOre(Base):
    def test_ore_corrette(self):
        self.scrivi("dati/ore.csv", "data,membro,ruolo,ore,riferimento\n"
                                    "2026-10-15,Luca Verdi,Analista,2.5,https://github.com/gruppo/docs/issues/3\n")
        self.assertEqual(self.codici(), [])

    def test_ore_errate(self):
        self.scrivi("dati/gruppo.toml", GRUPPO.replace("costo_aggiudicato = 0.0", "costo_aggiudicato = 100.0"))
        self.scrivi("dati/ore.csv", "data,membro,ruolo,ore,riferimento\n"
                                    "2026-10-15,Giulia Gialli,Analista,2,riunione\n"
                                    "2026-10-15,Luca Verdi,Progettista,2,progettazione\n"
                                    "2026-10-16,Anna Bianchi,Responsabile,96,pianificazione\n")
        problemi = [m for _, _, c, m in self.problemi() if c == "E-ORE"]
        self.assertEqual(len(problemi), 4)
        self.assertTrue(any("oltre il costo aggiudicato" in m for m in problemi))


class TestRuoli(Base):
    def test_periodi_sovrapposti(self):
        self.scrivi("dati/ruoli.csv", RUOLI
                    + "2026-11-01,2026-11-30,Anna Bianchi,Verificatore\n"
                    + "2026-10-10,2026-10-12,Anna Bianchi,Analista\n"
                    + "2026-10-20,2026-10-25,Anna Bianchi,Progettista\n")
        self.assertEqual(self.codici(), ["E-RUOLI", "E-RUOLI"])


class TestPreventivo(Base):
    def ripartizione(self, *ore):
        testo = TARIFFE
        for membro, valori in zip(("Anna Bianchi", "Marco Rossi", "Luca Verdi"), ore):
            testo += f'\n[[ripartizione]]\nmembro = "{membro}"\n'
            testo += "".join(f"{r} = {x}\n" for r, x in zip(
                ("Responsabile", "Amministratore", "Analista", "Progettista", "Programmatore", "Verificatore"), valori))
        self.scrivi("dati/preventivo.toml", testo)
        return self.codici()

    def test_preventivo_conforme(self):
        conforme = (8, 10, 14, 14, 30, 14)  # 90 ore, 1800 euro: minimo 5142,86 per tre membri
        self.assertEqual(self.ripartizione(conforme, conforme, conforme), [])

    def test_preventivo_errato(self):
        conforme = (8, 10, 14, 14, 30, 14)
        codici = self.ripartizione(conforme, (0, 10, 14, 14, 30, 14), (1, 1, 1, 1, 38, 36))
        self.assertEqual(codici.count("E-PREVENTIVO"), 3)

    def test_preventivo_elevato(self):
        caro = (40, 11, 11, 11, 11, 11)
        self.assertEqual(self.ripartizione(caro, caro, caro), ["W-PREVENTIVO"])


PIANO = """\
[[fase]]
nome = "Candidatura"
inizio = 2026-09-01
fine = 2026-09-30
inizio_effettivo = 2026-09-01
fine_effettiva = 2026-09-30
ore_previste = 0

  [[fase.attivita]]
  nome = "Valutazione dei capitolati"
  inizio = 2026-09-05
  fine = 2026-09-20
  inizio_effettivo = 2026-09-06

  [[fase.milestone]]
  nome = "Invio della candidatura"
  data = 2026-09-30
  data_effettiva = 2026-09-30

[[fase]]
nome = "RTB"
inizio = 2026-10-01
fine = 2026-12-20

  [[fase.attivita]]
  nome = "Analisi dei Requisiti"
  inizio = 2026-10-02
  fine = 2026-11-30
"""


class TestPianificazione(Base):
    def problemi_piano(self, testo):
        self.scrivi("dati/pianificazione.toml", testo)
        return [(riga, codice, messaggio) for _, riga, codice, messaggio in self.problemi("dati/pianificazione.toml")]

    def test_piano_corretto(self):
        self.assertEqual(self.problemi_piano(PIANO), [])

    def test_campi_e_date_errati(self):
        testo = (PIANO.replace('nome = "Valutazione dei capitolati"', 'nome = "Valutazione dei capitolati"\n  responsabile = "Anna"')
                 .replace("fine = 2026-11-30", "fine = 2026-10-01")
                 .replace("data_effettiva = 2026-09-30", "data_effettiva = 2999-01-01")
                 .replace("ore_previste = 0", "ore_previste = -1"))
        problemi = self.problemi_piano(testo)
        self.assertEqual({codice for _, codice, _ in problemi}, {"E-PIANO"})
        messaggi = " | ".join(m for _, _, m in problemi)
        self.assertIn('chiave "responsabile" non ammessa', messaggi)
        self.assertIn("la fine prevista precede l'inizio", messaggi)
        self.assertIn("data_effettiva 2999-01-01 nel futuro", messaggi)
        self.assertIn("ore_previste deve essere un numero non negativo", messaggi)
        # la riga è quella del blocco [[fase.attivita]] che contiene l'errore
        righe = {m.split(":")[0]: r for r, _, m in problemi}
        self.assertEqual(righe['fase.attivita "Analisi dei Requisiti"'], testo.splitlines().index("  [[fase.attivita]]", 15) + 1)

    def test_fasi_sovrapposte_e_non_concluse(self):
        testo = (PIANO.replace("fine_effettiva = 2026-09-30\n", "")
                 .replace("inizio = 2026-10-01", "inizio = 2026-09-30\ninizio_effettivo = 2026-10-01"))
        messaggi = " | ".join(m for _, c, m in self.problemi_piano(testo) if c == "E-PIANO")
        self.assertEqual(messaggi.count("|"), 1)
        self.assertIn("inizio previsto non successivo alla fine della fase precedente", messaggi)
        self.assertIn("iniziata prima della fine effettiva della fase precedente", messaggi)

    def test_effettivi_incoerenti_e_voce_fuori_fase(self):
        testo = (PIANO.replace("  inizio_effettivo = 2026-09-06\n", "  fine_effettiva = 2026-09-21\n")
                 .replace("  data = 2026-09-30\n", "  data = 2026-10-02\n"))
        problemi = [(c, m) for _, c, m in self.problemi_piano(testo)]
        self.assertIn(("E-PIANO", 'fase.attivita "Valutazione dei capitolati": fine_effettiva senza inizio_effettivo'), problemi)
        self.assertIn(("W-PIANO", '"Invio della candidatura" è prevista fuori dalla fase "Candidatura"'), problemi)

    def test_file_non_valido_o_vuoto(self):
        self.assertEqual([c for _, c, _ in self.problemi_piano("[[fase]\n")], ["E-PIANO"])
        self.assertEqual([m for _, _, m in self.problemi_piano("# nessuna fase\n")], ["nessuna [[fase]]"])
        self.assertEqual([m for _, _, m in self.problemi_piano(PIANO.replace('nome = "RTB"', "nome = 3"))],
                         ["nome: atteso un altro tipo"])


class TestSegnaposto(Base):
    def test_bozza_con_segnaposto(self):
        self.doc("= Introduzione <intro>\nTODO: completare.\n")
        self.assertEqual(self.codici(), [])

    def test_documento_rilasciato(self):
        self.doc("= Introduzione <intro>\nTODO: completare la <sezione dei rischi>.\n", RILASCIATO)
        self.assertEqual(self.codici(), ["E-SEGNAPOSTO", "E-SEGNAPOSTO"])


DIARIO = """\
#import "/modello/slide.typ": presentazione, slide
#show: presentazione.with(evento: "Diario di bordo", data: "2026-10-26", titolo: "Settimana dal 2026-10-19 al 2026-10-25")

#slide(titolo: "Fatto e da fare")[
  - Analisi dei capitolati completata
]
"""


class TestPresentazioni(Base):
    def test_diario_corretto(self):
        self.scrivi("presentazioni/diari/2026-10-26.typ", DIARIO)
        self.assertEqual(self.codici(), [])

    def test_diario_errato(self):
        self.scrivi("presentazioni/diari/2026-10-26.typ",
                    DIARIO.replace('data: "2026-10-26"', 'data: "26/10/2026"')
                    .replace("completata", "completata nella sprint. TODO")
                    .replace('"Fatto e da fare"', '"Fatto e Da fare"'))
        codici = self.codici()
        for codice in ("E-DATA-TESTO", "E-LESSICO", "E-SEGNAPOSTO", "E-MAIUSCOLE", "E-DATA-FILE"):
            self.assertIn(codice, codici)

    def test_nome_del_diario(self):
        self.scrivi("presentazioni/diari/26-10-2026.typ", DIARIO)
        self.scrivi("presentazioni/diari/2026-10-27.typ", DIARIO)
        self.assertEqual(self.codici(), ["E-DATA-FILE", "E-DATA-FILE"])


class TestGulpease(Base):
    def test_indice(self):
        semplice = "Il gruppo lavora. Ogni membro ha un ruolo. Il piano è chiaro."
        difficile = "Considerazioni particolarmente approfondite sull'organizzazione metodologica complessiva"
        self.assertGreater(gulpease(semplice), 60)
        self.assertLess(gulpease(difficile), 40)

    def test_markup_rimosso(self):
        testo = testo_leggibile('#let x = (\n  a: 1,\n)\n// commento\n= Titolo\nIl #g("Proof of Concept") va.\n')
        self.assertNotIn("let", testo)
        self.assertNotIn("commento", testo)
        self.assertIn("Proof of Concept", testo)

    def test_soglia(self):
        self.doc("= Introduzione\nIl gruppo lavora. Ogni membro ha un ruolo.\n")
        self.assertEqual(self.codici(), [])
        self.doc("= Introduzione\nConsiderazioni particolarmente approfondite sull'organizzazione metodologica "
                 "complessiva determinano conseguentemente l'individuazione dell'architettura implementativa.\n")
        self.assertEqual(self.codici(), ["W-GULPEASE"])


if __name__ == "__main__":
    unittest.main()
