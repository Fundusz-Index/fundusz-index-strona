"""Testy sprawdzania plików z danymi. Uruchom: python3 -m unittest discover tests"""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import sprawdz_dane as S  # noqa: E402


class TestSprawdzanie(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        for nazwa in ("data", "analizy", "assets", "pliki", "en", "i18n"):
            shutil.copytree(ROOT / nazwa, self.tmp / nazwa)
        for plik in ROOT.glob("*.html"):
            shutil.copy(plik, self.tmp / plik.name)
        self._root, self._data = S.ROOT, S.DATA
        S.ROOT, S.DATA = self.tmp, self.tmp / "data"

    def tearDown(self):
        S.ROOT, S.DATA = self._root, self._data
        shutil.rmtree(self.tmp)

    def zapisz(self, nazwa, tekst):
        (self.tmp / "data" / nazwa).write_text(tekst, encoding="utf-8")

    def test_obecne_pliki_bez_bledow(self):
        r = S.sprawdz()
        self.assertEqual(r.bledy, [])
        self.assertTrue(r.ostrzezenia)  # są jeszcze pola [do uzupełnienia]

    def test_tekst_z_danych_bez_tlumaczenia(self):
        import json
        plik = self.tmp / "data" / "spolki.json"
        spolki = json.loads(plik.read_text(encoding="utf-8"))
        spolki[0]["opis"] = "zupełnie nowy opis spółki"
        plik.write_text(json.dumps(spolki, ensure_ascii=False), encoding="utf-8")
        r = S.sprawdz()
        self.assertEqual(r.bledy, [])
        self.assertTrue(any("zupełnie nowy opis spółki" in o and "i18n/en.json" in o for o in r.ostrzezenia))

    def test_strona_angielska_z_brakujacym_linkiem(self):
        (self.tmp / "polityka-prywatnosci.html").unlink()
        r = S.sprawdz()
        self.assertTrue(any(b.startswith("en/") and "polityka-prywatnosci.html" in b for b in r.bledy))

    def test_brakujacy_raport_pdf(self):
        (self.tmp / "pliki" / "analizy" / "fundusz-index-cvx-2026-10.pdf").unlink()
        r = S.sprawdz()
        self.assertTrue(any("fundusz-index-cvx-2026-10.pdf" in b for b in r.bledy))

    def test_tryb_publikacji_zamienia_ostrzezenia_w_bledy(self):
        r = S.sprawdz(publikacja=True)
        self.assertTrue(any("do uzupełnienia" in b for b in r.bledy))

    def test_zly_json(self):
        self.zapisz("spolki.json", '[{"ticker": "AAA",}]')
        r = S.sprawdz()
        self.assertTrue(any("zła składnia JSON" in b for b in r.bledy))

    def test_nieznany_ticker_i_zla_data(self):
        self.zapisz("transakcje.csv", "data,typ,ticker,kwota_pln,liczba_akcji,uzasadnienie\n2026-13-01,kupno,XYZ,1000,,test\n")
        r = S.sprawdz()
        self.assertTrue(any("RRRR-MM-DD" in b for b in r.bledy))
        self.assertTrue(any("XYZ" in b for b in r.bledy))

    def test_przecinek_bez_cudzyslowu(self):
        self.zapisz("transakcje.csv", "data,typ,ticker,kwota_pln,liczba_akcji,uzasadnienie\n2026-10-25,kupno,CVX,1000,,tanio, dobrze\n")
        r = S.sprawdz()
        self.assertTrue(any("za dużo kolumn" in b for b in r.bledy))

    def test_za_duza_sprzedaz(self):
        self.zapisz("transakcje.csv", "data,typ,ticker,kwota_pln,liczba_akcji,uzasadnienie\n"
                    "2026-10-25,kupno,CVX,,10,a\n2026-10-27,sprzedaz,CVX,,11,b\n2026-10-27,sprzedaz,AMD,500,,c\n")
        r = S.sprawdz()
        self.assertTrue(any("sprzedaż 11 akcji CVX" in b for b in r.bledy))
        self.assertTrue(any("AMD, którego wcześniej nie kupiono" in b for b in r.bledy))

    def test_ogloszenie_bez_tytulu(self):
        self.zapisz("ogloszenie.json", '{"pokaz": true, "tytul": ""}')
        r = S.sprawdz()
        self.assertTrue(any("nie ma tytułu" in b for b in r.bledy))

    def test_kalendarz_zla_data_i_typ(self):
        self.zapisz("kalendarz.json", '{"wydarzenia": [{"data": "2026-13-01", "typ": "Impreza", "tytul": "X"}]}')
        r = S.sprawdz()
        self.assertTrue(any("zła data" in b for b in r.bledy))
        self.assertTrue(any("nieznany typ" in b for b in r.bledy))

    def test_martwy_link(self):
        (self.tmp / "index.html").write_text('<a href="nie-ma.html">x</a>', encoding="utf-8")
        r = S.sprawdz()
        self.assertTrue(any("nie-ma.html" in b for b in r.bledy))


if __name__ == "__main__":
    unittest.main()
