# Wdrożenie na Zenbox: fundusz.knrkindex.pl

Strona jest statyczna. GitHub sam wgrywa ją na Zenbox przez FTPS (`.github/workflows/wdrozenie-zenbox.yml`):
po każdej zmianie na `main`, po nocnej aktualizacji danych portfela i na żądanie (Actions → Wdrożenie na Zenbox → Run workflow).

Hasła, loginy i adresy serwera wpisujemy tylko w panelu Zenbox i w sekretach GitHuba. Nigdy w plikach repozytorium (jest publiczne) ani w czacie.

## Stan: wdrożone 25.11.2026

Strona działa pod `https://fundusz.knrkindex.pl` od 25.11.2026 (data pierwszej publikacji analiz: 26.11.2026).
Tak to jest ustawione:

| Co | Jak |
| --- | --- |
| Hosting | Panel Klienta Zenbox na koncie hostingowym koła i fundacji (tym samym, na którym stoi `knrkindex.pl`). Loguje się Szymon; przy logowaniu z nowego urządzenia Zenbox wysyła kod autoryzacji |
| Domena strony | `fundusz.knrkindex.pl` dodana jako **osobna domena** (Domeny → Konfiguracja domen), nie jako subdomena. Ma własny katalog `domains/fundusz.knrkindex.pl/public_html`, własną strefę DNS i własny certyfikat. Strona koła (`knrkindex.pl`, WordPress) jest nietknięta: inny katalog, inny certyfikat |
| DNS | Strefa w Zenbox, `fundusz` i `www.fundusz` kierują na serwer hostingu. Powstała sama przy dodaniu domeny |
| SSL | Zaawansowane → Certyfikat SSL → `fundusz.knrkindex.pl` → darmowy Let's Encrypt (CN `fundusz.knrkindex.pl`, pozycje `fundusz.knrkindex.pl` i `www.fundusz.knrkindex.pl`). Panel odnawia go sam |
| Konto FTP | Osobne konto (Hosting → Konta FTP → `fundusz.knrkindex.pl`) z katalogiem głównym `public_html` tej domeny (opcja „Dowolny”). Widzi tylko pliki naszej strony |
| Sekrety GitHuba | `FTP_SERWER`, `FTP_LOGIN`, `FTP_HASLO` (wartości tylko w sekretach) |
| Zmienne GitHuba | `ZENBOX_WLACZONE` = `tak`. `ZENBOX_KATALOG` nie jest potrzebna, bo konto FTP startuje od razu w `public_html` |

Zmiana hasła FTP: panel Zenbox → Konta FTP → „Zmień” przy koncie strony, potem nowe hasło w sekrecie `FTP_HASLO`.
Wyłączenie wgrywania (np. na czas prac): zmienna `ZENBOX_WLACZONE` na cokolwiek innego niż `tak`.

Dlaczego osobna domena, a nie subdomena: w Zenbox certyfikat jest jeden na domenę, więc subdomena w katalogu WordPressa
koła musiałaby dzielić certyfikat ze stroną koła (ten jest wgrany ręcznie i odnawiany poza panelem). Osobna domena nie dotyka
strony koła w ogóle. Decyzja Szymona z 25.11.2026.

## Jak to ustawić od zera (gdyby trzeba było powtórzyć)

### 1. Panel Zenbox: domena

1. Domeny → Konfiguracja domen → **Dodaj następną domenę** → `fundusz.knrkindex.pl` → Utwórz. Strona koła (WordPress) zostaje bez zmian.
2. Jeśli wcześniej istniała subdomena `fundusz` przy `knrkindex.pl` (Domeny → Subdomeny), najpierw ją usuń, bez zaznaczania „Usuń zawartość katalogu”. Panel nie pozwoli dodać domeny o tej samej nazwie.
3. Zaawansowane → Certyfikat SSL → `fundusz.knrkindex.pl` → „Darmowy certyfikat od Let's Encrypt”, CN `fundusz.knrkindex.pl`, zaznaczone `fundusz.knrkindex.pl` i `www.fundusz.knrkindex.pl` → Zapisz. Wydanie trwa kilkanaście sekund.
4. DNS: strefa domeny powstaje sama. Sprawdź np. `https://dns.google/resolve?name=fundusz.knrkindex.pl&type=A`, ma zwracać adres serwera hostingu.

### 2. Panel Zenbox: konto FTP tylko dla strony

1. Hosting → Konta FTP → `fundusz.knrkindex.pl` → **Utwórz konto FTP**: dowolna nazwa użytkownika, opcja „Dowolny” z katalogiem `public_html` tej domeny (panel podpowiada pełną ścieżkę), hasło z przycisku „Losowe” (skopiuj je). Dzięki temu automat nie może dotknąć strony koła.
2. Zapisz: adres serwera FTP (panel pokazuje go na pasku „Twoje konto”), login (`użytkownik@fundusz.knrkindex.pl`), hasło.

### 3. GitHub: sekrety

Repozytorium → Settings → Secrets and variables → Actions → zakładka **Secrets** → New repository secret:

| Nazwa | Wartość |
| --- | --- |
| `FTP_SERWER` | adres serwera FTP z panelu Zenbox |
| `FTP_LOGIN` | login konta FTP z kroku 2 |
| `FTP_HASLO` | hasło konta FTP z kroku 2 |

### 4. GitHub: zmienne (włączenie wgrywania)

Ta sama strona ustawień → zakładka **Variables** → New repository variable:

| Nazwa | Wartość |
| --- | --- |
| `ZENBOX_WLACZONE` | `tak` |
| `ZENBOX_KATALOG` | tylko gdy konto FTP widzi szerszy katalog niż strona: ścieżka do katalogu strony zakończona `/`. Gdy konto FTP startuje od razu w `public_html`, nie dodawaj tej zmiennej |

### 5. Pierwsze wgranie

1. Wgrywanie przerywa się, jeśli na stronie są pola w `[nawiasach]` (`sprawdz_dane.py --publikacja`). Przed startem trzeba więc wpisać datę pierwszej publikacji analiz: `python3 scripts/start.py "DD.MM.RRRR"` (albo z godziną: `"DD.MM.RRRR, GG:MM"`), potem commit i push. Zrobione 25.11.2026 z datą 26.11.2026.
2. Push na `main` uruchamia wgranie sam. Ręcznie: GitHub → Actions → **Wdrożenie na Zenbox** → Run workflow.
3. Pierwsze wgranie trwa około minuty (cała strona). Kolejne wysyłają tylko zmienione pliki.

### 6. Sprawdzenie po starcie (przeszło 25.11.2026)

- `https://fundusz.knrkindex.pl` otwiera stronę główną, a `http://` przekierowuje na `https://`.
- Zły adres (np. `/xyz`) pokazuje stronę „Nie ma takiej strony” ze stylami.
- Portfel pokazuje wykres i aktualną datę danych. Następnego dnia roboczego po 23:30 dane powinny się zaktualizować same.
- Linki do raportów PDF działają.
- Katalogi robocze (`scripts`, `tests`, `zrodla`, `i18n`, `wdrozenie`) i pliki `.md` nie są wgrywane na serwer (404). Pliki z kropką (`.htaccess`, `.ftp-deploy-sync-state.json`) odpowiadają 403.
- Nagłówki bezpieczeństwa i kompresja (brotli) działają. HSTS jest wyłączony.

## Do zrobienia po starcie

- Po kilku dniach poprawnego działania SSL włączyć HSTS (linia z komentarzem w `.htaccess`).
- Dodać stronę w Google Search Console i zgłosić `https://fundusz.knrkindex.pl/sitemap.xml`.
- W polityce prywatności wpisać, jak długo Zenbox przechowuje logi serwera (sprawdzić w panelu: Zaawansowane → Logi serwera, albo zapytać pomoc Zenbox).
- Sprawy samego konta hostingu (limity pakietu, odnowienie domeny `knrkindex.pl`) są opisane w notatce w projekcie Claude „Fundusz INDEX”, nie tutaj.
