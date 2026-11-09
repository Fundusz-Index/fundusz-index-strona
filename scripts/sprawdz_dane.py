#!/usr/bin/env python3
"""Sprawdza pliki z danymi i strony przed publikacją.

Błędy (zatrzymują aktualizację i publikację):
  - zła składnia JSON lub CSV,
  - brakujące lub błędne pola (data, typ transakcji, kwota, ticker),
  - ticker w transakcjach bez wpisu w spolki.json,
  - sprzedaż większej liczby akcji niż kupiono,
  - link na stronie do pliku, którego nie ma.

Ostrzeżenia (nie zatrzymują, chyba że użyjesz --publikacja):
  - pola do uzupełnienia w nawiasach kwadratowych, np. [rok],
  - ogłoszenie włączone bez tytułu lub linku.

Użycie:
  python3 scripts/sprawdz_dane.py               # sprawdzenie codzienne
  python3 scripts/sprawdz_dane.py --publikacja  # przed startem strony: ostrzeżenia też są błędami
"""

import argparse
import csv
import datetime as dt
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DZIALY = {"Przegląd tygodnia", "Profit Journal", "Edukacja", "Z życia funduszu"}
NAWIAS = re.compile(r"\[[^\]\n]{1,60}\]")


class Raport:
    def __init__(self):
        self.bledy, self.ostrzezenia = [], []

    def blad(self, gdzie, tekst):
        self.bledy.append(f"{gdzie}: {tekst}")

    def uwaga(self, gdzie, tekst):
        self.ostrzezenia.append(f"{gdzie}: {tekst}")


def wczytaj_json(r, nazwa):
    sciezka = DATA / nazwa
    if not sciezka.exists():
        r.blad(f"data/{nazwa}", "brak pliku")
        return None
    try:
        return json.loads(sciezka.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        r.blad(f"data/{nazwa}, wiersz {e.lineno}, znak {e.colno}",
               f"zła składnia JSON ({e.msg}). Sprawdź przecinki, cudzysłowy i nawiasy.")
        return None


def data_ok(tekst, format_="%Y-%m-%d"):
    try:
        return dt.datetime.strptime(tekst, format_).date()
    except (TypeError, ValueError):
        return None


def liczba(tekst):
    tekst = (tekst or "").strip().replace(" ", "").replace(" ", "").replace(",", ".")
    if not tekst:
        return None
    try:
        return float(tekst)
    except ValueError:
        return "zla"


def sprawdz_ustawienia(r):
    u = wczytaj_json(r, "ustawienia.json")
    if u is None:
        return
    g = "data/ustawienia.json"
    if not isinstance(u.get("kapital_startowy_pln"), (int, float)) or u["kapital_startowy_pln"] <= 0:
        r.blad(g, "kapital_startowy_pln musi być liczbą większą od zera")
    if not data_ok(u.get("data_startu")):
        r.blad(g, "data_startu musi mieć format RRRR-MM-DD")
    if not (u.get("benchmark") or {}).get("stooq"):
        r.blad(g, "brak symbolu benchmarku w polu benchmark.stooq")


def sprawdz_spolki(r):
    s = wczytaj_json(r, "spolki.json")
    if s is None:
        return {}
    g = "data/spolki.json"
    if not isinstance(s, list):
        r.blad(g, "plik musi być listą spółek w nawiasach [ ]")
        return {}
    wynik = {}
    for i, x in enumerate(s, start=1):
        gdzie = f"{g}, spółka nr {i}"
        if not isinstance(x, dict):
            r.blad(gdzie, "wpis musi być obiektem w nawiasach { }")
            continue
        for pole in ("ticker", "nazwa", "stooq", "sektor"):
            if not str(x.get(pole) or "").strip():
                r.blad(gdzie, f"brak pola '{pole}'")
        t = str(x.get("ticker") or "").upper()
        if t in wynik:
            r.blad(gdzie, f"ticker {t} występuje dwa razy")
        if x.get("stooq") and not re.fullmatch(r"[a-z0-9.\-^]+", x["stooq"]):
            r.blad(gdzie, f"symbol Stooq '{x['stooq']}' wygląda na błędny (np. googl.us, małymi literami)")
        if x.get("analiza") and not (ROOT / x["analiza"]).exists():
            r.blad(gdzie, f"link do analizy '{x['analiza']}' prowadzi do pliku, którego nie ma")
        if t:
            wynik[t] = x
    return wynik


def sprawdz_transakcje(r, spolki):
    sciezka = DATA / "transakcje.csv"
    g = "data/transakcje.csv"
    if not sciezka.exists():
        r.blad(g, "brak pliku")
        return
    try:
        wiersze = list(csv.DictReader(sciezka.read_text(encoding="utf-8").splitlines()))
    except csv.Error as e:
        r.blad(g, f"zła składnia CSV: {e}")
        return
    wymagane = {"data", "typ", "ticker", "kwota_pln", "liczba_akcji", "uzasadnienie"}
    naglowek = set(wiersze[0].keys()) if wiersze else set()
    if wiersze and not wymagane <= naglowek:
        r.blad(g, "pierwszy wiersz musi zawierać kolumny: " + ",".join(sorted(wymagane)))
        return
    dzis = dt.date.today()
    akcje = {}
    for nr, w in enumerate(wiersze, start=2):
        gdzie = f"{g}, wiersz {nr}"
        if None in w:
            r.blad(gdzie, "za dużo kolumn. Tekst z przecinkiem weź w cudzysłów: \"tak, jak tu\"")
            continue
        if not any((v or "").strip() for v in w.values()):
            continue
        d = data_ok((w["data"] or "").strip())
        if not d:
            r.blad(gdzie, f"data '{w['data']}' musi mieć format RRRR-MM-DD")
        elif d > dzis:
            r.blad(gdzie, f"data {d} jest w przyszłości")
        typ = (w["typ"] or "").strip().lower()
        if typ not in ("kupno", "sprzedaz", "sprzedaż"):
            r.blad(gdzie, f"typ '{w['typ']}' musi być 'kupno' albo 'sprzedaz'")
        t = (w["ticker"] or "").strip().upper()
        if t not in spolki:
            r.blad(gdzie, f"ticker '{t}' nie ma wpisu w data/spolki.json")
        kw, ak = liczba(w["kwota_pln"]), liczba(w["liczba_akcji"])
        if kw == "zla" or ak == "zla":
            r.blad(gdzie, "kwota_pln i liczba_akcji muszą być liczbami (np. 20000 albo 12,5)")
            continue
        if kw is None and ak is None:
            r.blad(gdzie, "podaj kwota_pln albo liczba_akcji")
        if (kw is not None and kw <= 0) or (ak is not None and ak <= 0):
            r.blad(gdzie, "kwota i liczba akcji muszą być większe od zera")
        if typ.startswith("sprzeda"):
            if t not in akcje:
                r.blad(gdzie, f"sprzedaż {t}, którego wcześniej nie kupiono")
            elif ak is not None and ak > akcje[t] + 1e-9:
                r.blad(gdzie, f"sprzedaż {ak:g} akcji {t}, a w portfelu jest {akcje[t]:g}")
        if typ == "kupno":
            # przy kupnie za kwotę liczbę akcji liczy dopiero skrypt, więc jej nie znamy
            akcje[t] = akcje.get(t, 0) + (ak if ak is not None else float("inf"))
        elif t in akcje and ak is not None:
            akcje[t] -= ak
        if not (w["uzasadnienie"] or "").strip():
            r.uwaga(gdzie, "brak uzasadnienia. Na stronie zobaczysz pustą tezę przy spółce.")


def sprawdz_analizy(r):
    a = wczytaj_json(r, "analizy.json")
    if a is None:
        return
    g = "data/analizy.json"
    if not isinstance(a, list):
        r.blad(g, "plik musi być listą w nawiasach [ ]")
        return
    for i, x in enumerate(a, start=1):
        gdzie = f"{g}, analiza nr {i}"
        for pole in ("ticker", "nazwa", "sektor", "data", "autorzy", "link"):
            if not str(x.get(pole) or "").strip():
                r.blad(gdzie, f"brak pola '{pole}' (autorzy są obowiązkowi)")
        if x.get("data") and not data_ok(x["data"], "%Y-%m"):
            r.blad(gdzie, f"data '{x['data']}' musi mieć format RRRR-MM")
        if x.get("link") and not (ROOT / x["link"]).exists():
            r.blad(gdzie, f"strona analizy '{x['link']}' nie istnieje")


def sprawdz_artykuly(r):
    a = wczytaj_json(r, "artykuly.json")
    if a is None:
        return
    g = "data/artykuly.json"
    if not isinstance(a, list):
        r.blad(g, "plik musi być listą w nawiasach [ ]")
        return
    for i, x in enumerate(a, start=1):
        gdzie = f"{g}, artykuł nr {i}"
        for pole in ("dzial", "data", "tytul", "autor"):
            if not str(x.get(pole) or "").strip():
                r.blad(gdzie, f"brak pola '{pole}'")
        if x.get("dzial") and x["dzial"] not in DZIALY:
            r.blad(gdzie, f"dział '{x['dzial']}' musi być jednym z: {', '.join(sorted(DZIALY))}")
        if x.get("data") and not data_ok(x["data"]):
            r.blad(gdzie, f"data '{x['data']}' musi mieć format RRRR-MM-DD")


def sprawdz_ogloszenie(r):
    o = wczytaj_json(r, "ogloszenie.json")
    if o is None:
        return
    g = "data/ogloszenie.json"
    if not isinstance(o.get("pokaz"), bool):
        r.blad(g, "pole 'pokaz' musi mieć wartość true albo false (bez cudzysłowu)")
    elif o["pokaz"]:
        if not str(o.get("tytul") or "").strip():
            r.blad(g, "ogłoszenie jest włączone, ale nie ma tytułu")
        if NAWIAS.search(json.dumps(o, ensure_ascii=False)):
            r.uwaga(g, "ogłoszenie jest włączone, a ma pola do uzupełnienia w nawiasach [ ]")
        if not o.get("link"):
            r.uwaga(g, "ogłoszenie nie ma linku do szczegółów")


class Linki(HTMLParser):
    def __init__(self):
        super().__init__()
        self.linki = []

    def handle_starttag(self, tag, attrs):
        for k, v in attrs:
            if k in ("href", "src") and v:
                self.linki.append((self.getpos()[0], v))


def sprawdz_strony(r):
    for plik in sorted(ROOT.glob("*.html")) + sorted((ROOT / "analizy").glob("*.html")):
        tekst = plik.read_text(encoding="utf-8")
        wzgl = plik.relative_to(ROOT).as_posix()
        p = Linki()
        p.feed(tekst)
        for wiersz, link in p.linki:
            if re.match(r"^(https?:|mailto:|tel:|#|data:)", link) or link == "#":
                continue
            cel = link.split("#")[0].split("?")[0]
            if cel and not (plik.parent / cel).resolve().exists():
                r.blad(f"{wzgl}, wiersz {wiersz}", f"link '{link}' prowadzi do pliku, którego nie ma")
        for nr, linia in enumerate(tekst.splitlines(), start=1):
            for m in NAWIAS.finditer(re.sub(r"<[^>]+>", " ", linia)):
                r.uwaga(f"{wzgl}, wiersz {nr}", f"do uzupełnienia: {m.group(0)}")
    for nazwa in ("spolki.json", "analizy.json", "artykuly.json"):
        sciezka = DATA / nazwa
        if sciezka.exists():
            for nr, linia in enumerate(sciezka.read_text(encoding="utf-8").splitlines(), start=1):
                for m in NAWIAS.finditer(linia):
                    r.uwaga(f"data/{nazwa}, wiersz {nr}", f"do uzupełnienia: {m.group(0)}")


def sprawdz(publikacja=False):
    r = Raport()
    sprawdz_ustawienia(r)
    spolki = sprawdz_spolki(r)
    sprawdz_transakcje(r, spolki)
    sprawdz_analizy(r)
    sprawdz_artykuly(r)
    sprawdz_ogloszenie(r)
    sprawdz_strony(r)
    if publikacja:
        r.bledy += r.ostrzezenia
        r.ostrzezenia = []
    return r


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--publikacja", action="store_true", help="traktuj ostrzeżenia jak błędy (przed startem strony)")
    a = p.parse_args(argv)
    r = sprawdz(a.publikacja)
    for o in r.ostrzezenia:
        print(f"UWAGA  {o}")
    for b in r.bledy:
        print(f"BŁĄD   {b}")
    if r.bledy:
        print(f"\nZnaleziono błędy: {len(r.bledy)}. Popraw je przed publikacją.")
        return 1
    print(f"\nPliki są w porządku. Ostrzeżenia: {len(r.ostrzezenia)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
