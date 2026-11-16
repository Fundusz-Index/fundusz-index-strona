"""Dopisuje do odwołań do CSS i JS w plikach HTML znacznik wersji (?v=skrót treści pliku).

Po co: przeglądarka trzyma stare style i skrypty w pamięci podręcznej. Gdy plik się zmieni,
zmienia się jego skrót, więc przeglądarka pobiera nową wersję od razu.

Uruchom po każdej zmianie w assets/css lub assets/js:  python3 scripts/wersje.py
Sprawdzenie bez zapisu (kod wyjścia 1, gdy coś jest nieaktualne): python3 scripts/wersje.py --sprawdz
"""
import hashlib
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
WZOR = re.compile(r'((?:src|href)=")((?:\.\./)?assets/(?:css|js)/[\w.-]+\.(?:css|js))(?:\?v=[0-9a-f]+)?(")')


def skrot(sciezka):
    return hashlib.md5(sciezka.read_bytes()).hexdigest()[:8]


def przepisz(html, katalog):
    def zamien(m):
        plik = (katalog / m.group(2)).resolve()
        if not plik.is_file():
            return m.group(0)
        return m.group(1) + m.group(2) + "?v=" + skrot(plik) + m.group(3)
    return WZOR.sub(zamien, html)


def nieaktualne(repo=REPO, zapisz=False):
    zle = []
    for f in sorted(list(repo.glob("*.html")) + list(repo.glob("analizy/*.html"))):
        stary = f.read_text(encoding="utf-8")
        nowy = przepisz(stary, f.parent)
        if nowy != stary:
            zle.append(str(f.relative_to(repo)))
            if zapisz:
                f.write_text(nowy, encoding="utf-8")
    return zle


if __name__ == "__main__":
    tylko_sprawdz = "--sprawdz" in sys.argv
    lista = nieaktualne(zapisz=not tylko_sprawdz)
    if tylko_sprawdz and lista:
        print("Nieaktualne wersje CSS/JS w: " + ", ".join(lista) + ". Uruchom: python3 scripts/wersje.py")
        sys.exit(1)
    print("Zaktualizowano: " + ", ".join(lista) if lista else "Wersje CSS i JS są aktualne.")
