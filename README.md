# Strona Funduszu Index

Strona funduszu pod adresem **fundusz.knrkindex.pl**. Statyczne pliki HTML, CSS i JavaScript, bez WordPressa i bez bazy danych. Wyniki portfela liczy skrypt w Pythonie raz dziennie.

## Co jest w środku

| Plik lub folder | Do czego służy |
| --- | --- |
| `index.html` | Start: pasek kursów, ogłoszenie, portfel w skrócie, partnerzy |
| `portfel.html` | Portfel: wykres na tle S&P 500, skład, spółki z tezami, dziennik decyzji |
| `analizy.html`, `analizy/wmb.html` | Biblioteka analiz z filtrami i strona analizy |
| `artykuly.html` | Artykuły w działach (Przegląd tygodnia, Profit Journal, Edukacja, Z życia funduszu) |
| `o-funduszu.html` | Proces decyzyjny, zarząd, analitycy, kontakt |
| `data/` | Wszystkie dane, które zarząd edytuje (opis niżej) |
| `scripts/aktualizuj_dane.py` | Pobiera kursy i liczy `data/portfolio.json` |
| `tests/` | Testy obliczeń portfela |
| `.github/workflows/` | Automatyczna aktualizacja danych raz dziennie |
| `wdrozenie/` | Przykład wgrywania na Zenbox przez FTP |

## Jak edytować treści

Wszystko, co zmienia się regularnie, siedzi w folderze `data/`:

- **`transakcje.csv`**: każde kupno i sprzedaż. Kolumny: `data` (RRRR-MM-DD), `typ` (`kupno` albo `sprzedaz`), `ticker`, `kwota_pln` albo `liczba_akcji`, `uzasadnienie`. Jeśli podasz tylko kwotę, skrypt sam policzy liczbę akcji po kursie zamknięcia z dnia transakcji (albo z najbliższej sesji po nim).
- **`spolki.json`**: opis każdej spółki: nazwa, symbol w Stooq (np. `googl.us`), sektor, link do analizy i autorzy. Nowa spółka w transakcjach musi mieć tu wpis.
- **`analizy.json`**: karty na stronie Analizy. Nowa analiza to nowy wpis i nowa strona w `analizy/` (najprościej skopiować `analizy/wmb.html`). Pliki PDF i Excel wrzucajcie do folderu `pliki/analizy/`.
- **`artykuly.json`**: lista artykułów. Przykład wpisu:
  ```json
  { "dzial": "Profit Journal", "data": "2026-11-20", "tytul": "Tytuł", "wstep": "Dwa zdania wstępu.", "autor": "Imię Nazwisko", "link": "https://..." }
  ```
- **`ogloszenie.json`**: pasek z wydarzeniem na stronie głównej, np. Startup Stage. Ustaw `"pokaz": true`, wpisz tytuł, tekst i link. Po wydarzeniu zmień na `false`.
- **`ustawienia.json`**: kapitał startowy, data startu, benchmark.

Pól w nawiasach kwadratowych, np. `[rok]`, `[adres e-mail funduszu]`, `[osoba 2]`, nie wolno zostawić na stronie publicznej.

## Sprawdzanie plików

Skrypt `scripts/sprawdz_dane.py` sprawdza wszystkie pliki z danymi i strony. Uruchamia się sam po każdej zmianie w repozytorium i przed codzienną aktualizacją. Przy błędzie GitHub pokaże czerwony krzyżyk przy zmianie i wyśle e-mail do osoby, która ją wprowadziła. Codzienna aktualizacja i wgrywanie na Zenbox zatrzymują się wtedy, więc na stronie zostaje ostatnia dobra wersja. Przy Cloudflare Pages to samo zapewnia polecenie budowania (krok 3 wdrożenia).

Błędy, które zatrzymują aktualizację:

- zła składnia JSON (brakujący przecinek, cudzysłów, nawias),
- przecinek w uzasadnieniu bez cudzysłowu w `transakcje.csv`,
- zła data, typ transakcji albo kwota,
- ticker bez wpisu w `spolki.json`,
- sprzedaż spółki, której nie ma w portfelu, albo większej liczby akcji niż kupiono,
- link do strony lub pliku, którego nie ma,
- analiza bez autorów, artykuł spoza listy działów,
- włączone ogłoszenie bez tytułu.

Ostrzeżenia to pola w nawiasach `[ ]` i brakujące uzasadnienia. Przed startem strony uruchom tryb publikacji, w którym ostrzeżenia też są błędami:

```bash
python3 scripts/sprawdz_dane.py               # codzienne sprawdzenie
python3 scripts/sprawdz_dane.py --publikacja  # przed startem strony
```

## Dane portfela

Skrypt `scripts/aktualizuj_dane.py`:

1. czyta `transakcje.csv` i `spolki.json`,
2. pobiera kursy zamknięcia akcji i S&P 500: najpierw z Yahoo Finance, a gdy nie odpowie, z Nasdaq, potem ze Stooq,
3. pobiera średni kurs USD/PLN z NBP (tabela A),
4. liczy wartość portfela i S&P 500 w PLN dzień po dniu,
5. zapisuje `data/portfolio.json`, z którego korzysta strona.

Obecny plik `portfolio.json` zawiera **dane przykładowe** (`"demo": true`). Strona pokazuje wtedy notkę o danych przykładowych. Pierwsze uruchomienie bez `--demo` zastąpi je prawdziwymi wynikami od 25.10.2026.

```bash
python3 scripts/aktualizuj_dane.py          # prawdziwe dane (potrzebny internet)
python3 scripts/aktualizuj_dane.py --demo   # dane przykładowe
python3 -m unittest discover tests          # testy obliczeń
```

Ograniczenia: wyniki nie uwzględniają dywidend ani prowizji, zarówno w portfelu, jak i w S&P 500. Serwisy z kursami czasem blokują pobieranie z serwerów GitHuba. Skrypt łączy się jak przeglądarka (biblioteka `curl_cffi`), ponawia próby i przechodzi do kolejnego źródła. Gdy zawiodą wszystkie, zostawia poprzedni plik bez zmian. Ręczne uruchomienie w trakcie sesji w USA pokaże kurs bieżący, a nie zamknięcia; automat działa po zamknięciu.

## Podgląd na komputerze

Strona wczytuje dane z plików JSON, więc nie zadziała przez dwuklik w plik. Uruchom w folderze strony:

```bash
python3 -m http.server 8000
```

i otwórz http://localhost:8000.

## Wdrożenie krok po kroku

1. **Konto GitHub.** Załóż darmowe konto i nowe repozytorium, np. `fundusz-index-strona`. Wgraj do niego cały ten folder (Claude Code na komputerze może to zrobić za Ciebie).
2. **Automatyczna aktualizacja.** Po wgraniu w zakładce *Actions* włącz workflow „Aktualizacja danych portfela” i uruchom go raz ręcznie (*Run workflow*). Od tego momentu działa sam w dni robocze o 22:30 UTC.
3. **Hosting.** Wybierz jedną drogę:
   - **Cloudflare Pages (najprościej):** załóż konto, *Workers & Pages → Create → Pages → Connect to Git*, wskaż repozytorium. Polecenie budowania: `python3 scripts/sprawdz_dane.py`, katalog wyjściowy `/`. Jeśli pliki mają błąd, Cloudflare nie opublikuje zmiany i zostawi poprzednią wersję. Każda zmiana w repozytorium sama trafi na stronę. Potem *Custom domains → fundusz.knrkindex.pl*.
   - **Zenbox:** w panelu dodaj subdomenę `fundusz.knrkindex.pl`. Potem skopiuj `wdrozenie/zenbox-ftp.yml.przyklad` do `.github/workflows/` i dodaj dane FTP jako sekrety w GitHubie (instrukcja w pliku).
4. **DNS.** Przy Cloudflare Pages: w panelu Zenbox (strefa DNS domeny knrkindex.pl) dodaj rekord `CNAME`: `fundusz` → adres `*.pages.dev`, który pokaże Cloudflare. Przy Zenbox subdomena działa od razu po dodaniu w panelu.
5. **Certyfikat SSL.** Cloudflare włącza go sam. W Zenbox włącz Let's Encrypt dla subdomeny w panelu.

## Przed publikacją

- Uzupełnij pola w nawiasach kwadratowych.
- Adres e-mail funduszu (do dodania w `o-funduszu.html`, sekcja Kontakt). Adres zarządu koła zostaje na stronie koła.
- Zgody na zdjęcia i nazwiska członków.
- Treść zastrzeżenia prawnego i ujawnień przy analizach do potwierdzenia przy ustaleniach o statucie.
- Oceny i ceny docelowe są celowo wyłączone do czasu tych ustaleń.
