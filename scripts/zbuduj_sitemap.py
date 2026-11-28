"""Buduje sitemap.xml z listy stron (polskie, analizy, angielskie). Uruchamia go też zbuduj_en.py."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADRES = "https://fundusz.knrkindex.pl/"
POMIN = {"404.html"}


def strony():
    pl = [p.name for p in sorted(ROOT.glob("*.html")) if p.name not in POMIN]
    pl = sorted(pl, key=lambda n: (n != "index.html", n))
    analizy = ["analizy/" + p.name for p in sorted((ROOT / "analizy").glob("*.html"))]
    analizy += ["artykuly/" + p.name for p in sorted((ROOT / "artykuly").glob("*.html"))]
    en = ["en/" + p.name for p in sorted((ROOT / "en").glob("*.html")) if p.name not in POMIN]
    en = sorted(en, key=lambda n: (n != "en/index.html", n))
    return pl, analizy, en


def adres(sciezka):
    """Adres kanoniczny: strona główna bez index.html (tak samo jak rel="canonical" na stronach)."""
    if sciezka == "index.html":
        return ADRES
    if sciezka == "en/index.html":
        return ADRES + "en/"
    return ADRES + sciezka


def tresc():
    pl, analizy, en = strony()
    wpisy = []
    for s in pl + analizy + en:
        para = None
        if s in pl and "en/" + s in en:
            para = (s, "en/" + s)
        elif s.startswith("en/") and s[3:] in pl:
            para = (s[3:], s)
        linki = ""
        if para:
            linki = ("\n    <xhtml:link rel=\"alternate\" hreflang=\"pl\" href=\"%s\"/>"
                     "\n    <xhtml:link rel=\"alternate\" hreflang=\"en\" href=\"%s\"/>"
                     "\n    <xhtml:link rel=\"alternate\" hreflang=\"x-default\" href=\"%s\"/>") % (
                adres(para[0]), adres(para[1]), adres(para[0]))
        wpisy.append("  <url>\n    <loc>%s</loc>%s\n  </url>" % (adres(s), linki))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + "\n".join(wpisy) + "\n</urlset>\n")


def main():
    plik = ROOT / "sitemap.xml"
    nowa = tresc()
    if not plik.exists() or plik.read_text(encoding="utf-8") != nowa:
        plik.write_text(nowa, encoding="utf-8")
        print("Zaktualizowano: sitemap.xml")


if __name__ == "__main__":
    main()
