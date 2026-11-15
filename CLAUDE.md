# Strona Funduszu Index: instrukcje dla Claude

Ten plik czyta każdy czat, który pracuje nad stroną. Aktualizuj go, gdy zmieni się coś z poniższych zasad.

## Czym jest strona

- Strona Funduszu Index, edukacyjnego projektu Koła Naukowego Rynku Kapitałowego INDEX (KNRK INDEX) na UEK, prowadzonego przez Fundację Index (KRS 0001137760).
- Adres docelowy: **fundusz.knrkindex.pl**. Strona koła (knrkindex.pl, WordPress z Elementorem) to osobna sprawa, tu jej nie ruszamy.
- Portfel jest **wirtualny**: 100 000 zł umownego kapitału od 25.10.2026, porównanie z S&P 500 w złotych.
- Opiekun techniczny po stronie zarządu: Szymon Jakubowski. Strona w zarządzie: Mikołaj Bujacz i Paweł Osiński.

## Źródła zasad

- `PRODUCT.md`: dla kogo i po co jest strona, ograniczenia, zobowiązania marki (format Impeccable, nagłówki po angielsku, nie zmieniaj ich nazw).
- `DESIGN.md`: kolory, typografia, układ, komponenty, wykresy, ruch. Przy zmianie wyglądu najpierw sprawdź ten plik, a po zmianie go zaktualizuj.
- W sporze narzędzi wygrywa Impeccable i `DESIGN.md`. Taste to tylko druga opinia.

## Technika

- Statyczne HTML, CSS i JavaScript, bez bibliotek, bez frameworków, bez bazy danych. Nie dodawaj zależności bez wyraźnej prośby.
- Dane w `data/` (JSON i CSV), wczytywane przez JS w przeglądarce. `data/portfolio.json` generuje skrypt, nie edytuj go ręcznie.
- `scripts/aktualizuj_dane.py`: kursy z Yahoo Finance, potem Nasdaq, potem Stooq (przez `curl_cffi`), USD/PLN z NBP. Liczy `data/portfolio.json`.
- `scripts/sprawdz_dane.py`: walidacja danych i linków. `--publikacja` zamienia ostrzeżenia (pola w `[nawiasach]`) w błędy.
- GitHub Actions: `aktualizacja-danych.yml` w dni robocze o 22:30 UTC (testy, walidacja, pobranie kursów, commit „Dane portfela: …” jako „Fundusz Index (automat)”); `sprawdzenie-danych.yml` przy każdym pushu.
- Style: `assets/css/style.css`, tokeny kolorów w `:root`, tryb jasny i ciemny. Kolory i logo z identyfikacji v1 (czerń, biel, żółty akcent #FFD60A, granaty serii #14213D…#D5DEEC). Logo i symbol w `assets/img/ikony.svg`.
- Ruch (blok na końcu `style.css`): wejście nagłówka strony głównej raz przy wczytaniu, podkreślenie w menu, przyciski i karty po najechaniu. Tylko `transform`/`opacity`, tylko w `prefers-reduced-motion: no-preference`, najechanie tylko w `(hover: hover) and (pointer: fine)`. Bez animacji sekcji przy przewijaniu.
- Telefon (do 640 px): menu w jednym wierszu, symbol X w nagłówku ukryty, wykres portfela rysowany w proporcjach 440×300 (`WASKI` w `portfel.js`). Cele dotykowe min. 24 px, tekst min. 12 px.
- Czerń marki na stałe (niezależnie od trybu): `var(--black)`, akcent: `var(--accent)`. Nie wpisuj tych kolorów ręcznie.
- Każda strona ma `<body data-base="">` (w `analizy/*.html`: `data-base="../"`), link „Przejdź do treści” (`.skip-link` → `<main id="tresc">`), wspólny nagłówek, menu (Start, Portfel, Analizy, Artykuły, O funduszu) i stopkę z linkami do dokumentów prawnych.

## Mapa plików

| Plik | Co jest w środku |
| --- | --- |
| `index.html` | Start: pasek kursów spółek (nie zatrzymuje się po najechaniu kursorem), ogłoszenie (`data/ogloszenie.json`), portfel w skrócie, ostatnia decyzja, statystyki koła, najnowsze analizy, kalendarz (`data/kalendarz.json`, cztery najbliższe, minione znikają same), dla partnerów |
| `portfel.html` + `assets/js/portfel.js` | Wykres funduszu vs S&P 500 z zakresami, skład, „W liczbach”, spółki z tezami, dziennik decyzji. Wykres w stylu księgi znaku (wzór: `04_Wykresy/Wykres_raport_kurs_52_tygodnie`): gruba granatowa linia funduszu z kropką i podpisem na końcu, ciągła jaśniejsza linia S&P 500, bez legendy i bez wypełnienia. Żółty romb na linii funduszu = dzień transakcji z `transakcje.csv` (jedyny żółty element wykresu). Dymek `#wykres-dymek`: data, oba wyniki, różnica w pp, decyzja; na telefonie stała ramka pod wykresem |
| `analizy.html` + `assets/js/analizy.js` | Biblioteka analiz z filtrami (sektor, w portfelu / poza) z `data/analizy.json` |
| `analizy/wmb.html`, `googl.html`, `cvx.html`, `eme.html`, `amd.html` | Strony analiz (kopia jednego szablonu); raporty PDF w `pliki/analizy/fundusz-index-<ticker>-RRRR-MM.pdf`. Blok `.quote[data-kurs]` pokazuje aktualny kurs z `portfolio.json` (kod w `wspolne.js`). Wykres wyceny pokazuje tylko kurs z dnia raportu |
| `data/kalendarz.json` | Wydarzenia na stronie głównej: data, do, typ, tytul, opis, szacunek (termin niepotwierdzony przez spółkę), link. Sprawdza go `sprawdz_dane.py` |
| `artykuly.html` + `assets/js/artykuly.js` | Działy: Przegląd tygodnia, Profit Journal, Edukacja, Z życia funduszu; newsletter |
| `o-funduszu.html` | Opis, filary „Dlaczego powstał fundusz”, proces decyzji, zarząd, analitycy, kontakt |
| `polityka-prywatnosci.html`, `nota-prawna.html`, `regulamin-newslettera.html` + `assets/js/dokumenty.js` | Dokumenty prawne (spis treści z podświetleniem) |
| `pliki/fundusz-index-oferta-wspolpracy.pdf` + `zrodla/oferta/` | Oferta dla partnerów (4 strony A4). Treść w `zrodla/oferta/oferta.html`, PDF buduje `python3 zrodla/oferta/zbuduj.py` (Playwright). Liczby: 26 członków funduszu, 13 analityków, ok. 185 członków koła. Nie wymieniamy Wall Street Prep ani partnerów koła bez zgody |
| `data/transakcje.csv` | Każde kupno i sprzedaż: `data,typ,ticker,kwota_pln,liczba_akcji,uzasadnienie` |
| `data/spolki.json` | Opis spółek; nowa spółka w transakcjach musi mieć tu wpis |

## Zasady treści (ustalone, nie zmieniaj bez decyzji zarządu)

- Język polski. Krótkie zdania, naturalny, ciepły, profesjonalny ton. **Bez długich myślników (—)**. Bez słów-wypełniaczy.
- **Na stronach HTML bez ocen typu „kupuj”, „trzymaj”, bez cen docelowych i upside.** Pokazujemy przedziały wycen i metodę. Raporty PDF publikujemy w wersji autorów, z ocenami (decyzja Szymona z 15.11.2026). Warunek: pełne ujawnienia przy każdej analizie, zwłaszcza data i godzina pierwszej publikacji (MAR art. 20, rozp. 2016/958).
- **Autorzy zawsze podani** przy analizach i artykułach. Każda analiza ma sekcję ujawnień (autorzy, data, czy fundusz i autorzy mają akcje).
- Zastrzeżenie: projekt edukacyjny, nie fundusz inwestycyjny w rozumieniu ustawy z 27.05.2004, portfel wirtualny, analizy to nie porada inwestycyjna.
- Układ nie może przypominać strony Hossa ProCapital.
- Nie dodawaj sekcji rekrutacji („Dołącz”): rekrutacja zamknięta. Bez rolki z przeglądem tygodnia.
- Ze starego opisu funduszu bierzemy tylko liczby: 25+ lat, 300+ prezentacji, 60+ opracowań. Sponsor Willway i dawny koordynator są nieaktualni, nie wspominaj o nich.
- Zdjęcia i nazwiska członków tylko za zgodą. Pola w `[nawiasach]` to miejsca do uzupełnienia; nie wolno ich zostawić na stronie publicznej.
- Linki do plików oznaczamy samym „(PDF)”, bez rozmiaru pliku.
- Kontakt funduszu: funduszindex@knrkindex.pl. LinkedIn: linkedin.com/company/index-fund.

## Jak pracować

1. Przed zmianą: `git fetch origin main` i pracuj na aktualnym `main`.
2. Po zmianie: `python3 -m unittest discover tests` i `python3 scripts/sprawdz_dane.py`. Oba muszą przejść.
3. Commit jako `Claude <noreply@anthropic.com>` (ustaw `git config user.name/user.email`), opis po polsku, krótko, co i gdzie. Push na `main`, chyba że Szymon poprosi o gałąź i pull request.
4. Pokaż zmianę: zrzut ekranu (Playwright, szerokość 1280 i 390) albo odśwież podgląd. Podgląd dla zarządu to artefakt https://claude.ai/artifact/Hviuj95cNrNmjTeJo8jCsW: kopia plików strony, w której `index.html` jest bez `<head>`/`<body>` i z meta `claude:viewport-fit-sides`. Nie wrzucaj tej meta do plików w repozytorium.
5. Większe zmiany wyglądu: najpierw krótka propozycja, potem wdrożenie.

## Otwarte sprawy

- **Hosting**: Zenbox przez FTP (`wdrozenie/zenbox-ftp.yml.przyklad`, sekrety FTP_SERWER, FTP_LOGIN, FTP_HASLO) albo Cloudflare Pages (budowanie: `python3 scripts/sprawdz_dane.py`, katalog `/`, CNAME `fundusz` w DNS Zenbox). Decyzja czeka na wgląd w panel Zenbox. Hasła wpisuje Szymon w sekretach GitHuba, nigdy w czacie ani w plikach.
- **Do uzupełnienia** (lista: `python3 scripts/sprawdz_dane.py --publikacja`): daty publikacji analiz i daty wcześniejszych analiz. Na bieżąco prowadzimy je w dokumencie Google „Strona Funduszu Index: pola do uzupełnienia” na Dysku Szymona.
- Zgody na zdjęcia członków.
- Analizy z 16.10.2026 to gruntowne aktualizacje wcześniejszych analiz z okresu przyjęcia spółek do portfela. Daty publikacji czekają na model ryzyka (Mikołaj), daty wcześniejszych analiz trzeba dopasować do historii portfela.
- Do rozważenia przy ujawnieniach (dla „ekspertów” w rozumieniu rozp. 2016/958): horyzont inwestycyjny, znaczenie oceny (np. co oznacza „TRZYMAJ”), planowana częstotliwość aktualizacji.
- Kalendarz: terminy wyników na początek 2027 r. są szacunkowe (`"szacunek": true`). Zmień na potwierdzone, gdy spółki je ogłoszą. Dodać walne zgromadzenia 2027, gdy spółki podadzą daty. Dodawać spotkania funduszu.
- Newsletter: formularz wyłączony („Zapisy ruszą wkrótce”), czeka na Dysk Google funduszu (Michał). Po podpięciu: włączyć pola w `artykuly.html` i wpisać datę w `regulamin-newslettera.html` („Obowiązuje od”).
- Polityka prywatności: czas przechowywania logów opisany kryterium (zasady hostingu). Po wyborze hostingu wpisać konkretny okres.
- Opiekun naukowy: do ustalenia, może go nie być (blok usunięty z `o-funduszu.html`). Partnerów na razie brak.
- Pomysły odłożone: panel do edycji treści (Pages CMS), dywidendy w wynikach, strona jako aplikacja na telefon (PWA).
- Kontekst prawny: dokument „Strona_funduszu_kontekst_prawny.md” w projekcie Fundusz INDEX.
