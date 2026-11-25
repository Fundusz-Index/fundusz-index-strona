"""Dzień startu: wpisuje datę i godzinę pierwszej publikacji we wszystkich analizach i w raportach PDF.

Uruchom raz, w dniu startu:  python3 scripts/start.py "21.11.2026, 18:00"
Sama data też przechodzi:   python3 scripts/start.py "21.11.2026"
Skrypt wpisuje datę w sekcjach ujawnień (analizy/*.html), dokleja zaktualizowaną stronę
ujawnień do raportów PDF i sprawdza, czy strona przechodzi kontrolę przed publikacją.
Potem zostaje commit i push; wgranie na Zenbox ruszy samo.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLE = "[data i godzina publikacji]"


def main(argv):
    if len(argv) != 2 or not re.fullmatch(r"\d{2}\.\d{2}\.\d{4}(, \d{2}:\d{2})?", argv[1]):
        sys.exit('Podaj datę startu (z godziną albo bez), np.: python3 scripts/start.py "21.11.2026, 18:00"')
    wpis = argv[1] + (" (czas polski)" if "," in argv[1] else "")
    zmienione = []
    for plik in sorted((ROOT / "analizy").glob("*.html")):
        s = plik.read_text(encoding="utf-8")
        if POLE in s:
            plik.write_text(s.replace(POLE, wpis), encoding="utf-8")
            zmienione.append(plik.name)
    if not zmienione:
        sys.exit("Nie ma już pól „%s”. Data publikacji została wpisana wcześniej." % POLE)
    print("Data publikacji wpisana: " + ", ".join(zmienione))
    for polecenie in (["zrodla/ujawnienia/zbuduj.py"], ["scripts/zbuduj_en.py"], ["scripts/sprawdz_dane.py", "--publikacja"]):
        subprocess.run([sys.executable] + polecenie, cwd=ROOT, check=True)


if __name__ == "__main__":
    main(sys.argv)
