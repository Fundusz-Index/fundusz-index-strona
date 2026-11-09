#!/usr/bin/env python3
"""Liczy wyniki portfela Funduszu Index i zapisuje data/portfolio.json.

Uruchamiane raz dziennie po zamknięciu sesji w USA (GitHub Actions albo cron na hostingu).

Źródła:
  - kursy zamknięcia akcji i S&P 500: Yahoo Finance, a gdy nie odpowie, Nasdaq, potem Stooq,
  - kurs USD/PLN: NBP, tabela A (średni kurs).

Użycie:
  python3 scripts/aktualizuj_dane.py          # prawdziwe dane
  python3 scripts/aktualizuj_dane.py --demo   # dane przykładowe, bez internetu
"""

import argparse
import csv
import datetime as dt
import json
import math
import random
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
# Symbol benchmarku w Yahoo dla symbolu ze Stooq
YAHOO_BENCHMARK = {"^spx": "^GSPC"}


# ---------- odczyt plików ----------

def wczytaj_json(nazwa):
    with open(DATA / nazwa, encoding="utf-8") as f:
        return json.load(f)


def wczytaj_transakcje(sciezka=None):
    sciezka = sciezka or DATA / "transakcje.csv"
    wynik = []
    with open(sciezka, encoding="utf-8", newline="") as f:
        for nr, w in enumerate(csv.DictReader(f), start=2):
            if not (w.get("data") or "").strip():
                continue
            typ = w["typ"].strip().lower()
            if typ not in ("kupno", "sprzedaz", "sprzedaż"):
                raise ValueError(f"transakcje.csv, wiersz {nr}: typ musi być 'kupno' albo 'sprzedaz', jest '{w['typ']}'")
            kwota = (w.get("kwota_pln") or "").strip().replace(" ", "").replace(",", ".")
            akcje = (w.get("liczba_akcji") or "").strip().replace(" ", "").replace(",", ".")
            if not kwota and not akcje:
                raise ValueError(f"transakcje.csv, wiersz {nr}: podaj kwota_pln albo liczba_akcji")
            wynik.append({
                "data": dt.date.fromisoformat(w["data"].strip()),
                "typ": "sprzedaz" if typ.startswith("sprzeda") else "kupno",
                "ticker": w["ticker"].strip().upper(),
                "kwota_pln": float(kwota) if kwota else None,
                "liczba_akcji": float(akcje) if akcje else None,
                "uzasadnienie": (w.get("uzasadnienie") or "").strip(),
            })
    wynik.sort(key=lambda t: t["data"])
    return wynik


# ---------- pobieranie danych ----------

try:  # curl_cffi łączy się jak przeglądarka Chrome; serwisy giełdowe rzadziej go blokują
    from curl_cffi import requests as _cffi
except ImportError:
    _cffi = None


def _pobierz_raz(url, naglowki):
    if _cffi is not None:
        r = _cffi.get(url, headers=naglowki, impersonate="chrome", timeout=30)
        if r.status_code >= 400:
            raise RuntimeError(f"HTTP Error {r.status_code}")
        return r.text
    req = urllib.request.Request(url, headers=dict({"User-Agent": USER_AGENT}, **naglowki))
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def _pobierz(url, proby=3, naglowki=None):
    ostatni = None
    for i in range(proby):
        try:
            return _pobierz_raz(url, naglowki or {})
        except Exception as e:  # sieć bywa kapryśna, próbujemy jeszcze raz
            ostatni = e
            if "404" in str(e):
                break
            # przy 429 (za dużo zapytań) czekamy dłużej
            time.sleep((10 if "429" in str(e) else 2) * (i + 1))
    raise RuntimeError(f"Nie udało się pobrać {url}: {ostatni}")


def kursy_yahoo(symbol, od, do):
    """Zwraca {data: kurs zamknięcia} z Yahoo Finance (kurs skorygowany o splity, bez dywidend)."""
    p1 = int(dt.datetime(od.year, od.month, od.day, tzinfo=dt.timezone.utc).timestamp())
    p2 = int(dt.datetime(do.year, do.month, do.day, 23, 59, tzinfo=dt.timezone.utc).timestamp())
    blad = None
    for host in ("query2", "query1"):
        url = (f"https://{host}.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol)}"
               f"?period1={p1}&period2={p2}&interval=1d&events=history")
        try:
            return parsuj_yahoo(_pobierz(url, proby=2), symbol)
        except RuntimeError as e:
            blad = e
    raise blad


NASDAQ_NAGLOWKI = {"Accept": "application/json, text/plain, */*", "Origin": "https://www.nasdaq.com",
                   "Referer": "https://www.nasdaq.com/"}
# Symbol benchmarku w Nasdaq dla symbolu ze Stooq: (symbol, klasa aktywów)
NASDAQ_BENCHMARK = {"^spx": ("SPX", "index")}


def kursy_nasdaq(symbol, od, do, klasa="stocks"):
    """Zwraca {data: kurs zamknięcia} z API strony nasdaq.com."""
    url = (f"https://api.nasdaq.com/api/quote/{urllib.parse.quote(symbol)}/historical?"
           + urllib.parse.urlencode({"assetclass": klasa, "fromdate": od.isoformat(),
                                     "todate": do.isoformat(), "limit": 9999}))
    return parsuj_nasdaq(_pobierz(url, naglowki=NASDAQ_NAGLOWKI), symbol)


def parsuj_nasdaq(tekst, symbol):
    try:
        wiersze = json.loads(tekst)["data"]["tradesTable"]["rows"]
    except (ValueError, KeyError, TypeError):
        raise RuntimeError(f"Nasdaq nie zwrócił danych dla {symbol}: {tekst[:120]!r}")
    dane = {}
    for w in wiersze or []:
        try:
            dzien = dt.datetime.strptime(w["date"], "%m/%d/%Y").date()
            dane[dzien] = round(float(str(w["close"]).replace("$", "").replace(",", "")), 4)
        except (KeyError, ValueError):
            continue
    if not dane:
        raise RuntimeError(f"Nasdaq zwrócił pustą serię dla {symbol}")
    return dane


def parsuj_yahoo(tekst, symbol):
    try:
        wynik = json.loads(tekst)["chart"]["result"][0]
        czasy = wynik["timestamp"]
        zamkniecia = wynik["indicators"]["quote"][0]["close"]
        przesuniecie = wynik.get("meta", {}).get("gmtoffset", 0)
    except (ValueError, KeyError, IndexError, TypeError):
        raise RuntimeError(f"Yahoo nie zwrócił danych dla {symbol}: {tekst[:120]!r}")
    dane = {}
    for t, c in zip(czasy, zamkniecia):
        if c is not None:
            dzien = dt.datetime.fromtimestamp(t + przesuniecie, tz=dt.timezone.utc).date()
            dane[dzien] = round(float(c), 4)
    if not dane:
        raise RuntimeError(f"Yahoo zwrócił pustą serię dla {symbol}")
    return dane


def kursy_akcji(symbol_yahoo, symbol_stooq, od, do, symbol_nasdaq=None, klasa="stocks"):
    """Kolejno Yahoo, Nasdaq i Stooq. Błąd tylko wtedy, gdy wszystkie źródła zawiodą."""
    bledy = []
    zrodla = [("Yahoo", lambda: kursy_yahoo(symbol_yahoo, od, do), symbol_yahoo)]
    if symbol_nasdaq:
        zrodla.append(("Nasdaq", lambda: kursy_nasdaq(symbol_nasdaq, od, do, klasa), symbol_nasdaq))
    zrodla.append(("Stooq", lambda: kursy_stooq(symbol_stooq, od, do), symbol_stooq))
    for nazwa, funkcja, sym in zrodla:
        try:
            return funkcja()
        except RuntimeError as e:
            bledy.append(f"{nazwa}: {e}")
            print(f"Uwaga: {nazwa} nie odpowiedział dla {sym}, próbuję dalej.", file=sys.stderr)
    raise RuntimeError("Nie udało się pobrać kursów. " + " | ".join(bledy))


def kursy_stooq(symbol, od, do):
    """Zwraca {data: kurs zamknięcia} ze Stooq."""
    url = "https://stooq.com/q/d/l/?" + urllib.parse.urlencode({
        "s": symbol, "d1": od.strftime("%Y%m%d"), "d2": do.strftime("%Y%m%d"), "i": "d"})
    tekst = _pobierz(url)
    wiersze = list(csv.DictReader(tekst.splitlines()))
    if not wiersze or "Close" not in wiersze[0]:
        raise RuntimeError(f"Stooq nie zwrócił danych dla {symbol}: {tekst[:120]!r}")
    return {dt.date.fromisoformat(w["Date"]): float(w["Close"]) for w in wiersze if w.get("Close")}


def kursy_nbp_usd(od, do):
    """Zwraca {data: średni kurs USD/PLN} z NBP. NBP przyjmuje maks. 93 dni w jednym zapytaniu."""
    wynik = {}
    poczatek = od
    while poczatek <= do:
        koniec = min(poczatek + dt.timedelta(days=90), do)
        url = f"https://api.nbp.pl/api/exchangerates/rates/a/usd/{poczatek}/{koniec}/?format=json"
        try:
            dane = json.loads(_pobierz(url))
            for r in dane["rates"]:
                wynik[dt.date.fromisoformat(r["effectiveDate"])] = float(r["mid"])
        except RuntimeError as e:
            if "404" not in str(e):  # 404 = brak notowań w tym okresie (np. same święta)
                raise
        poczatek = koniec + dt.timedelta(days=1)
    if not wynik:
        raise RuntimeError("NBP nie zwrócił kursów USD")
    return wynik


# ---------- dane przykładowe ----------

def dane_demo(spolki, benchmark_symbol, od, do):
    """Generuje powtarzalne kursy przykładowe (bez internetu)."""
    rnd = random.Random(20261025)
    dni = [od + dt.timedelta(days=i) for i in range((do - od).days + 1)]
    dni_sesji = [d for d in dni if d.weekday() < 5]
    kursy = {}
    start = {"googl.us": 250.0, "cvx.us": 155.0, "wmb.us": 70.0, "eme.us": 640.0, "amd.us": 230.0}
    rynek = [rnd.gauss(0, 0.0095) for _ in dni_sesji]
    for s in spolki:
        sym = s["stooq"]
        cena = start.get(sym, 100.0)
        beta = 0.7 + rnd.random() * 0.8
        ser = {}
        for i, d in enumerate(dni_sesji):
            if i:
                cena *= math.exp(0.0004 + beta * rynek[i] + rnd.gauss(0, 0.012))
            ser[d] = round(cena, 2)
        kursy[sym] = ser
    cena = 6800.0
    ser = {}
    for i, d in enumerate(dni_sesji):
        if i:
            cena *= math.exp(0.0003 + rynek[i])
        ser[d] = round(cena, 2)
    kursy[benchmark_symbol] = ser
    fx, kurs = {}, 3.70
    for d in dni_sesji:
        kurs *= math.exp(rnd.gauss(0, 0.004))
        fx[d] = round(kurs, 4)
    return kursy, fx


# ---------- obliczenia ----------

def ostatni_do(seria, dzien):
    """Ostatnia wartość z serii {data: wartość} z dnia <= dzien."""
    najlepszy = None
    for d in seria:
        if d <= dzien and (najlepszy is None or d > najlepszy):
            najlepszy = d
    return seria[najlepszy] if najlepszy is not None else None


def zaokr(x, n=2):
    return None if x is None else round(x, n)


def policz(ustawienia, spolki, transakcje, kursy, fx, benchmark_symbol, teraz=None):
    kapital = float(ustawienia["kapital_startowy_pln"])
    po_tickerze = {s["ticker"]: s for s in spolki}
    for t in transakcje:
        if t["ticker"] not in po_tickerze:
            raise ValueError(f"Ticker {t['ticker']} z transakcje.csv nie ma wpisu w spolki.json")

    bench = kursy[benchmark_symbol]
    sesje = sorted(bench)
    pierwsza_data = transakcje[0]["data"] if transakcje else dt.date.fromisoformat(ustawienia["data_startu"])
    sesje = [d for d in sesje if d >= pierwsza_data]
    if not sesje:
        raise RuntimeError("Brak sesji giełdowych od daty startu. Czy rynek już był otwarty?")

    def cena(ticker, dzien):
        c = ostatni_do(kursy[po_tickerze[ticker]["stooq"]], dzien)
        if c is None:
            raise RuntimeError(f"Brak kursu {ticker} na {dzien}")
        return c

    def usd(dzien):
        k = ostatni_do(fx, dzien)
        if k is None:
            raise RuntimeError(f"Brak kursu USD/PLN na {dzien}")
        return k

    # Każda transakcja rozliczana po kursie zamknięcia pierwszej sesji w dniu transakcji lub po nim.
    rozliczone = []
    for t in transakcje:
        dzien = next((d for d in sesje if d >= t["data"]), None)
        if dzien is None:
            continue  # transakcja z dzisiaj, zanim była sesja
        c, k = cena(t["ticker"], dzien), usd(dzien)
        akcje = t["liczba_akcji"] if t["liczba_akcji"] is not None else t["kwota_pln"] / (c * k)
        rozliczone.append(dict(t, dzien_rozliczenia=dzien, akcje=akcje, cena_usd=c, usdpln=k, wartosc_pln=akcje * c * k))

    seria, gotowka, pozycje, koszt = [], kapital, {}, {}
    b0 = None
    idx = 0
    for d in sesje:
        while idx < len(rozliczone) and rozliczone[idx]["dzien_rozliczenia"] == d:
            t = rozliczone[idx]
            if t["typ"] == "kupno":
                gotowka -= t["wartosc_pln"]
                pozycje[t["ticker"]] = pozycje.get(t["ticker"], 0) + t["akcje"]
                koszt[t["ticker"]] = koszt.get(t["ticker"], 0) + t["wartosc_pln"]
            else:
                przed = pozycje.get(t["ticker"], 0)
                if t["akcje"] > przed + 1e-9:
                    raise ValueError(f"Sprzedaż {t['ticker']} z {t['data']}: więcej akcji niż w portfelu")
                if przed > 0:
                    koszt[t["ticker"]] *= (przed - t["akcje"]) / przed
                pozycje[t["ticker"]] = przed - t["akcje"]
                gotowka += t["wartosc_pln"]
                if pozycje[t["ticker"]] < 1e-9:
                    pozycje.pop(t["ticker"])
                    koszt.pop(t["ticker"], None)
            idx += 1
        k = usd(d)
        wartosc = gotowka + sum(a * cena(tk, d) * k for tk, a in pozycje.items())
        b = bench[d] * k
        if b0 is None:
            b0 = b
        seria.append({"d": d.isoformat(), "f": round(wartosc, 2), "b": round(kapital * b / b0, 2)})

    ostatni, poprzedni = sesje[-1], (sesje[-2] if len(sesje) > 1 else sesje[-1])
    k = usd(ostatni)
    razem = seria[-1]["f"]
    lista = []
    for tk, a in pozycje.items():
        s = po_tickerze[tk]
        c, cp = cena(tk, ostatni), cena(tk, poprzedni)
        wart = a * c * k
        lista.append({
            "ticker": tk, "nazwa": s["nazwa"], "sektor": s["sektor"], "opis": s.get("opis", ""),
            "analiza": s.get("analiza"), "autorzy": s.get("autorzy"),
            "liczba_akcji": round(a, 4), "kurs_usd": zaokr(c),
            "wartosc_pln": zaokr(wart), "koszt_pln": zaokr(koszt[tk]),
            "waga": zaokr(wart / razem * 100, 2),
            "zwrot": zaokr((wart / koszt[tk] - 1) * 100, 2),
            "zmiana_dzienna": zaokr((c / cp - 1) * 100, 2) if poprzedni != ostatni else 0.0,
        })
    lista.sort(key=lambda p: -p["wartosc_pln"])

    def zwrot_od(dni_wstecz=None, od_daty=None):
        if od_daty is not None:
            kandydaci = [p for p in seria if p["d"] < od_daty]
            p0 = kandydaci[-1] if kandydaci else seria[0]
        else:
            granica = (ostatni - dt.timedelta(days=dni_wstecz)).isoformat()
            kandydaci = [p for p in seria if p["d"] <= granica]
            if not kandydaci:
                return None
            p0 = kandydaci[-1]
        return {"f": zaokr((seria[-1]["f"] / p0["f"] - 1) * 100), "b": zaokr((seria[-1]["b"] / p0["b"] - 1) * 100)}

    okresy = {
        "1M": zwrot_od(30), "3M": zwrot_od(91), "6M": zwrot_od(182),
        "YTD": zwrot_od(od_daty=f"{ostatni.year}-01-01"), "1R": zwrot_od(365),
        "start": {"f": zaokr((seria[-1]["f"] / kapital - 1) * 100), "b": zaokr((seria[-1]["b"] / kapital - 1) * 100)},
    }
    sp = bench[ostatni] / bench[poprzedni] - 1 if poprzedni != ostatni else 0.0
    teraz = teraz or dt.datetime.now(dt.timezone.utc)

    return {
        "zaktualizowano": teraz.isoformat(timespec="minutes"),
        "stan_na": ostatni.isoformat(),
        "kapital_startowy_pln": kapital,
        "data_startu": ustawienia["data_startu"],
        "benchmark": ustawienia["benchmark"]["nazwa"],
        "kurs_usdpln": k,
        "podsumowanie": {
            "wartosc_pln": razem,
            "gotowka_pln": zaokr(gotowka),
            "zwrot_od_startu": okresy["start"]["f"],
            "benchmark_od_startu": okresy["start"]["b"],
            "zmiana_dzienna": zaokr((seria[-1]["f"] / seria[-2]["f"] - 1) * 100) if len(seria) > 1 else 0.0,
            "benchmark_zmiana_dzienna": zaokr(sp * 100),
            "liczba_pozycji": len(lista),
        },
        "okresy": okresy,
        "pozycje": lista,
        "transakcje": [{
            "data": t["data"].isoformat(), "rozliczono": t["dzien_rozliczenia"].isoformat(), "typ": t["typ"],
            "ticker": t["ticker"], "nazwa": po_tickerze[t["ticker"]]["nazwa"],
            "kwota_pln": zaokr(t["wartosc_pln"]), "liczba_akcji": round(t["akcje"], 4),
            "uzasadnienie": t["uzasadnienie"],
        } for t in reversed(rozliczone)],
        "seria": seria,
    }


# ---------- główna funkcja ----------

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--demo", action="store_true", help="dane przykładowe z ostatniego roku, bez internetu")
    p.add_argument("--wyjscie", default=str(DATA / "portfolio.json"))
    a = p.parse_args(argv)

    ustawienia = wczytaj_json("ustawienia.json")
    spolki = wczytaj_json("spolki.json")
    transakcje = wczytaj_transakcje()
    bsym = ustawienia["benchmark"]["stooq"]
    dzis = dt.date.today()

    if a.demo:
        od = dzis - dt.timedelta(days=372)
        kursy, fx = dane_demo(spolki, bsym, od, dzis)
        start_demo = min(kursy[bsym])
        ustawienia = dict(ustawienia, data_startu=start_demo.isoformat())
        transakcje = [dict(t, data=start_demo) if t["data"] == min(x["data"] for x in transakcje) else t for t in transakcje]
    else:
        od = min([t["data"] for t in transakcje] + [dt.date.fromisoformat(ustawienia["data_startu"])]) - dt.timedelta(days=10)
        tickery = {t["ticker"] for t in transakcje}
        kursy = {}
        for s in spolki:
            if s["ticker"] in tickery:
                kursy[s["stooq"]] = kursy_akcji(s.get("yahoo") or s["ticker"], s["stooq"], od, dzis,
                                                s.get("nasdaq") or s["ticker"].replace("-", "."))
                time.sleep(1)  # odstęp między spółkami, żeby nie wywołać limitu zapytań
        bn, bk = NASDAQ_BENCHMARK.get(bsym, (None, "index"))
        kursy[bsym] = kursy_akcji(ustawienia["benchmark"].get("yahoo") or YAHOO_BENCHMARK.get(bsym, bsym),
                                  bsym, od, dzis, bn, bk)
        fx = kursy_nbp_usd(od, dzis)

    wynik = policz(ustawienia, spolki, transakcje, kursy, fx, bsym)
    wynik["demo"] = a.demo
    Path(a.wyjscie).write_text(json.dumps(wynik, ensure_ascii=False, indent=1), encoding="utf-8")
    pod = wynik["podsumowanie"]
    print(f"Zapisano {a.wyjscie}: stan na {wynik['stan_na']}, wartość {pod['wartosc_pln']:.0f} PLN, "
          f"zwrot {pod['zwrot_od_startu']}%, {wynik['benchmark']} {pod['benchmark_od_startu']}%"
          + (" (DEMO)" if a.demo else ""))


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError) as e:
        print(f"BŁĄD: {e}", file=sys.stderr)
        sys.exit(1)
