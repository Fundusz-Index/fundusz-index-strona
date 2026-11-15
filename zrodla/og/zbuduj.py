"""Buduje obrazki podglądu linków (og:image, 1200×630) do assets/img/og/.

Uruchom: python3 zrodla/og/zbuduj.py (wymaga Playwright). Uruchom ponownie po dodaniu analizy.
"""
import asyncio
import json
from pathlib import Path
from urllib.parse import urlencode

from playwright.async_api import async_playwright

TU = Path(__file__).resolve().parent
REPO = TU.parents[1]
MIESIACE = ["styczeń", "luty", "marzec", "kwiecień", "maj", "czerwiec", "lipiec", "sierpień",
            "wrzesień", "październik", "listopad", "grudzień"]


def obrazki():
    yield "fundusz-index", {
        "gora": "KNRK INDEX · UEK w Krakowie",
        "etykieta": "Studencki fundusz",
        "tytul": "Analizujemy spółki, wyceniamy je i prowadzimy portfel wirtualny.",
        "dol": "Portfel na tle S&amp;P 500, analizy z nazwiskami autorów,<br>dziennik każdej decyzji.",
    }
    for a in json.loads((REPO / "data" / "analizy.json").read_text(encoding="utf-8")):
        rok, mies = a["data"].split("-")[:2]
        yield "analiza-" + a["ticker"].lower(), {
            "gora": "KNRK INDEX · UEK w Krakowie",
            "etykieta": "Analiza · %s %s" % (MIESIACE[int(mies) - 1], rok),
            "tytul": a["nazwa"],
            "ticker": a["ticker"] + " · " + a["sektor"],
            "dol": "Autorzy: <b>%s</b>" % a["autorzy"],
        }


async def main():
    wyj = REPO / "assets" / "img" / "og"
    wyj.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1200, "height": 630})
        for nazwa, pola in obrazki():
            await pg.goto("file://" + str(TU / "szablon.html") + "?" + urlencode(pola))
            await pg.wait_for_timeout(200)
            await pg.screenshot(path=str(wyj / (nazwa + ".png")))
            print(nazwa)
        await b.close()


asyncio.run(main())
