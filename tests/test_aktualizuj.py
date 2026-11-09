"""Testy obliczeń portfela. Uruchom: python3 -m unittest discover tests"""

import datetime as dt
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import aktualizuj_dane as A  # noqa: E402

D = dt.date
USTAWIENIA = {"kapital_startowy_pln": 100000, "data_startu": "2026-10-25", "benchmark": {"nazwa": "S&P 500", "stooq": "^spx"}}
SPOLKI = [
    {"ticker": "AAA", "nazwa": "Alfa", "stooq": "aaa.us", "sektor": "X"},
    {"ticker": "BBB", "nazwa": "Beta", "stooq": "bbb.us", "sektor": "Y"},
]
SESJE = [D(2026, 10, 23), D(2026, 10, 26), D(2026, 10, 27), D(2026, 10, 28)]


def tr(data, typ, ticker, kwota=None, akcje=None):
    return {"data": data, "typ": typ, "ticker": ticker, "kwota_pln": kwota, "liczba_akcji": akcje, "uzasadnienie": ""}


class TestPortfel(unittest.TestCase):
    def test_stale_ceny_daja_zero(self):
        kursy = {"aaa.us": {d: 10.0 for d in SESJE}, "bbb.us": {d: 20.0 for d in SESJE}, "^spx": {d: 5000.0 for d in SESJE}}
        fx = {d: 4.0 for d in SESJE}
        t = [tr(D(2026, 10, 25), "kupno", "AAA", 60000), tr(D(2026, 10, 25), "kupno", "BBB", 40000)]
        w = A.policz(USTAWIENIA, SPOLKI, t, kursy, fx, "^spx")
        self.assertEqual(w["seria"][0]["d"], "2026-10-26")  # niedziela -> poniedziałek
        self.assertAlmostEqual(w["podsumowanie"]["wartosc_pln"], 100000, places=2)
        self.assertAlmostEqual(w["podsumowanie"]["zwrot_od_startu"], 0)
        self.assertAlmostEqual(w["podsumowanie"]["gotowka_pln"], 0, places=2)
        self.assertEqual([p["waga"] for p in w["pozycje"]], [60.0, 40.0])

    def test_wzrost_kursu_i_dolara(self):
        kursy = {"aaa.us": {SESJE[1]: 10.0, SESJE[2]: 10.0, SESJE[3]: 12.0}, "bbb.us": {d: 20.0 for d in SESJE},
                 "^spx": {SESJE[1]: 5000.0, SESJE[2]: 5000.0, SESJE[3]: 5500.0}}
        fx = {SESJE[1]: 4.0, SESJE[2]: 4.0, SESJE[3]: 4.4}
        t = [tr(D(2026, 10, 26), "kupno", "AAA", 50000)]
        w = A.policz(USTAWIENIA, SPOLKI, t, kursy, fx, "^spx")
        # 50 000 gotówki + 50 000 * 1,2 * 1,1 = 116 000
        self.assertAlmostEqual(w["podsumowanie"]["wartosc_pln"], 116000, places=2)
        self.assertAlmostEqual(w["podsumowanie"]["zwrot_od_startu"], 16.0)
        # benchmark: 1,1 * 1,1 = +21%
        self.assertAlmostEqual(w["podsumowanie"]["benchmark_od_startu"], 21.0)
        self.assertAlmostEqual(w["pozycje"][0]["zmiana_dzienna"], 20.0)
        self.assertAlmostEqual(w["pozycje"][0]["zwrot"], 32.0)

    def test_sprzedaz_czesciowa(self):
        kursy = {"aaa.us": {SESJE[1]: 10.0, SESJE[2]: 20.0, SESJE[3]: 20.0}, "bbb.us": {d: 20.0 for d in SESJE},
                 "^spx": {d: 5000.0 for d in SESJE}}
        fx = {d: 1.0 for d in SESJE}
        t = [tr(D(2026, 10, 26), "kupno", "AAA", akcje=1000), tr(D(2026, 10, 27), "sprzedaz", "AAA", akcje=400)]
        w = A.policz(USTAWIENIA, SPOLKI, t, kursy, fx, "^spx")
        # gotówka: 100 000 - 10 000 + 8 000 = 98 000; akcje 600 * 20 = 12 000
        self.assertAlmostEqual(w["podsumowanie"]["wartosc_pln"], 110000, places=2)
        self.assertAlmostEqual(w["pozycje"][0]["koszt_pln"], 6000, places=2)
        self.assertEqual(w["transakcje"][0]["typ"], "sprzedaz")

    def test_za_duza_sprzedaz(self):
        kursy = {"aaa.us": {d: 10.0 for d in SESJE}, "bbb.us": {d: 20.0 for d in SESJE}, "^spx": {d: 5000.0 for d in SESJE}}
        fx = {d: 1.0 for d in SESJE}
        t = [tr(D(2026, 10, 26), "kupno", "AAA", akcje=10), tr(D(2026, 10, 27), "sprzedaz", "AAA", akcje=11)]
        with self.assertRaises(ValueError):
            A.policz(USTAWIENIA, SPOLKI, t, kursy, fx, "^spx")

    def test_plik_transakcji(self):
        t = A.wczytaj_transakcje()
        self.assertEqual(len(t), 5)
        self.assertAlmostEqual(sum(x["kwota_pln"] for x in t), 100000)


if __name__ == "__main__":
    unittest.main()
