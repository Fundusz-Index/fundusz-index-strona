"""Dokleja stronę „Ujawnienia i zastrzeżenia” na końcu raportów PDF w pliki/analizy/.

Uruchom: python3 zrodla/ujawnienia/zbuduj.py (wymaga Playwright i pypdf).
Treść ujawnień pochodzi z sekcji #ujawnienia na stronach analizy/<ticker>.html,
reszta z zrodla/ujawnienia/raporty.json. Uruchom ponownie po każdej zmianie ujawnień
(np. w dniu startu, po wpisaniu daty pierwszej publikacji). Skrypt rozpoznaje swoją
stronę i ją podmienia, więc raport nigdy nie ma dwóch takich stron.
"""
import base64
import html
import io
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright
from pypdf import PdfReader, PdfWriter

TU = Path(__file__).resolve().parent
REPO = TU.parents[1]
ZNACZNIK = "Ujawnienia i zastrzeżenia"
NOTA = "fundusz.knrkindex.pl/nota-prawna.html"


def ujawnienia(ticker):
    s = (REPO / "analizy" / (ticker + ".html")).read_text(encoding="utf-8")
    dl = re.search(r'<section id="ujawnienia".*?<dl[^>]*>(.*?)</dl>', s, re.S).group(1)
    czysc = lambda x: html.unescape(re.sub(r"<[^>]+>", "", x)).strip()
    return [(czysc(k), czysc(v)) for k, v in re.findall(r"<dt>(.*?)</dt>\s*<dd>(.*?)</dd>", dl, re.S)]


def e(s):
    s = html.escape(s)
    return re.sub(r"\[([^\]]*)\]", r'<span class="luka">[\1]</span>', s)


def obraz(nazwa):
    return "data:image/png;base64," + base64.b64encode((TU / nazwa).read_bytes()).decode()


CSS_WSPOLNY = """
@page { size: A4; margin: 0 }
* { box-sizing: border-box; margin: 0; padding: 0 }
body { width: 210mm; height: 297mm; font-family: Arial, Helvetica, sans-serif; color: #262626; font-size: 9.6pt; line-height: 1.38; position: relative }
.pod { margin: 1.2mm 0 4.5mm; color: #595959 }
table { width: 100%; border-collapse: collapse; margin-bottom: 4.2mm }
th, td { text-align: left; vertical-align: top; padding: 1.3mm 2.6mm }
.uj th { width: 50mm }
.skala td:first-child { font-weight: 700; width: 38mm }
.skala td:nth-child(2) { width: 34mm; white-space: nowrap }
.uwaga { margin: -2.4mm 0 5mm; font-size: 8.6pt; color: #404040 }
p + p { margin-top: 1.6mm }
.zastrz p { text-align: justify }
.wiecej { margin-top: 4mm; font-size: 8.6pt; color: #404040 }
.luka { color: #8a8a8a; font-style: italic }
"""

CSS = {
    "szary": CSS_WSPOLNY + """
header { background: #666; height: 25mm; border-bottom: 2.2mm solid #1478C7; position: relative }
header img { position: absolute; left: 13mm; top: 3.4mm; width: 19mm }
header .marka { position: absolute; right: 13mm; top: 5.2mm; text-align: right; color: #fff }
header .marka b { font-family: Georgia, 'Times New Roman', serif; font-size: 22pt; letter-spacing: .3pt; display: block; border-bottom: .5mm solid #fff; padding-bottom: 1.2mm; min-width: 105mm }
header .marka span { font-size: 7.4pt; letter-spacing: 2.6pt; display: block; margin-top: 1.4mm }
main { padding: 7.5mm 13mm 0 }
h1 { color: #1478C7; font-size: 17pt; line-height: 1.15 }
h2 { background: #1478C7; color: #fff; font-size: 10.5pt; text-align: center; padding: 1.6mm 0 }
h3 { color: #1478C7; font-size: 12pt; margin-bottom: 1.6mm }
th, td { border-bottom: .35mm solid #fff }
.uj th, .skala th { background: #E7E7E7; font-weight: 700 }
.uj td, .skala td { background: #F2F2F2 }
.wiecej a { color: #1478C7; text-decoration: none }
footer { position: absolute; left: 0; right: 0; bottom: 0; height: 17mm; background: #666; border-top: 2.2mm solid #1478C7 }
footer img { position: absolute; left: 13mm; top: 2.6mm; height: 10mm }
footer .nr { position: absolute; right: 13mm; top: 5mm; color: #fff; font-weight: 700; font-size: 10pt }
""",
    "jasny": CSS_WSPOLNY + """
header { margin: 0 19mm; height: 23.5mm; border-bottom: .9mm solid #FFF600; position: relative }
header img { position: absolute; left: 0; top: 7.9mm; width: 10.5mm }
header .marka { position: absolute; right: 0; bottom: 1.2mm; text-align: right }
header .marka b { font-size: 15pt; letter-spacing: 1.2pt; color: #111; display: block }
header .marka span { font-size: 6.6pt; letter-spacing: 2.6pt; color: #6b6b6b; display: block; margin-top: .6mm }
main { padding: 7mm 19mm 0 }
body { font-size: 10.2pt; line-height: 1.42 }
th, td { padding: 1.7mm 2.8mm }
.uwaga, .wiecej { font-size: 9.2pt }
.pod { margin-bottom: 6mm }
table { margin-bottom: 6mm }
h1 { color: #111; font-size: 17pt; line-height: 1.15 }
h2 { color: #111; font-size: 12.5pt; margin-bottom: 2mm }
h3 { color: #111; font-size: 12.5pt; margin-bottom: 2mm }
th, td { border: .25mm solid #BFBFBF }
.uj th { background: #F2F2F2; font-weight: 700 }
.skala tr:first-child th { background: #111; color: #fff; font-weight: 700 }
.wiecej a { color: #1F4E8C; text-decoration: none }
footer { position: absolute; left: 19mm; right: 19mm; bottom: 6mm; border-top: .25mm solid #BFBFBF; padding-top: 2.2mm; font-size: 7.6pt; color: #6b6b6b }
footer .nr { position: absolute; right: 0; top: 2mm; color: #111; font-weight: 700; font-size: 8.6pt }
""",
}


def strona(ticker, r, numer):
    wiersze = ujawnienia(ticker)
    if r.get("ocena"):
        i = next((n for n, (k, _) in enumerate(wiersze) if k.startswith("Ceny")), len(wiersze))
        wiersze.insert(i, ("Ocena w raporcie", r["ocena"]))
    uj = "".join("<tr><th>%s</th><td>%s</td></tr>" % (e(k), e(v)) for k, v in wiersze)
    skala = ""
    if r.get("ocena"):
        skala = """<h2>Skala ocen funduszu</h2>
<table class="skala">
<tr><th>Ocena</th><th>Potencjał</th><th>Co oznacza</th></tr>
<tr><td>KUPUJ (BUY)</td><td>powyżej +15%</td><td>Wartość z naszego modelu jest wyraźnie wyższa od kursu.</td></tr>
<tr><td>TRZYMAJ (HOLD)</td><td>od −15% do +15%</td><td>Kurs jest blisko wartości z naszego modelu.</td></tr>
<tr><td>SPRZEDAJ (SELL)</td><td>poniżej −15%</td><td>Wartość z naszego modelu jest wyraźnie niższa od kursu.</td></tr>
</table>
<p class="uwaga">Potencjał to wartość z modelu podzielona przez kurs z dnia wyceny, minus 1. Wartość podajemy na dzień wyceny, a nie jako prognozę kursu na określony termin. Progi są takie same we wszystkich analizach funduszu. Ocena odnosi się do dnia wyceny i nie jest automatycznie aktualizowana.</p>"""
    styl = r["styl"]
    if styl == "szary":
        naglowek_tabeli = "<h2>Ujawnienia</h2>"
        stopka = '<img src="%s" alt=""><span class="nr">Strona | %d</span>' % (obraz(r["logo_spolki"]), numer)
    else:
        naglowek_tabeli = "<h2>Ujawnienia</h2>"
        stopka = '%s · Raport analityczny<span class="nr">Strona | %d</span>' % (e(r["spolka"]), numer)
    return """<!DOCTYPE html><html lang="pl"><head><meta charset="utf-8"><style>%s</style></head><body>
<header><img src="%s" alt=""><div class="marka"><b>FUNDUSZ INDEX</b><span>KNRK INDEX · UEK KRAKÓW</span></div></header>
<main>
<h1>%s</h1>
<p class="pod">%s · %s</p>
%s
<table class="uj">%s</table>
%s
<div class="zastrz">
<h3>Zastrzeżenia</h3>
<p>Fundusz Index to edukacyjny projekt studentów Koła Naukowego Rynku Kapitałowego INDEX na Uniwersytecie Ekonomicznym w Krakowie, prowadzony przez Fundację Index (KRS 0001137760). Nie jest funduszem inwestycyjnym w rozumieniu ustawy z 27 maja 2004 r. o funduszach inwestycyjnych, nie zbiera pieniędzy na inwestycje i nie prowadzi działalności maklerskiej. Portfel funduszu jest wirtualny.</p>
<p>Raport wyraża poglądy autorów według stanu na dzień wyceny. Nie jest poradą inwestycyjną i nie uwzględnia sytuacji, celów ani wiedzy żadnego czytelnika. Może zawierać błędy, mimo że korzystamy z wiarygodnych źródeł. Źródła podajemy przy rysunkach i w części ze źródłami.</p>
<p>Inwestowanie wiąże się z ryzykiem, w tym z utratą części lub całości zainwestowanych pieniędzy. Decyzje inwestycyjne podejmujesz samodzielnie i na własne ryzyko.</p>
</div>
<p class="wiecej">Nota prawna: <a href="https://%s">%s</a> · Strona analizy: <a href="https://fundusz.knrkindex.pl/analizy/%s.html">fundusz.knrkindex.pl/analizy/%s.html</a> · Kontakt: <a href="mailto:funduszindex@knrkindex.pl">funduszindex@knrkindex.pl</a></p>
</main>
<footer>%s</footer>
</body></html>""" % (CSS[styl], obraz("byk.png"), ZNACZNIK, e(r["spolka"]), e(r["raport"]),
                      naglowek_tabeli, uj, skala, NOTA, NOTA, ticker, ticker, stopka)


def nasza(strona_pdf):
    t = strona_pdf.extract_text() or ""
    return ZNACZNIK in t and NOTA in t


def main(tylko=None, podglad=None):
    raporty = {k: v for k, v in json.loads((TU / "raporty.json").read_text(encoding="utf-8")).items() if not k.startswith("_")}
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        for ticker, r in raporty.items():
            if tylko and ticker not in tylko:
                continue
            sciezka = REPO / r["plik"]
            czytnik = PdfReader(str(sciezka))
            strony = list(czytnik.pages)
            if strony and nasza(strony[-1]):
                strony = strony[:-1]
            # Okładka nie ma numeru, więc nowa strona ma numer równy liczbie stron raportu.
            pg.set_content(strona(ticker, r, len(strony)))
            nowa = PdfReader(io.BytesIO(pg.pdf(format="A4", print_background=True, prefer_css_page_size=True)))
            if len(nowa.pages) != 1:
                sys.exit("%s: strona ujawnień nie mieści się na jednej stronie A4" % ticker)
            w = PdfWriter(clone_from=czytnik)
            while len(w.pages) > len(strony):
                w.remove_page(len(w.pages) - 1)
            w.add_page(nowa.pages[0])
            w.pages[-1].compress_content_streams()
            w.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
            cel = Path(podglad) / sciezka.name if podglad else sciezka
            with open(cel, "wb") as f:
                w.write(f)
            # pypdf zapisuje obiekty bez strumieni obiektów, więc plik rośnie. qpdf (jeśli jest) go odchudza.
            if shutil.which("qpdf"):
                tmp = cel.with_suffix(".tmp.pdf")
                subprocess.run(["qpdf", "--object-streams=generate", "--compress-streams=y", "--recompress-flate",
                                str(cel), str(tmp)], check=True)
                tmp.replace(cel)
            print("%s: %d stron + ujawnienia -> %s" % (ticker, len(strony), cel.relative_to(REPO) if not podglad else cel))
        b.close()


if __name__ == "__main__":
    import argparse
    a = argparse.ArgumentParser()
    a.add_argument("ticker", nargs="*", help="tylko te raporty (domyślnie wszystkie)")
    a.add_argument("--podglad", help="zapisz do tego katalogu zamiast nadpisywać pliki/analizy")
    x = a.parse_args()
    main(x.ticker or None, x.podglad)
