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

    def test_gotowka_w_etf(self):
        # ETF rośnie o 1% dziennie, dolar stały. Połowa kapitału w spółce o stałym kursie.
        etf = {SESJE[1]: 100.0, SESJE[2]: 101.0, SESJE[3]: 102.01}
        kursy = {"aaa.us": {d: 10.0 for d in SESJE}, "bbb.us": {d: 20.0 for d in SESJE},
                 "^spx": {d: 5000.0 for d in SESJE}, "etf.uk": etf}
        fx = {d: 4.0 for d in SESJE}
        u = dict(USTAWIENIA, gotowka={"ticker": "ETF", "nazwa": "Fundusz obligacji", "stooq": "etf.uk"})
        t = [tr(D(2026, 10, 26), "kupno", "AAA", 50000)]
        w = A.policz(u, SPOLKI, t, kursy, fx, "^spx")
        # 50 000 w akcjach bez zmian, 50 000 gotówki * 1,01 * 1,01 = 51 005
        self.assertAlmostEqual(w["podsumowanie"]["gotowka_pln"], 51005, places=2)
        self.assertAlmostEqual(w["podsumowanie"]["wartosc_pln"], 101005, places=2)
        self.assertAlmostEqual(w["podsumowanie"]["gotowka_waga"], 50.5, places=1)
        self.assertEqual(w["gotowka"]["ticker"], "ETF")
        self.assertAlmostEqual(w["gotowka"]["zmiana_dzienna"], 1.0)
        # drugi zakup dzień później zabiera gotówkę po jej wzroście
        t.append(tr(D(2026, 10, 27), "kupno", "BBB", 50500))
        w = A.policz(u, SPOLKI, t, kursy, fx, "^spx")
        self.assertAlmostEqual(w["seria"][1]["f"], 100500, places=2)
        self.assertAlmostEqual(w["podsumowanie"]["gotowka_pln"], 0, places=2)
        self.assertAlmostEqual(w["podsumowanie"]["wartosc_pln"], 100500, places=2)

    def test_gotowka_w_etf_bez_kursow(self):
        kursy = {"aaa.us": {d: 10.0 for d in SESJE}, "^spx": {d: 5000.0 for d in SESJE}}
        u = dict(USTAWIENIA, gotowka={"ticker": "ETF", "nazwa": "Fundusz obligacji", "stooq": "etf.uk"})
        with self.assertRaises(RuntimeError):
            A.policz(u, SPOLKI, [tr(D(2026, 10, 26), "kupno", "AAA", 1000)], kursy, {d: 4.0 for d in SESJE}, "^spx")

    def test_za_malo_gotowki(self):
        kursy = {"aaa.us": {d: 10.0 for d in SESJE}, "bbb.us": {d: 20.0 for d in SESJE}, "^spx": {d: 5000.0 for d in SESJE}}
        t = [tr(D(2026, 10, 26), "kupno", "AAA", 70000), tr(D(2026, 10, 27), "kupno", "BBB", 40000)]
        with self.assertRaises(ValueError):
            A.policz(USTAWIENIA, SPOLKI, t, kursy, {d: 4.0 for d in SESJE}, "^spx")

    def test_spolka_spoza_portfela_ma_kurs(self):
        kursy = {"aaa.us": {d: 10.0 for d in SESJE}, "bbb.us": {SESJE[1]: 20.0, SESJE[2]: 20.0, SESJE[3]: 21.0},
                 "^spx": {d: 5000.0 for d in SESJE}}
        w = A.policz(USTAWIENIA, SPOLKI, [tr(D(2026, 10, 26), "kupno", "AAA", 1000)], kursy, {d: 4.0 for d in SESJE}, "^spx")
        self.assertEqual([p["ticker"] for p in w["pozycje"]], ["AAA"])
        self.assertEqual(w["obserwowane"][0]["ticker"], "BBB")
        self.assertAlmostEqual(w["obserwowane"][0]["kurs_usd"], 21.0)
        self.assertAlmostEqual(w["obserwowane"][0]["zmiana_dzienna"], 5.0)

    def test_parsowanie_yahoo(self):
        import json
        t = json.dumps({"chart": {"result": [{"meta": {"gmtoffset": -18000},
             "timestamp": [1792157400, 1792416600, 1792503000],
             "indicators": {"quote": [{"close": [71.28, None, 72.5]}]}}]}})
        d = A.parsuj_yahoo(t, "WMB")
        self.assertEqual(list(d.values()), [71.28, 72.5])
        self.assertEqual(min(d).weekday(), 4)  # piątek 16.10.2026

    def test_parsowanie_nasdaq(self):
        import json
        t = json.dumps({"data": {"tradesTable": {"rows": [
            {"date": "10/27/2026", "close": "$71.90"}, {"date": "10/26/2026", "close": "6,812.35"}]}}})
        d = A.parsuj_nasdaq(t, "WMB")
        self.assertEqual(d, {D(2026, 10, 27): 71.9, D(2026, 10, 26): 6812.35})
        with self.assertRaises(RuntimeError):
            A.parsuj_nasdaq('{"data": null}', "WMB")

    def test_zrodla_zapasowe(self):
        A.kursy_yahoo, stare = (lambda *a: (_ for _ in ()).throw(RuntimeError("blokada"))), A.kursy_yahoo
        A.kursy_stooq, stare2 = (lambda *a: {D(2026, 10, 26): 1.0}), A.kursy_stooq
        try:
            self.assertEqual(A.kursy_akcji("X", "x.us", D(2026, 10, 1), D(2026, 10, 30)), {D(2026, 10, 26): 1.0})
        finally:
            A.kursy_yahoo, A.kursy_stooq = stare, stare2

    def test_plik_transakcji(self):
        t = A.wczytaj_transakcje()
        self.assertEqual(len(t), 4)
        self.assertEqual([x["data"] for x in t], sorted(x["data"] for x in t))
        self.assertLessEqual(sum(x["kwota_pln"] for x in t), 100000)


if __name__ == "__main__":
    unittest.main()
