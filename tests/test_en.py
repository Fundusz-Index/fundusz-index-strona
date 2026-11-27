"""Testy wersji angielskiej (katalog en/). Uruchom: python3 -m unittest discover tests"""

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import zbuduj_en  # noqa: E402

POLSKIE = sorted(list(ROOT.glob("*.html")) + list(ROOT.glob("analizy/*.html")) + list(ROOT.glob("artykuly/*.html")))


class TestWersjaAngielska(unittest.TestCase):
    def test_strony_en_sa_aktualne(self):
        rozne, _ = zbuduj_en.zbuduj(zapisz=False)
        self.assertEqual(rozne, [], "Uruchom: python3 scripts/zbuduj_en.py")

    def test_kazdy_tekst_ze_stron_ma_tlumaczenie(self):
        _, braki = zbuduj_en.zbuduj(zapisz=False)
        self.assertEqual(braki, [], "Dopisz tłumaczenia do i18n/en.json (pole 'teksty') "
                                    "albo do 'bez_zmian', jeśli tekst ma zostać taki sam.")

    def test_teksty_ze_skryptow_sa_w_slowniku(self):
        teksty, _ = zbuduj_en.wczytaj()
        brak = []
        for plik in sorted((ROOT / "assets" / "js").glob("*.js")):
            if plik.name == "en.js":
                continue
            kod = plik.read_text(encoding="utf-8")
            for m in re.finditer(r"\bt\(((?:'[^']*'|[^()'])*)\)", kod):
                argument = re.sub(r"[=!]==?\s*'[^']*'", "", m.group(1))  # porównania, nie teksty
                for napis in re.findall(r"'([^']*)'", argument):
                    if re.search(r"[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż]{2}", napis) and napis not in teksty:
                        brak.append(plik.name + ": " + napis)
        self.assertEqual(brak, [], "Dopisz te teksty do i18n/en.json")

    def test_slownik_bez_pustych_tlumaczen_i_dlugich_myslnikow(self):
        d = json.loads((ROOT / "i18n" / "en.json").read_text(encoding="utf-8"))
        for pl, en in d["teksty"].items():
            self.assertTrue(en.strip(), "Puste tłumaczenie: " + pl)
            self.assertNotIn("\u2014", en, "Długi myślnik w tłumaczeniu: " + pl)
            self.assertEqual(pl.count("{"), en.count("{"), "Inna liczba pól {…} w tłumaczeniu: " + pl)

    def test_kazda_polska_strona_ma_przelacznik_do_istniejacej_strony_en(self):
        for plik in POLSKIE:
            html = plik.read_text(encoding="utf-8")
            m = re.findall(r'<a class="lang-switch" href="([^"]+)" hreflang="en"', html)
            self.assertEqual(len(m), 1, plik.name + ": brak przełącznika języka w nagłówku")
            self.assertTrue((plik.parent / m[0]).resolve().is_file(), plik.name + ": " + m[0])

    def test_strony_en_wracaja_do_polskiej_wersji_tej_samej_strony(self):
        for nazwa in zbuduj_en.STRONY:
            html = (ROOT / "en" / nazwa).read_text(encoding="utf-8")
            self.assertIn('<html lang="en">', html)
            self.assertIn('<a class="lang-switch" href="../%s" hreflang="pl"' % nazwa, html)
            self.assertIn("assets/js/en.js", html)
            self.assertNotIn("claude:viewport", html)


if __name__ == "__main__":
    unittest.main()
