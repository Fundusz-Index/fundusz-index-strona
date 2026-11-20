# Wdrożenie na Zenbox: fundusz.knrkindex.pl

Strona jest statyczna. GitHub sam wgrywa ją na Zenbox przez FTPS (`.github/workflows/wdrozenie-zenbox.yml`):
po każdej zmianie na `main`, po nocnej aktualizacji danych portfela i na żądanie.
Dopóki nie wykonasz kroku 4, wgrywanie jest wyłączone i nic się nie dzieje.

Hasła wpisujesz tylko w panelu Zenbox i w sekretach GitHuba. Nigdy w plikach ani w czacie.

## 1. Panel Zenbox: subdomena

1. Dodaj subdomenę `fundusz` do domeny `knrkindex.pl`. Strona koła (WordPress) zostaje bez zmian.
2. Zapisz, jaki katalog panel przypisał subdomenie (np. `domains/knrkindex.pl/public_html/fundusz` albo podobny).
3. Włącz dla subdomeny darmowy certyfikat SSL (Let's Encrypt). Bywa, że wydaje się dopiero po kilku minutach od utworzenia subdomeny.
4. Jeśli DNS domeny jest w Zenbox, rekord dla `fundusz` powstaje sam. Sprawdź to w strefie DNS domeny.

## 2. Panel Zenbox: konto FTP tylko dla strony

1. Utwórz osobne konto FTP z dostępem **tylko do katalogu subdomeny** z kroku 1.2. Dzięki temu automat nie może dotknąć strony koła.
2. Zapisz: adres serwera FTP, login, hasło.

## 3. GitHub: sekrety

Repozytorium → Settings → Secrets and variables → Actions → zakładka **Secrets** → New repository secret:

| Nazwa | Wartość |
| --- | --- |
| `FTP_SERWER` | adres serwera FTP z panelu Zenbox |
| `FTP_LOGIN` | login konta FTP z kroku 2 |
| `FTP_HASLO` | hasło konta FTP z kroku 2 |

## 4. GitHub: zmienne (włączenie wgrywania)

Ta sama strona ustawień → zakładka **Variables** → New repository variable:

| Nazwa | Wartość |
| --- | --- |
| `ZENBOX_WLACZONE` | `tak` |
| `ZENBOX_KATALOG` | tylko gdy konto FTP widzi szerszy katalog niż subdomena: ścieżka do katalogu subdomeny zakończona `/`. Gdy konto FTP startuje od razu w katalogu subdomeny, nie dodawaj tej zmiennej |

## 5. Pierwsze wgranie

1. Wgrywanie przerywa się, jeśli na stronie są pola w `[nawiasach]` (`sprawdz_dane.py --publikacja`). Przed startem trzeba więc wpisać datę i godzinę pierwszej publikacji analiz (robi to Claude w dniu startu, razem z przebudową PDF-ów).
2. GitHub → Actions → **Wdrożenie na Zenbox** → Run workflow.
3. Pierwsze wgranie trwa kilka minut (cała strona). Kolejne wysyłają tylko zmienione pliki.

## 6. Sprawdzenie po starcie

- `https://fundusz.knrkindex.pl` otwiera stronę główną, a `http://` przekierowuje na `https://`.
- Zły adres (np. `/xyz`) pokazuje stronę „Nie ma takiej strony” ze stylami.
- Portfel pokazuje wykres i aktualną datę danych. Następnego dnia roboczego po 23:30 dane powinny się zaktualizować same.
- Linki do raportów PDF działają.
- Katalogi robocze (`scripts`, `tests`, `zrodla`, `i18n`, `wdrozenie`) i pliki `.md` nie są wgrywane na serwer.
- Po kilku dniach poprawnego działania SSL można włączyć HSTS (linia z komentarzem w `.htaccess`).
- Warto dodać stronę w Google Search Console i zgłosić `https://fundusz.knrkindex.pl/sitemap.xml`.
- W polityce prywatności wpisać, jak długo Zenbox przechowuje logi serwera (sprawdzić w panelu albo zapytać pomoc Zenbox).
