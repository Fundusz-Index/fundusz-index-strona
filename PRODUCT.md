# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Kolejność potwierdzona przez Szymona 16.11.2026.

1. **Potencjalny partner lub sponsor.** Osoba z firmy doradczej, inwestycyjnej albo z działu employer brandingu. Sprawdza, czy projekt jest poważny i czy warto się z nim związać. Ma kilka minut. Chce zobaczyć ludzi, wyniki i jakość analiz, a potem umówić rozmowę.
2. **Rekruter i absolwent koła.** Szuka nazwiska konkretnego analityka i jego pracy. Otwiera analizę, patrzy na autorów i metodę.
3. **Student UEK i członek koła INDEX.** Chce wiedzieć, co fundusz ma w portfelu, dlaczego i jak mu idzie. Czyta analizy, żeby się uczyć.
4. **Członek funduszu.** Pokazuje stronę jako dowód własnej pracy. Sprawdza portfel i kalendarz.

## Product Purpose

Strona pokazuje pracę Funduszu Index: wirtualny portfel liczony codziennie na tle S&P 500 w złotych, analizy spółek z nazwiskami autorów i dziennik decyzji. Istnieje po to, żeby każdą decyzję funduszu dało się sprawdzić.

Sukces: partner po wizycie pisze na adres funduszu. Rekruter znajduje analizę i autora w dwóch kliknięciach. Student rozumie, dlaczego spółka jest w portfelu.

## Positioning

Fundusz Index jest wzorowany na funduszach zarządzanych przez studentów na uczelniach w USA. W Europie Środkowo-Wschodniej takich projektów jest niewiele. To pierwsza rzecz, którą strona ma przekazać.

Fundusz publikuje każdą decyzję razem z analizą, datą i nazwiskami autorów, także wtedy, gdy portfel traci do indeksu. Wynik liczy skrypt z publicznych kursów, nikt nie wpisuje go ręcznie. Większość studenckich projektów inwestycyjnych pokazuje tylko opis działalności.

## Operating Context

- Projekt edukacyjny Koła Naukowego Rynku Kapitałowego INDEX na Uniwersytecie Ekonomicznym w Krakowie. Prowadzi go Fundacja Index (KRS 0001137760).
- Portfel jest wirtualny: 100 000 zł umownego kapitału od 13.01.2026. Zakupy mają daty pierwszych analiz spółek, a stronę z portfelem uruchomiono w listopadzie 2026 (wyniki za wcześniejsze miesiące policzone wstecz, co strona mówi wprost).
- Decyzje zapadają większością głosów członków funduszu po prezentacji analizy.
- Dane odświeżają się automatycznie w dni robocze po sesji w USA.
- Treść wprowadza zarząd przez repozytorium. Nie ma panelu do edycji.
- Docelowy adres: fundusz.knrkindex.pl. Strona koła (knrkindex.pl) to osobny serwis.

## Capabilities and Constraints

**Co strona robi**

- Portfel: wykres funduszu i S&P 500, skład, liczby, spółki z tezami, dziennik decyzji.
- Analizy: biblioteka z filtrami, strona każdej analizy z wyceną, autorami, ujawnieniami i raportem PDF.
- Start: pasek kursów, portfel w skrócie, ostatnia decyzja, najnowsze analizy, kalendarz.
- Artykuły, opis funduszu, dokumenty prawne, oferta współpracy (PDF).

**Ograniczenia**

- Statyczne HTML, CSS i JavaScript. Bez bibliotek, frameworków i bazy danych.
- Na stronach HTML nie ma ocen typu „kupuj” ani „trzymaj”, cen docelowych ani potencjału wzrostu. Pokazujemy przedziały wycen i metodę. Raporty PDF publikujemy w wersji autorów.
- Każda analiza ma autorów i sekcję ujawnień (MAR art. 20, rozporządzenie 2016/958).
- Na każdej stronie zastrzeżenie: projekt edukacyjny, nie fundusz inwestycyjny, portfel wirtualny, analizy to nie porada inwestycyjna.
- Zdjęcia i nazwiska członków tylko za zgodą.
- Nie ma sekcji rekrutacji. Rekrutacja jest zamknięta.

**Nieustalone**

- Hosting (Zenbox albo Cloudflare Pages).
- Daty i godziny publikacji analiz.
- Newsletter: formularz wyłączony do czasu przygotowania Dysku funduszu.
- Opiekun naukowy i partnerzy: na razie brak.

## Brand Commitments

- Nazwa: Fundusz Index. Znak i logo z identyfikacji v1 (listopad 2026).
- Język polski. Krótkie zdania. Ton naturalny, ciepły i profesjonalny. Bez długich myślników i słów-wypełniaczy.
- Mówimy „my”. Piszemy o tym, co zrobiliśmy, nie o tym, jacy jesteśmy.
- Strona nie może przypominać strony funduszu Hossa ProCapital.
- Nie wspominamy dawnego sponsora ani dawnego koordynatora.
- Partnerów i Wall Street Prep wymieniamy tylko za zgodą.
- Linki do plików oznaczamy samym „(PDF)”.

## Evidence on Hand

- Pięć analiz z października 2026: WMB, GOOGL, CVX, EME, AMD. Raporty w `pliki/analizy/`.
- Wynik portfela i seria dzienna: `data/portfolio.json` (generowany).
- Transakcje z tezami: `data/transakcje.csv`.
- Liczby koła: 25+ lat działalności, 300+ prezentacji, 60+ opracowań, ok. 185 członków koła, 26 członków funduszu, 13 analityków.
- Oferta współpracy: `pliki/fundusz-index-oferta-wspolpracy.pdf`.
- Brak: opinii partnerów, logotypów firm, zdjęć członków, historii wyników sprzed 13.01.2026. Nie wolno ich wymyślać.

## Product Principles

1. **Każda liczba ma źródło.** Wynik, kurs i wycena prowadzą do danych albo do raportu.
2. **Autor zawsze z nazwiska.** Analiza bez autorów nie trafia na stronę.
3. **Pokazujemy też straty.** Wynik gorszy od indeksu jest widoczny tak samo jak lepszy.
4. **Uczymy, nie doradzamy.** Tłumaczymy metodę i tezę. Nie mówimy czytelnikowi, co ma kupić.
5. **Prosto i lekko.** Strona ma działać szybko na telefonie i dać się utrzymać przez kolejny zarząd.

## Accessibility & Inclusion

- Cel: WCAG 2.2 AA.
- Cele dotykowe min. 24 px, tekst min. 12 px, widoczny fokus, link „Przejdź do treści”.
- Tryb jasny i ciemny. Ruch wyłącza się przy systemowym ustawieniu ograniczenia ruchu.
- Informacji nie przekazujemy samym kolorem: strata ma znak minus, szacowany termin ma przerywaną ramkę.
