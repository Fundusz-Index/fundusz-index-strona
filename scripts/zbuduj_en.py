"""Buduje angielską wersję strony w katalogu en/ z polskich plików HTML i słownika i18n/en.json.

Polskie strony są źródłem. Skrypt kopiuje je, podmienia teksty według słownika, poprawia ścieżki
i przełącznik języka. Generuje też assets/js/en.js (słownik dla skryptów i danych).

Uruchom po każdej zmianie na stronie:   python3 scripts/zbuduj_en.py
Sprawdzenie bez zapisu (kod wyjścia 1):  python3 scripts/zbuduj_en.py --sprawdz
Lista tekstów bez tłumaczenia:          python3 scripts/zbuduj_en.py --braki
"""
import html as htmllib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wersje

REPO = Path(__file__).resolve().parents[1]
SLOWNIK = REPO / "i18n" / "en.json"
STRONY = ["index.html", "portfel.html", "analizy.html", "artykuly.html", "o-funduszu.html"]
ATRYBUTY = ("aria-label", "alt", "title", "placeholder")
META = ('name="description"', 'property="og:title"', 'property="og:description"', 'name="twitter:title"')
ZNACZNIK = re.compile(r"(<!--[\s\S]*?-->|<script[\s\S]*?</script>|<style[\s\S]*?</style>|<[^>]+>)")
LITERA = re.compile(r"[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż]")


def wczytaj():
    d = json.loads(SLOWNIK.read_text(encoding="utf-8"))
    return d["teksty"], set(d.get("bez_zmian", []))


def klucz(s):
    return re.sub(r"\s+", " ", htmllib.unescape(s)).strip()


def tlumacz(surowy, teksty, bez_zmian, braki, w_atrybucie=False):
    k = klucz(surowy)
    if not k:
        return surowy
    if k in teksty:
        en = htmllib.escape(teksty[k], quote=w_atrybucie)
        przed = surowy[: len(surowy) - len(surowy.lstrip())]
        po = surowy[len(surowy.rstrip()):]
        return przed + en + po
    if LITERA.search(k) and k not in bez_zmian:
        braki.add(k)
    return surowy


def sciezka(link):
    """Linki do przetłumaczonych stron zostają w en/. Reszta wskazuje katalog wyżej."""
    if re.match(r"^(https?:|mailto:|tel:|#|data:|\.\./)", link) or not link:
        return link
    cel = link.split("#")[0].split("?")[0]
    if cel in STRONY:
        return link
    return "../" + link


def znacznik(tag, teksty, bez_zmian, braki, nazwa):
    if tag.startswith("<!--") or tag.startswith("<script") and "src=" not in tag[:200] or tag.startswith("<style"):
        return tag
    if tag.startswith("<html"):
        return tag.replace('lang="pl"', 'lang="en"')
    if tag.startswith("<meta") and 'property="og:locale"' in tag:
        return tag.replace("pl_PL", "en_GB")
    if tag.startswith("<meta") and 'property="og:url"' in tag:
        return tag.replace("https://fundusz.knrkindex.pl/", "https://fundusz.knrkindex.pl/en/")
    if tag.startswith("<link") and 'rel="canonical"' in tag:
        return tag.replace("https://fundusz.knrkindex.pl/", "https://fundusz.knrkindex.pl/en/")
    if tag.startswith("<meta") and any(m in tag for m in META):
        return re.sub(r'content="([^"]*)"', lambda m: 'content="' + tlumacz(m.group(1), teksty, bez_zmian, braki, True) + '"', tag)
    if tag.startswith("<body"):
        return tag.replace('data-base=""', 'data-base="../" data-pages=""')
    if 'class="lang-switch"' in tag:
        return '<a class="lang-switch" href="../%s" hreflang="pl" lang="pl" aria-label="Polska wersja strony">' % nazwa
    tag = re.sub(r'\b(href|src)="([^"]*)"', lambda m: m.group(1) + '="' + sciezka(m.group(2)) + '"', tag)
    for a in ATRYBUTY:
        tag = re.sub(r'\b%s="([^"]*)"' % a, lambda m: a + '="' + tlumacz(m.group(1), teksty, bez_zmian, braki, True) + '"', tag)
    return tag


def zbuduj_strone(nazwa, teksty, bez_zmian, braki):
    zrodlo = (REPO / nazwa).read_text(encoding="utf-8")
    czesci = ZNACZNIK.split(zrodlo)
    wynik = []
    po_przelaczniku = False
    for cz in czesci:
        if cz.startswith("<"):
            nowy = znacznik(cz, teksty, bez_zmian, braki, nazwa)
            po_przelaczniku = 'class="lang-switch"' in cz
            wynik.append(nowy)
        elif po_przelaczniku and cz.strip() == "EN":
            wynik.append(cz.replace("EN", "PL"))
            po_przelaczniku = False
        else:
            wynik.append(tlumacz(cz, teksty, bez_zmian, braki))
    out = "".join(wynik)
    out = out.replace('<script src="../assets/js/wspolne.js', '<script src="../assets/js/en.js" defer></script>\n<script src="../assets/js/wspolne.js', 1)
    return out


def en_js(teksty):
    return ("/* Wygenerowane przez scripts/zbuduj_en.py z i18n/en.json. Nie edytuj ręcznie. */\n"
            "window.FI_EN = " + json.dumps(teksty, ensure_ascii=False, sort_keys=True, indent=0) + ";\n")


def zbuduj(zapisz=True):
    teksty, bez_zmian = wczytaj()
    braki, rozne = set(), []
    wersje.nieaktualne(zapisz=zapisz)
    js = REPO / "assets" / "js" / "en.js"
    nowy_js = en_js(teksty)
    if not js.exists() or js.read_text(encoding="utf-8") != nowy_js:
        rozne.append("assets/js/en.js")
        if zapisz:
            js.write_text(nowy_js, encoding="utf-8")
    (REPO / "en").mkdir(exist_ok=True)
    for nazwa in STRONY:
        cel = REPO / "en" / nazwa
        nowa = wersje.przepisz(zbuduj_strone(nazwa, teksty, bez_zmian, braki), cel.parent)
        if not cel.exists() or cel.read_text(encoding="utf-8") != nowa:
            rozne.append("en/" + nazwa)
            if zapisz:
                cel.write_text(nowa, encoding="utf-8")
    return rozne, sorted(braki)


if __name__ == "__main__":
    if "--braki" in sys.argv:
        _, braki = zbuduj(zapisz=False)
        print("\n".join(braki) if braki else "Wszystkie teksty mają tłumaczenie.")
        sys.exit(0)
    sprawdz = "--sprawdz" in sys.argv
    rozne, braki = zbuduj(zapisz=not sprawdz)
    if not sprawdz:
        import zbuduj_sitemap
        zbuduj_sitemap.main()
    if braki:
        print("Teksty bez tłumaczenia w i18n/en.json (%d). Lista: python3 scripts/zbuduj_en.py --braki" % len(braki))
    if sprawdz and rozne:
        print("Wersja angielska jest nieaktualna: " + ", ".join(rozne) + ". Uruchom: python3 scripts/zbuduj_en.py")
        sys.exit(1)
    print("Zaktualizowano: " + ", ".join(rozne) if rozne else "Wersja angielska jest aktualna.")
