# Strona Funduszu Index

Strona funduszu działa pod adresem **https://fundusz.knrkindex.pl** (od 25.11.2026). To statyczne pliki HTML, CSS i JavaScript, bez WordPressa i bez bazy danych. Jedynym miejscem, w którym się ją zmienia, jest to repozytorium. Wszystko, co trafia na gałąź `main`, w ciągu minuty ląduje na serwerze. Nie trzeba nic wgrywać ręcznie.

Ten plik jest dla ludzi: dla obecnego i każdego kolejnego zarządu funduszu. Jeśli pracujesz z Claude, on czyta `CLAUDE.md` (szczegółowe zasady techniczne i treściowe). Oba pliki opisują to samo, ale z innej strony.

## Jak to działa

```
zmiana w repozytorium (push na main)
      │
      ├─► „Sprawdzenie danych”      sprawdza pliki z danymi, linki i testy
      │
      └─► „Wdrożenie na Zenbox”      testy → kontrola przed publikacją → wgranie przez FTPS
                                        na fundusz.knrkindex.pl (tylko zmienione pliki)

dni robocze, 23:30 czasu polskiego
      │
      └─► „Aktualizacja danych portfela”   pobiera kursy, liczy data/portfolio.json,
                                           robi commit „Dane portfela: …” i uruchamia wgranie
```

Wszystkie trzy automaty to GitHub Actions (zakładka **Actions** w repozytorium). Jeśli któryś się nie uda, GitHub pokazuje czerwony krzyżyk i wysyła e-mail do osoby, która zrobiła zmianę. Strona zostaje wtedy na ostatniej dobrej wersji. Nic się nie psuje publicznie.

Hosting: Zenbox, na koncie hostingowym koła (to samo, na którym stoi knrkindex.pl). Domena `fundusz.knrkindex.pl` jest tam osobną domeną z własnym katalogiem i certyfikatem SSL, więc strona koła i strona funduszu nie mają ze sobą nic wspólnego. Szczegóły i instrukcja odtworzenia: `wdrozenie/README.md`.

## Kto może zmieniać stronę

Potrzebny jest dostęp do tego repozytorium (organizacja **Fundusz-Index** na GitHubie). Nowej osobie daje go ktoś z uprawnieniami właściciela: strona organizacji → **People** → **Invite member**, albo w repozytorium → **Settings** → **Collaborators**. Przy przekazaniu funduszu kolejnemu zarządowi dodaj nowe osoby jako właścicieli organizacji, zanim odejdą stare.

Poza GitHubem są jeszcze dwa miejsca, o których trzeba wiedzieć, ale których na co dzień nikt nie dotyka:

- **Panel Zenbox** (konto koła): domena, certyfikat, konto FTP. Loginy i hasła ma zarząd koła.
- **Sekrety GitHuba** (Settings → Secrets and variables → Actions): dane konta FTP. Wpisane raz, działają same. Hasła nie zapisujemy nigdzie w repozytorium, bo jest publiczne.

## Trzy sposoby, żeby coś zmienić

### 1. Z Claude (najwygodniej)

Tak strona powstała i tak jest utrzymywana. Działa w czacie na claude.ai (projekt „Fundusz INDEX”, z podpiętym GitHubem) albo w Claude Code na komputerze. Na początek wystarczy powiedzieć, co ma się zmienić, np.:

- „Dodaj do portfela kupno Chevron za 10 000 zł z dnia 2.06.2026 z uzasadnieniem: …”
- „Dodaj analizę spółki X. Raport PDF jest w załączniku, autorzy: …, data analizy: …”
- „Zmień skład zarządu na stronie O funduszu: …”
- „Włącz ogłoszenie o Startup Stage 12 grudnia o 18:00 w sali …”
- „Dodaj do kalendarza wyniki kwartalne EMCOR 26 lutego 2027”

Claude czyta `CLAUDE.md`, robi zmianę, przebudowuje wersję angielską, uruchamia testy, robi commit i push. Po minucie zmiana jest na stronie. Jeśli poprosisz, pokaże Ci zrzut ekranu przed wgraniem albo zrobi gałąź i pull request do zatwierdzenia.

### 2. Bezpośrednio na GitHubie w przeglądarce (bez instalowania czegokolwiek)

Dobre do **plików z danymi** w folderze `data/` i PDF-ów w `pliki/`. Otwórz plik na GitHubie → ołówek (Edit) → zmień → **Commit changes** na `main`. Po minucie zmiana jest na stronie. Jeśli coś jest nie tak (np. brakujący przecinek w JSON), „Sprawdzenie danych” zatrzyma wgranie i napisze, co poprawić.

Tą drogą **nie zmieniaj tekstów w plikach `.html`**. Strona ma wersję angielską budowaną skryptem z polskich stron, a testy sprawdzają, czy jest aktualna. Zmiana polskiego tekstu bez przebudowy wersji angielskiej zablokuje wgranie. Teksty stron zmieniaj drogą 1 albo 3.

### 3. Na własnym komputerze

Potrzebny Python 3.12 lub nowszy i git.

```bash
git clone https://github.com/Fundusz-Index/fundusz-index-strona.git
cd fundusz-index-strona
pip install playwright pypdf curl_cffi && python3 -m playwright install chromium
```

Po zmianie, w tej kolejności:

```bash
python3 scripts/zbuduj_en.py            # wersja angielska i mapa strony (po zmianie tekstów, skryptów, danych)
python3 -m unittest discover tests      # testy
python3 scripts/sprawdz_dane.py         # kontrola danych i linków
git add -A && git commit -m "Co i gdzie zmienione" && git push
```

Podgląd przed pushem: `python3 -m http.server 8000` w folderze strony i otwórz http://localhost:8000. Strona wczytuje dane z plików JSON, więc nie zadziała przez dwuklik w plik.

## Typowe zadania

| Zadanie | Co zmienić | Uwagi |
| --- | --- | --- |
| Kupno lub sprzedaż spółki | Wiersz w `data/transakcje.csv` | Nowa spółka musi mieć wpis w `data/spolki.json`. Wyniki przeliczą się w nocy; żeby od razu: Actions → „Aktualizacja danych portfela” → Run workflow. Uzasadnienie trafia do dziennika decyzji, więc napisz je porządnie |
| Nowa analiza | Strona w `analizy/` (kopia innej, np. `analizy/wmb.html`), PDF w `pliki/analizy/`, karta w `data/analizy.json`, obrazek podglądu linku (`zrodla/og/zbuduj.py`), tłumaczenia w `i18n/en.json` | Sekcja ujawnień musi mieć autorów i datę pierwszej publikacji. Na stronach HTML bez ocen „kupuj/trzymaj” i cen docelowych; w PDF-ie zostają. Najprościej z Claude |
| Artykuł | Wpis w `data/artykuly.json` | Działy: Przegląd tygodnia, Profit Journal, Edukacja, Z życia funduszu. Autor zawsze podany |
| Ogłoszenie na stronie głównej | `data/ogloszenie.json` | `"pokaz": true` włącza pasek, `false` wyłącza. Po wydarzeniu wyłącz |
| Kalendarz | `data/kalendarz.json` | Wyniki spółek z portfela, walne, spotkania funduszu. Minione wydarzenia znikają same. `"szacunek": true` dla terminów, których spółka jeszcze nie potwierdziła |
| Zarząd, analitycy, kontakt | `o-funduszu.html` + `i18n/en.json` | Nazwiska i zdjęcia tylko za zgodą osoby |
| Zmiana kapitału, benchmarku, ETF-u gotówki | `data/ustawienia.json` | Rzadko. Każda zmiana przelicza całą historię |
| Dokumenty prawne | `polityka-prywatnosci.html`, `nota-prawna.html`, `regulamin-newslettera.html` | Zmiany po konsultacji z zarządem fundacji |

### Pliki z danymi

- **`transakcje.csv`**: kolumny `data` (RRRR-MM-DD), `typ` (`kupno` albo `sprzedaz`), `ticker`, `kwota_pln` albo `liczba_akcji`, `uzasadnienie`. Jeśli podasz tylko kwotę, skrypt sam policzy liczbę akcji po kursie zamknięcia z dnia transakcji. Uzasadnienie z przecinkami w cudzysłowie.
- **`spolki.json`**: nazwa, symbol w Stooq (np. `googl.us`), sektor, link do analizy, raport PDF, autorzy.
- **`analizy.json`**: karty na stronie Analizy. `link` prowadzi do strony analizy, `raport` daje przycisk „Pobierz raport (PDF)”. Nazwa PDF-a: `fundusz-index-<ticker>-RRRR-MM.pdf`.
- **`artykuly.json`**: `{ "dzial": "Profit Journal", "data": "2026-11-20", "tytul": "…", "wstep": "Dwa zdania.", "autor": "Imię Nazwisko", "link": "https://…" }`.
- **`ogloszenie.json`**, **`kalendarz.json`**, **`ustawienia.json`**: jak w tabeli wyżej.
- **`portfolio.json`**: liczony automatycznie, nie edytuj ręcznie.

Pól w nawiasach kwadratowych, np. `[data]`, nie wolno zostawić na stronie. Kontrola przed publikacją traktuje je jak błąd i zatrzymuje wgranie.

## Co dzieje się samo

- **Dni robocze, 23:30**: pobranie kursów (Yahoo Finance, w razie blokady Nasdaq, potem Stooq) i kursu USD/PLN z NBP, przeliczenie portfela i S&P 500 w złotych, commit i wgranie. Gdy wszystkie źródła zawiodą, dane zostają z poprzedniego dnia; następnej nocy automat nadrobi.
- **Każdy push na `main`**: sprawdzenie danych i wgranie.
- **Certyfikat SSL**: odnawia panel Zenbox.
- Wyniki nie uwzględniają dywidend ani prowizji (w portfelu i w benchmarku). Strona mówi o tym w nocie prawnej.

## Gdy coś pójdzie nie tak

- **Czerwony krzyżyk w Actions**: otwórz przebieg i przeczytaj log. Najczęściej to literówka w JSON albo brakujące tłumaczenie. Popraw i zrób nowy commit.
- **Cofnięcie zmiany**: na GitHubie otwórz commit → **Revert**. Powstaje nowy commit, który odwraca zmianę. Nie przepisuj historii `main`.
- **Zatrzymanie wgrywania na czas prac**: Settings → Secrets and variables → Actions → Variables → `ZENBOX_WLACZONE` ustaw na `nie`. Z powrotem `tak`, gdy skończysz.
- **Dane nie zaktualizowały się w nocy**: Actions → „Aktualizacja danych portfela” → log. Serwisy z kursami czasem blokują GitHuba; Run workflow jeszcze raz zwykle pomaga.
- **Zmiana hasła FTP**: panel Zenbox → Konta FTP → Zmień, potem nowa wartość sekretu `FTP_HASLO` na GitHubie.
- **Strona nie odpowiada, a Actions jest zielone**: problem po stronie hostingu. Sprawdź panel Zenbox (limity pakietu, status domeny) i napisz do pomocy Zenbox.

## O czym pamiętać co roku

- Domena **knrkindex.pl** (koło) wymaga odnowienia w panelu Zenbox w styczniu. Bez niej nie działa ani strona koła, ani fundusz.knrkindex.pl.
- Pakiet hostingu ma limit unikalnych użytkowników miesięcznie. Panel ostrzega, gdy jest przekroczony; wtedy trzeba porozmawiać z pomocą Zenbox o wyższym planie.
- Kalendarz: na początku roku wpisać terminy wyników kwartalnych i walnych spółek z portfela.
- Analizy: po każdej aktualizacji raportu podmienić PDF, wpisać nową datę i przebudować stronę ujawnień (`zrodla/ujawnienia/zbuduj.py`, Claude robi to sam).
- Przy zmianie zarządu: nowi właściciele organizacji na GitHubie, dostęp do panelu Zenbox, przekazanie tego pliku.

## Co jest w repozytorium

| Plik lub folder | Do czego służy |
| --- | --- |
| `index.html`, `portfel.html`, `analizy.html`, `artykuly.html`, `o-funduszu.html` | Strony po polsku |
| `analizy/*.html` | Strony pojedynczych analiz |
| `en/` | Wersja angielska, generowana skryptem. Nie edytuj ręcznie |
| `data/` | Wszystkie dane, które zarząd edytuje |
| `pliki/` | Raporty PDF i oferta dla partnerów |
| `assets/` | Style, skrypty, logo, obrazki podglądu linków |
| `i18n/en.json` | Słownik tłumaczeń polski → angielski |
| `scripts/` | `aktualizuj_dane.py` (kursy i portfel), `sprawdz_dane.py` (kontrola), `zbuduj_en.py` (wersja angielska), `wersje.py` (znaczniki plików CSS/JS), `start.py` (data pierwszej publikacji, użyty raz 25.11.2026) |
| `zrodla/` | Źródła do budowania PDF-ów: ujawnienia w raportach, oferta dla partnerów, obrazki og |
| `tests/` | Testy obliczeń, wersji angielskiej, mapy strony |
| `.github/workflows/` | Trzy automaty opisane wyżej |
| `wdrozenie/` | Jak strona jest wdrożona na Zenbox i jak to odtworzyć |
| `404.html`, `.htaccess`, `robots.txt`, `sitemap.xml` | Strona błędu, ustawienia serwera, mapa strony |
| `CLAUDE.md`, `PRODUCT.md`, `DESIGN.md` | Zasady dla Claude: technika i treść, dla kogo jest strona, wygląd |

## Zasady treści (w skrócie)

Pełna lista w `CLAUDE.md`. Najważniejsze:

- Portfel jest **wirtualny** i strona mówi to wprost. Projekt edukacyjny, nie fundusz inwestycyjny w rozumieniu ustawy, analizy to nie porada inwestycyjna.
- Przy każdej analizie i artykule są autorzy. Każda analiza ma sekcję ujawnień z datą pierwszej publikacji.
- Na stronach HTML nie ma ocen „kupuj/trzymaj” ani cen docelowych. Raporty PDF są w wersji autorów.
- Zdjęcia i nazwiska członków tylko za zgodą. Zawsze „portfel wirtualny”, nigdy „modelowy”.
- Krótkie zdania, naturalny język, bez długich myślników.
- Dodanie analityki, osadzonych filmów lub zewnętrznych czcionek wymaga zmiany polityki prywatności i banera cookies. Dziś strona niczego nie śledzi i nic nie zapisuje w przeglądarce.

Kontakt funduszu: funduszindex@knrkindex.pl. Opiekun techniczny strony w zarządzie: Szymon Jakubowski (2026).
