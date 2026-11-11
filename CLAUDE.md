# Strona Funduszu Index: instrukcje dla Claude

Ten plik czyta każdy czat, który pracuje nad stroną. Aktualizuj go, gdy zmieni się coś z poniższych zasad.

## Czym jest strona

- Strona Funduszu Index, edukacyjnego projektu Koła Naukowego Rynku Kapitałowego INDEX (KNRK INDEX) na UEK, prowadzonego przez Fundację Index (KRS 0001137760).
- Adres docelowy: **fundusz.knrkindex.pl**. Strona koła (knrkindex.pl, WordPress z Elementorem) to osobna sprawa, tu jej nie ruszamy.
- Portfel jest **wirtualny**: 100 000 zł umownego kapitału od 25.10.2026, porównanie z S&P 500 w złotych.
- Opiekun techniczny po stronie zarządu: Szymon Jakubowski. Strona w zarządzie: Mikołaj Bujacz i Paweł Osiński.

## Technika

- Statyczne HTML, CSS i JavaScript, bez bibliotek, bez frameworków, bez bazy danych. Nie dodawaj zależności bez wyraźnej prośby.
- Dane w `data/` (JSON i CSV), wczytywane przez JS w przeglądarce. `data/portfolio.json` generuje skrypt, nie edytuj go ręcznie.
- `scripts/aktualizuj_dane.py`: kursy z Yahoo Finance, potem Nasdaq, potem Stooq (przez `curl_cffi`), USD/PLN z NBP. Liczy `data/portfolio.json`.
- `scripts/sprawdz_dane.py`: walidacja danych i linków. `--publikacja` zamienia ostrzeżenia (pola w `[nawiasach]`) w błędy.
- GitHub Actions: `aktualizacja-danych.yml` w dni robocze o 22:30 UTC (testy, walidacja, pobranie kursów, commit „Dane portfela: …” jako „Fundusz Index (automat)”); `sprawdzenie-danych.yml` przy każdym pushu.
- Style: `assets/css/style.css`, tokeny kolorów w `:root`, tryb jasny i ciemny. Kolory i logo z identyfikacji v1 (czerń, biel, żółty akcent #FFD60A, granaty serii #14213D…#D5DEEC). Logo i symbol w `assets/img/ikony.svg`.
- Każda strona ma `<body data-base="">` (w `analizy/*.html`: `data-base="../"`), wspólny nagłówek, menu (Start, Portfel, Analizy, Artykuły, O funduszu) i stopkę z linkami do dokumentów prawnych.

## Mapa plików

| Plik | Co jest w środku |
| --- | --- |
| `index.html` | Start: pasek kursów spółek, ogłoszenie (`data/ogloszenie.json`), portfel w skrócie, ostatnia decyzja, statystyki koła, najnowsze analizy, kalendarz, dla partnerów |
| `portfel.html` + `assets/js/portfel.js` | Wykres funduszu vs S&P 500 z zakresami, skład, „W liczbach”, spółki z tezami, dziennik decyzji |
| `analizy.html` + `assets/js/analizy.js` | Biblioteka analiz z filtrami (sektor, w portfelu / poza) z `data/analizy.json` |
| `analizy/wmb.html`, `googl.html`, `cvx.html` | Strony analiz; raporty PDF w `pliki/analizy/` |
| `artykuly.html` + `assets/js/artykuly.js` | Działy: Przegląd tygodnia, Profit Journal, Edukacja, Z życia funduszu; newsletter |
| `o-funduszu.html` | Opis, filary „Dlaczego powstał fundusz”, proces decyzji, zarząd, analitycy, kontakt |
| `polityka-prywatnosci.html`, `nota-prawna.html`, `regulamin-newslettera.html` + `assets/js/dokumenty.js` | Dokumenty prawne (spis treści z podświetleniem) |
| `data/transakcje.csv` | Każde kupno i sprzedaż: `data,typ,ticker,kwota_pln,liczba_akcji,uzasadnienie` |
| `data/spolki.json` | Opis spółek; nowa spółka w transakcjach musi mieć tu wpis |

## Zasady treści (ustalone, nie zmieniaj bez decyzji zarządu)

- Język polski. Krótkie zdania, naturalny, ciepły, profesjonalny ton. **Bez długich myślników (—)**. Bez słów-wypełniaczy.
- **Bez ocen typu „kupuj”, „trzymaj”, bez cen docelowych i upside.** Do czasu ustaleń prawnych. Pokazujemy przedziały wycen i metodę.
- **Autorzy zawsze podani** przy analizach i artykułach. Każda analiza ma sekcję ujawnień (autorzy, data, czy fundusz i autorzy mają akcje).
- Zastrzeżenie: projekt edukacyjny, nie fundusz inwestycyjny w rozumieniu ustawy z 27.05.2004, portfel wirtualny, analizy to nie porada inwestycyjna.
- Układ nie może przypominać strony Hossa ProCapital.
- Nie dodawaj sekcji rekrutacji („Dołącz”): rekrutacja zamknięta. Bez rolki z przeglądem tygodnia.
- Ze starego opisu funduszu bierzemy tylko liczby: 25+ lat, 300+ prezentacji, 60+ opracowań. Sponsor Willway i dawny koordynator są nieaktualni, nie wspominaj o nich.
- Zdjęcia i nazwiska członków tylko za zgodą. Pola w `[nawiasach]` to miejsca do uzupełnienia; nie wolno ich zostawić na stronie publicznej.
- Kontakt funduszu: funduszindex@knrkindex.pl. LinkedIn: linkedin.com/company/index-fund.

## Jak pracować

1. Przed zmianą: `git fetch origin main` i pracuj na aktualnym `main`.
2. Po zmianie: `python3 -m unittest discover tests` i `python3 scripts/sprawdz_dane.py`. Oba muszą przejść.
3. Commit jako `Claude <noreply@anthropic.com>` (ustaw `git config user.name/user.email`), opis po polsku, krótko, co i gdzie. Push na `main`, chyba że Szymon poprosi o gałąź i pull request.
4. Pokaż zmianę: zrzut ekranu (Playwright, szerokość 1280 i 390) albo odśwież podgląd. Podgląd dla zarządu to artefakt https://claude.ai/artifact/Hviuj95cNrNmjTeJo8jCsW: kopia plików strony, w której `index.html` jest bez `<head>`/`<body>` i z meta `claude:viewport-fit-sides`. Nie wrzucaj tej meta do plików w repozytorium.
5. Większe zmiany wyglądu: najpierw krótka propozycja, potem wdrożenie.

## Otwarte sprawy

- **Hosting**: Zenbox przez FTP (`wdrozenie/zenbox-ftp.yml.przyklad`, sekrety FTP_SERWER, FTP_LOGIN, FTP_HASLO) albo Cloudflare Pages (budowanie: `python3 scripts/sprawdz_dane.py`, katalog `/`, CNAME `fundusz` w DNS Zenbox). Decyzja czeka na wgląd w panel Zenbox. Hasła wpisuje Szymon w sekretach GitHuba, nigdy w czacie ani w plikach.
- **Do uzupełnienia** (lista: `python3 scripts/sprawdz_dane.py --publikacja`): daty publikacji analiz, opis współpracy z Profit Journal, newsletter (formularz do arkusza Google), kalendarz na stronie głównej, opiekun naukowy, partnerzy, zasada głosowania, nazwisko Filipa, lista analityków z sektorami, termin w polityce prywatności, data uruchomienia newslettera.
- Zgody na zdjęcia członków.
- Pomysły odłożone: panel do edycji treści (Pages CMS), dywidendy w wynikach, strona jako aplikacja na telefon (PWA).
- Kontekst prawny: dokument „Strona_funduszu_kontekst_prawny.md” w projekcie Fundusz INDEX.
