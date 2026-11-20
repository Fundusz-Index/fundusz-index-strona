# Strona Funduszu Index: instrukcje dla Claude

Ten plik czyta każdy czat, który pracuje nad stroną. Aktualizuj go, gdy zmieni się coś z poniższych zasad.

## Czym jest strona

- Strona Funduszu Index, edukacyjnego projektu Koła Naukowego Rynku Kapitałowego INDEX (KNRK INDEX) na UEK, prowadzonego przez Fundację Index (KRS 0001137760).
- Adres docelowy: **fundusz.knrkindex.pl**. Strona koła (knrkindex.pl, WordPress z Elementorem) to osobna sprawa, tu jej nie ruszamy.
- Portfel jest **wirtualny** (zawsze piszemy „portfel wirtualny”, nigdy „modelowy”; decyzja Szymona z 16.11.2026): 100 000 zł umownego kapitału od 13.01.2026, porównanie z S&P 500 w złotych.
- Zakupy mają daty pierwszych analiz spółek: EMCOR 13.01.2026, Alphabet 15.01.2026, Williams 24.02.2026, Chevron 02.06.2026 (decyzja Szymona z 17.11.2026). AMD nie ma w portfelu, analiza zostaje w bibliotece jako „poza portfelem”. Stronę z portfelem uruchomiono w listopadzie 2026, więc wyniki za wcześniejsze miesiące są policzone wstecz. **Strona musi to mówić wprost** (notka pod podsumowaniem w `portfel.html` i akapit w nocie prawnej). Nie dobieramy dat zakupu pod wynik.
- Wolna gotówka jest liczona według kursu ETF-u IB01 (iShares $ Treasury Bond 0-1yr UCITS ETF, USD, akumulujący). Ustawienie: pole `gotowka` w `data/ustawienia.json`.
- Opiekun techniczny po stronie zarządu: Szymon Jakubowski. Strona w zarządzie: Mikołaj Bujacz i Paweł Osiński.

## Źródła zasad

- `PRODUCT.md`: dla kogo i po co jest strona, ograniczenia, zobowiązania marki (format Impeccable, nagłówki po angielsku, nie zmieniaj ich nazw).
- `DESIGN.md`: kolory, typografia, układ, komponenty, wykresy, ruch. Przy zmianie wyglądu najpierw sprawdź ten plik, a po zmianie go zaktualizuj.
- W sporze narzędzi wygrywa Impeccable i `DESIGN.md`. Taste to tylko druga opinia.
- Humanizer stosujemy do artykułów przed publikacją, nie do tekstów strony. Jego uwagi to sugestie, ostatnie słowo ma autor. Nie rusza liczb, nazw spółek, wycen, cytatów ani dokumentów prawnych.

## Technika

- Statyczne HTML, CSS i JavaScript, bez bibliotek, bez frameworków, bez bazy danych. Nie dodawaj zależności bez wyraźnej prośby.
- Dane w `data/` (JSON i CSV), wczytywane przez JS w przeglądarce. `data/portfolio.json` generuje skrypt, nie edytuj go ręcznie.
- `scripts/aktualizuj_dane.py`: kursy z Yahoo Finance, potem Nasdaq, potem Stooq (przez `curl_cffi`), USD/PLN z NBP. Liczy `data/portfolio.json`. Kursy pobiera też dla ETF-u gotówki i dla spółek z `spolki.json`, których nie ma w portfelu (pole `obserwowane`, potrzebne stronom analiz). W tym środowisku serwisy z kursami są zablokowane: prawdziwe dane liczy tylko GitHub Actions (`gh workflow run aktualizacja-danych.yml --ref <gałąź>`).
- `scripts/sprawdz_dane.py`: walidacja danych i linków. `--publikacja` zamienia ostrzeżenia (pola w `[nawiasach]`) w błędy.
- GitHub Actions: `aktualizacja-danych.yml` w dni robocze o 22:30 UTC (testy, walidacja, pobranie kursów, commit „Dane portfela: …” jako „Fundusz Index (automat)”); `sprawdzenie-danych.yml` przy każdym pushu.
- Style: `assets/css/style.css`, tokeny kolorów w `:root`, tryb jasny i ciemny. Kolory i logo z identyfikacji v1 (czerń, biel, żółty akcent #FFD60A, granaty serii #14213D…#D5DEEC). Logo i symbol w `assets/img/ikony.svg`.
- Ruch (blok na końcu `style.css`): wejście nagłówka strony głównej raz przy wczytaniu, podkreślenie w menu, przyciski i karty po najechaniu. Tylko `transform`/`opacity`, tylko w `prefers-reduced-motion: no-preference`, najechanie tylko w `(hover: hover) and (pointer: fine)`. Bez animacji sekcji przy przewijaniu.
- Telefon (do 640 px): menu w jednym wierszu, symbol X w nagłówku ukryty, wykres portfela rysowany w proporcjach 440×300 (`WASKI` w `portfel.js`). Cele dotykowe min. 24 px, tekst min. 12 px.
- Czerń marki na stałe (niezależnie od trybu): `var(--black)`, akcent: `var(--accent)`. Nie wpisuj tych kolorów ręcznie. Wyróżnione bloki idą za motywem (jasnoszare w jasnym, czarne w ciemnym): pasy (hero, pasek kursów, stopka) mają tokeny `--band-*`, panele i nagłówki tabel `--inv-*`.
- Wersja angielska: katalog `en/` (Start, Portfel, Analizy, Artykuły, O funduszu). **Nie edytuj plików w `en/` ani `assets/js/en.js` ręcznie**: buduje je `python3 scripts/zbuduj_en.py` z polskich stron i słownika `i18n/en.json` (polski tekst → angielski). Skrypty biorą tłumaczenia przez `FI.t('polski tekst')`; liczby i daty zmieniają format według `FI.lang`. Linki do stron: `FI.pages`, do danych, analiz i plików: `FI.base`. Strony analiz, dokumenty prawne i PDF-y są na razie tylko po polsku (w wersji angielskiej z dopiskiem „in Polish”). Bez zapamiętywania języka ani motywu w przeglądarce (polityka prywatności mówi, że niczego nie zapisujemy; decyzja z 19.11.2026).
- Każda strona ma w nagłówku przełącznik `<a class="lang-switch">` (EN na polskich, PL na angielskich) i przed nim przycisk motywu. Przycisk dokłada `assets/js/motyw.js` (w `<head>` zaraz po `style.css`, z `defer`); nowa strona też musi go mieć. Domyślnie ustawienie systemu, wybór działa tylko na bieżącej stronie, bez zapisu.
- Każda strona ma `<body data-base="">` (w `analizy/*.html`: `data-base="../"`), link „Przejdź do treści” (`.skip-link` → `<main id="tresc">`), wspólny nagłówek, menu (Start, Portfel, Analizy, Artykuły, O funduszu) i stopkę z linkami do dokumentów prawnych.

## Mapa plików

| Plik | Co jest w środku |
| --- | --- |
| `index.html` | Start: pasek kursów spółek (jako dół nagłówka, w tym samym kolorze pasa; nie zatrzymuje się po najechaniu kursorem), ogłoszenie (`data/ogloszenie.json`), portfel w skrócie, ostatnia decyzja, statystyki koła, najnowsze analizy, kalendarz (`data/kalendarz.json`, cztery najbliższe, minione znikają same), dla partnerów |
| `portfel.html` + `assets/js/portfel.js` | Wykres funduszu vs S&P 500 z zakresami, skład, „W liczbach”, spółki z tezami, dziennik decyzji z tezą przy każdym zakupie. Tezy pochodzą z raportów z dnia zakupu i mają podpis „Teza w dniu zakupu” (`TEZA_PODPIS` w `portfel.js`). Wykres w stylu księgi znaku (wzór: `04_Wykresy/Wykres_raport_kurs_52_tygodnie`): gruba granatowa linia funduszu z kropką i podpisem na końcu, ciągła jaśniejsza linia S&P 500, bez legendy i bez wypełnienia. Żółty romb na linii funduszu = dzień transakcji z `transakcje.csv` (jedyny żółty element wykresu). Dymek `#wykres-dymek`: data, oba wyniki, różnica w pp, decyzja; na telefonie stała ramka pod wykresem. Gdy kursor jest na wykresie, pasek „Skład” pokazuje skład z tego dnia (wagi `w` przy każdym punkcie `seria` w `portfolio.json`) i datę przy nagłówku; spółki mają stałe kolory, gotówka zawsze `--s5` |
| `analizy.html` + `assets/js/analizy.js` | Biblioteka analiz z filtrami (sektor, w portfelu / poza) z `data/analizy.json` |
| `analizy/wmb.html`, `googl.html`, `cvx.html`, `eme.html`, `amd.html` | Strony analiz (kopia jednego szablonu); raporty PDF w `pliki/analizy/fundusz-index-<ticker>-RRRR-MM.pdf`. Blok `.quote[data-kurs]` pokazuje aktualny kurs z `portfolio.json` (kod w `wspolne.js`). Wykres wyceny pokazuje tylko kurs z dnia raportu |
| `zrodla/ujawnienia/` | Ostatnia strona raportów PDF „Ujawnienia i zastrzeżenia”, w stylu danego raportu (jasny albo szary jak WMB). Treść ujawnień bierze z sekcji `#ujawnienia` na stronie analizy, styl, podpis i ocenę z `raporty.json` (ocena tylko tam, gdzie raport ją podaje; dziś tylko WMB, i wtedy też skala ocen z podręcznika). Buduje `python3 zrodla/ujawnienia/zbuduj.py` (Playwright, pypdf, qpdf jeśli jest). Uruchom po każdej zmianie ujawnień i po podmianie PDF-a; skrypt podmienia swoją stronę, nie dokłada drugiej. Oryginały autorów: folder „Analizy na stronę” u Szymona |
| `data/kalendarz.json` | Wydarzenia na stronie głównej: data, do, typ, tytul, opis, szacunek (termin niepotwierdzony przez spółkę), link. Sprawdza go `sprawdz_dane.py`. Tylko spółki z portfela (bez AMD, decyzja Szymona z 20.11.2026) |
| `artykuly.html` + `assets/js/artykuly.js` | Działy: Przegląd tygodnia, Profit Journal, Edukacja, Z życia funduszu; newsletter |
| `o-funduszu.html` | Opis, filary „Dlaczego powstał fundusz”, proces decyzji, zarząd, analitycy, kontakt |
| `polityka-prywatnosci.html`, `nota-prawna.html`, `regulamin-newslettera.html` + `assets/js/dokumenty.js` | Dokumenty prawne (spis treści z podświetleniem) |
| `pliki/fundusz-index-oferta-wspolpracy.pdf` + `zrodla/oferta/` | Oferta dla partnerów (4 strony A4). Treść w `zrodla/oferta/oferta.html`, PDF buduje `python3 zrodla/oferta/zbuduj.py` (Playwright). Liczby: 26 członków funduszu, 13 analityków, 185 członków koła. Nie wymieniamy Wall Street Prep ani partnerów koła bez zgody |
| `assets/img/og/*.png` + `zrodla/og/` | Obrazki podglądu linków (1200×630): `fundusz-index.png` dla stron ogólnych, `analiza-<ticker>.png` dla analiz. Buduje `python3 zrodla/og/zbuduj.py` (Playwright) z `data/analizy.json`; uruchom po dodaniu analizy. Każda strona ma w `<head>` blok `og:*` z adresami bezwzględnymi `https://fundusz.knrkindex.pl/…`. Nowa strona musi go dostać. Hasło na obrazku to slogan z LinkedIna |
| `404.html` + `.htaccess` | Strona „Nie ma takiej strony” z linkami do zakładek. Ma `<base href="/">` i `noindex`, bo serwer pokazuje ją pod dowolnym adresem; w podglądzie GitHub Pages (podkatalog) jest bez stylów, na docelowej domenie działa. `.htaccess` ustawia ją dla Apache (Zenbox) |
| `robots.txt`, `sitemap.xml` + `scripts/zbuduj_sitemap.py` | Mapa strony dla wyszukiwarek (polskie strony, analizy, angielskie, z parami hreflang). Buduje ją też `zbuduj_en.py`; `tests/test_sitemap.py` pilnuje, żeby była aktualna |
| `en/*.html`, `assets/js/en.js` | Wersja angielska, generowana. Źródło: polskie strony + `i18n/en.json` |
| `i18n/en.json` | Słownik: `teksty` (polski → angielski, klucz to dokładny tekst ze strony, skryptu albo danych) i `bez_zmian` (nazwiska, tickery, nazwy własne). Angielski brytyjski, bez długich myślników. Nazwa po angielsku: „Index Fund”, portfel: „virtual portfolio” |
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
2. Po zmianie tekstu na stronie, w skryptach albo w danych (`spolki.json`, `analizy.json`, `kalendarz.json`, `ogloszenie.json`, uzasadnienia w `transakcje.csv`): dopisz tłumaczenie do `i18n/en.json` i uruchom `python3 scripts/zbuduj_en.py` (lista braków: `--braki`). Testy `tests/test_en.py` nie przejdą, gdy strona angielska jest nieaktualna albo brakuje tłumaczenia tekstu ze strony. Brak tłumaczenia tekstu z danych to ostrzeżenie w `sprawdz_dane.py` (na stronie angielskiej zostaje wtedy polski tekst).
3. Po zmianie w `assets/css` lub `assets/js`: `python3 scripts/wersje.py` (robi to też `zbuduj_en.py`). Skrypt dopisuje do odwołań w HTML znacznik `?v=<skrót pliku>`, żeby przeglądarki nie pokazywały starych stylów z pamięci podręcznej. Test `tests/test_wersje.py` nie przejdzie, jeśli o tym zapomnisz.
4. Potem: `python3 -m unittest discover tests` i `python3 scripts/sprawdz_dane.py`. Oba muszą przejść.
5. Commit jako `Claude <noreply@anthropic.com>` (ustaw `git config user.name/user.email`), opis po polsku, krótko, co i gdzie. Push na `main`, chyba że Szymon poprosi o gałąź i pull request.
6. Pokaż zmianę: zrzut ekranu (Playwright, szerokość 1280 i 390) albo odśwież podgląd. Podgląd dla zarządu to artefakt https://claude.ai/artifact/Hviuj95cNrNmjTeJo8jCsW: kopia plików strony, w której `index.html` jest bez `<head>`/`<body>` i z meta `claude:viewport-fit-sides`. Nie wrzucaj tej meta do plików w repozytorium.
7. Większe zmiany wyglądu: najpierw krótka propozycja, potem wdrożenie.

## Otwarte sprawy

- **Hosting**: Zenbox przez FTP (`wdrozenie/zenbox-ftp.yml.przyklad`, sekrety FTP_SERWER, FTP_LOGIN, FTP_HASLO) albo Cloudflare Pages (budowanie: `python3 scripts/sprawdz_dane.py`, katalog `/`, CNAME `fundusz` w DNS Zenbox). Decyzja czeka na wgląd w panel Zenbox. Hasła wpisuje Szymon w sekretach GitHuba, nigdy w czacie ani w plikach.
- **Do uzupełnienia** (lista: `python3 scripts/sprawdz_dane.py --publikacja`): daty i godziny publikacji analiz. Analizy nie były wcześniej udostępniane na zewnątrz, więc „Pierwsza publikacja” to dzień i godzina startu strony (decyzja Szymona z 20.11.2026). Wpisać w dniu startu, nie wcześniej. Po wpisaniu uruchom `python3 zrodla/ujawnienia/zbuduj.py`, żeby data trafiła też do PDF-ów. Daty poprzednich analiz są wpisane (20.11.2026). Na bieżąco prowadzimy je w dokumencie Google „Strona Funduszu Index: pola do uzupełnienia” na Dysku Szymona.
- Zgody na zdjęcia członków. Zgody na imiona i nazwiska zarządu i analityków na stronie są potwierdzone (20.11.2026).
- Analizy z 16.10.2026 to gruntowne aktualizacje wcześniejszych analiz z okresu przyjęcia spółek do portfela. Pierwsza publikacja = start strony. Poprzednie analizy: EMCOR 13.01.2026, Alphabet 15.01.2026, Williams 24.02.2026, Chevron i AMD 02.06.2026.
- Do rozważenia przy ujawnieniach (dla „ekspertów” w rozumieniu rozp. 2016/958): horyzont inwestycyjny, znaczenie oceny (np. co oznacza „TRZYMAJ”), planowana częstotliwość aktualizacji.
- Kalendarz: terminy wyników na początek 2027 r. są szacunkowe (`"szacunek": true`). Zmień na potwierdzone, gdy spółki je ogłoszą. Dodać walne zgromadzenia 2027, gdy spółki podadzą daty. Dodawać spotkania funduszu.
- Newsletter: formularz wyłączony („Zapisy ruszą wkrótce”), czeka na Dysk Google funduszu (Michał). Po podpięciu: włączyć pola w `artykuly.html` i wpisać datę w `regulamin-newslettera.html` („Obowiązuje od”).
- Polityka prywatności: czas przechowywania logów opisany kryterium (zasady hostingu). Po wyborze hostingu wpisać konkretny okres.
- Opiekun naukowy: do ustalenia, może go nie być (blok usunięty z `o-funduszu.html`). Partnerów na razie brak.
- Wersja angielska, etap 2: strony analiz, dokumenty prawne, oferta dla partnerów i raporty PDF po angielsku; obrazek podglądu linku (og) z angielskim hasłem. Do potwierdzenia przez zarząd: angielska nazwa „Index Fund” (w finansach „index fund” to fundusz pasywny).
- Pomysły odłożone: panel do edycji treści (Pages CMS), dywidendy w wynikach, strona jako aplikacja na telefon (PWA).
- Kontekst prawny: dokument „Strona_funduszu_kontekst_prawny.md” w projekcie Fundusz INDEX.
