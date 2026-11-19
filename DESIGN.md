---
name: Fundusz Index
description: Strona edukacyjnego funduszu studenckiego. Czerń, biel, granat i jeden żółty akcent.
colors:
  black: "#0D0D0D"
  white: "#FFFFFF"
  accent: "#FFD60A"
  ink: "#0D0D0D"
  ink-2: "#3A3A3A"
  muted: "#666666"
  surface: "#F3F3F3"
  line: "#E6E6E6"
  line-strong: "#BDBDBD"
  series-1: "#14213D"
  series-2: "#3463A6"
  series-3: "#6F8CBB"
  series-4: "#A9BCDB"
  series-5: "#D5DEEC"
  loss: "#B3261E"
  dark-bg: "#101113"
  dark-surface: "#1A1B1E"
  dark-ink: "#F2F2F2"
  dark-series-1: "#9DBBF0"
typography:
  display:
    fontFamily: "Arial, Helvetica Neue, Helvetica, sans-serif"
    fontSize: "clamp(36px, 6vw, 54px)"
    fontWeight: 700
    lineHeight: 1.04
  headline:
    fontFamily: "Arial, Helvetica Neue, Helvetica, sans-serif"
    fontSize: "28px"
    fontWeight: 700
    lineHeight: 1.15
  title:
    fontFamily: "Arial, Helvetica Neue, Helvetica, sans-serif"
    fontSize: "20px"
    fontWeight: 700
    lineHeight: 1.15
  body:
    fontFamily: "Arial, Helvetica Neue, Helvetica, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.5
  lead:
    fontFamily: "Arial, Helvetica Neue, Helvetica, sans-serif"
    fontSize: "18px"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "Arial, Helvetica Neue, Helvetica, sans-serif"
    fontSize: "12px"
    fontWeight: 700
    letterSpacing: "0.07em"
rounded:
  sm: "6px"
  md: "8px"
  pill: "22px"
spacing:
  xs: "8px"
  sm: "16px"
  md: "24px"
  lg: "32px"
  xl: "48px"
  xxl: "64px"
components:
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.white}"
    rounded: "{rounded.sm}"
    height: "44px"
    padding: "0 20px"
  button-light:
    backgroundColor: "{colors.white}"
    textColor: "{colors.black}"
    rounded: "{rounded.sm}"
    height: "44px"
  card:
    backgroundColor: "{colors.white}"
    rounded: "{rounded.md}"
    padding: "20px"
  panel:
    backgroundColor: "{colors.black}"
    textColor: "{colors.white}"
    rounded: "{rounded.md}"
    padding: "24px"
  chip:
    backgroundColor: "{colors.white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    height: "44px"
---

# Design System: Fundusz Index

## Overview

**Creative North Star: „Studencki fundusz na wzór uczelni amerykańskich”**

Fundusz Index robi to, co fundusze zarządzane przez studentów na uczelniach w USA: prowadzi portfel, pisze analizy i pokazuje wyniki. W naszej części Europy takich projektów jest niewiele. Strona ma więc wyglądać jak strona poważnego funduszu studenckiego: rzeczowa jak raport analityczny, ale wyraźnie uczelniana i ludzka. Nie jak reklama produktu finansowego i nie jak strona koła naukowego z ogłoszeniami. Dużo bieli, czarny tekst, granatowe dane i jeden żółty znak tam, gdzie czytelnik ma spojrzeć najpierw. Źródłem jest identyfikacja v1 funduszu (logo, paleta, wykresy, księga znaku). Strona ją stosuje, nie interpretuje na nowo.

Gęstość jest umiarkowana. Liczby stoją blisko opisów, sekcje oddziela światło, a nie ozdobniki. Czarne bloki (nagłówek strony głównej, panel „W liczbach”, stopka) dają rytm i niosą najważniejsze liczby.

Układ nie może przypominać strony funduszu Hossa ProCapital.

**Key Characteristics:**
- Czerń i biel jako baza, granat tylko dla danych.
- Jeden żółty element w polu widzenia.
- Jeden krój pisma, hierarchia przez rozmiar i grubość.
- Płasko: ramki i kontrast zamiast cieni.
- Liczby tabelaryczne, zawsze ze znakiem i jednostką.

## Colors

Paleta jest prawie achromatyczna. Kolor pojawia się tylko tam, gdzie niesie informację.

### Primary
- **Czerń marki** (black): tekst, przyciski główne, czarne bloki. W blokach zostaje czarna także w trybie ciemnym.
- **Biel** (white): tło strony i tekst na czerni.

### Secondary
- **Żółty akcent** (accent): jedno wyróżnienie. Kwadrat w symbolu, romb kursu na wykresie wyceny, romb decyzji na wykresie portfela, znacznik przy etykiecie.

### Tertiary
- **Granaty serii** (series-1 do series-5): dane na wykresach i paskach, od najciemniejszego dla najważniejszej serii. Fundusz to zawsze series-1. Benchmark to series-3.
- **Czerwień straty** (loss): tylko wartości ujemne wyniku.

### Neutral
- **Tekst drugiego planu** (ink-2) i **wyciszony** (muted): opisy, podpisy osi, metadane.
- **Powierzchnia** (surface): tła bloków pomocniczych.
- **Linie** (line, line-strong): ramki kart, siatka wykresu, linia bazowa.
- **Tryb ciemny** (dark-bg, dark-surface, dark-ink, dark-series-1): te same role, odwrócona jasność. Granaty serii jaśnieją.

### Named Rules
**Zasada jednego żółtego.** W jednym widoku żółty wskazuje jedną rzecz. Nigdy nie jest kolorem tekstu ani cienkiej linii na białym tle.

**Zasada czerwieni.** Czerwony oznacza wyłącznie stratę. Nie błąd, nie ostrzeżenie, nie ozdobę.

**Zasada kształtu prognozy.** Prognozę i wartość szacunkową odróżnia forma (linia lub ramka przerywana), nie kolor. Dane historyczne są zawsze linią ciągłą.

## Typography

**Display Font:** Arial (zapas: Helvetica Neue, Helvetica, sans-serif)
**Body Font:** Arial

**Character:** Jeden krój systemowy z identyfikacji. Rzeczowy, bez charakteru własnego, więc głos mają liczby i treść. Strona nie wczytuje żadnych czcionek.

### Hierarchy
- **Display** (700, clamp 36–54 px, 1,04): nagłówek strony głównej, dwa krótkie zdania.
- **Headline** (700, 28 px, 1,15): tytuły sekcji i tytuł strony.
- **Title** (700, 20 px, 1,15): tytuły kart i bloków.
- **Lead** (400, 18 px, 1,55): wstęp pod tytułem, maks. 720 px szerokości.
- **Body** (400, 16 px, 1,5): tekst. Pomocniczy 14 px, drobny 13 px.
- **Label** (700, 12 px, odstęp 0,07em, wersaliki): krótkie etykiety nad blokami danych.

### Named Rules
**Zasada dwunastu.** Żaden tekst nie jest mniejszy niż 12 px, także na wykresach.

**Zasada liczb.** Liczby mają cyfry tabelaryczne, polski zapis (przecinek, spacja tysięcy), znak plus lub minus i jednostkę.

## Layout

Kontener do 1200 px, marginesy boczne 16 px. Treść strony układa się w kolumnie z odstępem 48 px między sekcjami. Karty stoją w siatce, która sama zmienia liczbę kolumn. Od 960 px Portfel ma układ dwóch kolumn: wykres i czarny panel z liczbami.

Do 640 px: logo i przycisk „Kontakt” w jednej linii, menu w jednym wierszu z przewijaniem w bok, symbol X w nagłówku ukryty, wykres portfela w proporcjach 440×300, dymek wykresu jako stała ramka pod wykresem. Cele dotykowe mają co najmniej 24 px, przyciski 44 px.

## Elevation & Depth

System jest płaski. Głębię dają ramka 1 px, tło powierzchni i kontrast czarnych bloków. Cień pojawia się tylko jako odpowiedź na działanie.

### Shadow Vocabulary
- **Karta po najechaniu** (`0 10px 24px rgba(13, 13, 13, 0.08)`): razem z uniesieniem o 2 px.
- **Dymek wykresu** (`0 8px 20px rgba(13, 13, 13, 0.10)`): element nad treścią.

### Named Rules
**Zasada płaskiego spoczynku.** W spoczynku nic nie rzuca cienia.

## Shapes

Narożniki lekko zaokrąglone: 6 px dla przycisków i przełączników, 8 px dla kart i paneli, 22 px dla pigułek filtrów. Ramki 1 px. Motyw z identyfikacji to mały kwadrat i romb: kwadrat w symbolu, romb jako znacznik na wykresach.

## Components

### Buttons
- **Kształt:** lekko zaokrąglony prostokąt (6 px), wysokość 44 px, tekst 15 px pogrubiony.
- **Główny:** czarne tło, biały tekst. Na czarnym bloku: biały z czarnym tekstem albo obrys.
- **Najechanie i klik:** unosi się o 1 px w 150 ms, przy kliknięciu opada o 1 px. Wyłączony ma 40% krycia.

### Chips
- **Pigułki filtrów i sortowania:** białe z szarą ramką, wybrana jest czarna z białym tekstem.
- **Przełączniki zakresu wykresu:** ten sam schemat, narożnik 6 px.

### Cards / Containers
- **Karta:** białe tło, ramka 1 px, narożnik 8 px, wnętrze 20 px. Karta-link po najechaniu unosi się o 2 px i dostaje ciemniejszą ramkę. Tak samo zachowują się karty w bibliotece analiz: cała karta prowadzi do strony analizy, a link do PDF działa osobno.
- **Panel:** czarny blok z białym tekstem, wnętrze 24 px. Niesie najważniejsze liczby.

### Navigation
- Pięć pozycji tekstem 15 px. Aktywna jest pogrubiona z czarną kreską 3 px pod spodem. Po najechaniu kreska rysuje się od lewej w 150 ms. Fokus z klawiatury: obrys 3 px w kolorze series-2.

### Przełącznik języka
- Mały przycisk z obrysem w nagłówku, przed „Kontakt”: „EN” na stronach polskich, „PL” na angielskich. Prowadzi do tej samej strony w drugim języku.
- Bez flag i bez żółtego. Na telefonie 40×40 px.

### Przełącznik motywu
- Ostatni element nagłówka, w prawym górnym rogu: kwadratowy przycisk z obrysem jak przełącznik języka (44×44 px, na telefonie 40×40 px). Ikona słońca w trybie ciemnym, księżyca w jasnym, opis dla czytników „Włącz jasny motyw” / „Włącz ciemny motyw”.
- Domyślnie strona idzie za ustawieniem systemu. Wybór zapisuje `assets/js/motyw.js` w localStorage (klucz `fi-motyw`), ładowany w `<head>` bez `defer`, żeby nie mignął zły motyw. To jedyna rzecz zapisywana w przeglądarce (polityka prywatności, pkt 7).

### Pasek kursów
- Dolna część czarnego nagłówka strony głównej, oddzielona cienką linią. Etykieta „Nasze spółki” to biały tekst z żółtym kwadratem przy lewej krawędzi ekranu. Pasek zajmuje całą szerokość. Bez osobnego tła.
- Spadki na czerni mają jaśniejszą czerwień (#FF8A80), wzrosty są białe.
- Na telefonie etykieta bez daty.

### Wykres portfela
- Wzór: wykres kursu z identyfikacji. Gruba granatowa linia funduszu (3,25 px) z kropką i pogrubioną wartością na końcu. Cieńsza, ciągła linia S&P 500 (2 px) z własnym podpisem. Bez legendy i bez wypełnienia.
- Siatka pozioma jasna, linia zera i linia bazowa mocniejsze.
- Żółty romb z czarną ramką na linii funduszu oznacza dzień decyzji.
- Dymek: data, oba wyniki, różnica w punktach procentowych, decyzja z tego dnia.
- Pod wykresem zdanie o źródle danych.

### Wykres wyceny
- Poziome pasy w granatach serii pokazują przedziały z każdej metody. Żółty romb oznacza kurs z dnia raportu. Bez ceny docelowej.

### Ruch
- Nagłówek strony głównej wchodzi raz przy wczytaniu: elementy po kolei, 520 ms, przesunięcie 12 px.
- Reszta ruchu odpowiada tylko na działanie użytkownika. Animowane są wyłącznie przesunięcie i krycie.
- Efekty najechania działają tylko z myszką. Cały ruch wyłącza się przy systemowym ograniczeniu ruchu.

## Do's and Don'ts

### Do:
- **Do** używaj tokenów z `:root` (`var(--black)`, `var(--accent)`, `var(--s1)`…) zamiast wpisywać kolory.
- **Do** podpisuj serie przy samych liniach i podawaj źródło pod wykresem.
- **Do** pokazuj autorów, datę i ujawnienia przy każdej analizie.
- **Do** sprawdzaj każdą zmianę na 375, 768 i 1440 px oraz w trybie ciemnym.
- **Do** oznaczaj pliki samym „(PDF)”.

### Don't:
- **Don't** dodawaj drugiego koloru akcentu, gradientów ani ozdobnych cieni.
- **Don't** używaj żółtego jako tekstu ani cienkiej linii na białym tle.
- **Don't** rysuj danych historycznych linią przerywaną.
- **Don't** animuj sekcji przy przewijaniu.
- **Don't** pokazuj na stronach HTML ocen „kupuj” i „trzymaj”, cen docelowych ani potencjału wzrostu.
- **Don't** dodawaj sekcji rekrutacji, zdjęć stockowych ani logotypów firm bez zgody.
- **Don't** wczytuj czcionek, bibliotek ani frameworków.
- **Don't** układaj strony tak, żeby przypominała Hossa ProCapital.
