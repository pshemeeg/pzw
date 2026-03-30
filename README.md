# PZW — System Obsługi Zawodów Wędkarskich
 
Aplikacja webowa do zarządzania zawodami wędkarskimi zgodna z Zasadami Organizacji
Sportu Wędkarskiego (ZOSW) PZW. Obsługuje losowanie stanowisk, wprowadzanie wyników,
klasyfikację sektorową i końcową oraz generowanie protokołów.
 
## Stack technologiczny
 
- **Python 3.12** + **Flask** — backend i renderowanie szablonów
- **SQLAlchemy ORM** + **Flask-Migrate** — modele i migracje bazy danych
- **MariaDB** — baza danych produkcyjna
- **Docker + Docker Compose** — konteneryzacja
- **Jinja2** — szablony HTML
 
## Struktura projektu
 
```
pzw/
├── app/
│   ├── __init__.py          # Application factory (create_app)
│   ├── extensions.py        # SQLAlchemy, Migrate — inicjalizacja rozszerzeń
│   ├── models.py            # Modele ORM (Zawody, Zawodnik, Stanowisko, …)
│   ├── logging_config.py    # Konfiguracja logów (plik + stdout)
│   ├── blueprints/
│   │   ├── zawody/          # Tworzenie i zarządzanie zawodami
│   │   ├── zawodnicy/       # Rejestracja zawodników, baza globalna
│   │   └── wyniki/          # Wprowadzanie wyników, punktacja, protokoły
│   ├── templates/           # Szablony Jinja2 (per blueprint)
│   └── static/              # CSS, JS, logo
├── logs/                    # Logi aplikacji (gitignore)
├── config.py                # Klasy konfiguracji (Dev / Prod / Test)
├── run.py                   # Punkt wejścia (lokalny dev)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example             # Szablon zmiennych środowiskowych
└── .env                     # Sekrety — NIE w repozytorium
```
 
## Uruchomienie lokalne (bez Dockera)
 
```bash
# 1. Sklonuj i wejdź do folderu
git clone https://github.com/TWOJ_NICK/pzw.git && cd pzw
 
# 2. Utwórz środowisko wirtualne
python3 -m venv .venv
source .venv/bin/activate
 
# 3. Zainstaluj zależności
pip install -r requirements.txt
 
# 4. Skonfiguruj zmienne środowiskowe
cp .env.example .env
# Edytuj .env — uzupełnij SECRET_KEY, dane bazy
 
# 5. Uruchom migracje i aplikację
flask db upgrade
flask run
```
 
## Uruchomienie przez Docker
 
```bash
# Zbuduj i uruchom wszystkie kontenery (app + mariadb)
docker compose up --build
 
# Pierwsza migracja bazy (tylko raz po `up`)
docker compose exec app flask db upgrade
 
# Logi na żywo
docker compose logs -f app
```
 
## Zmienne środowiskowe
 
Skopiuj `.env.example` do `.env` i uzupełnij:
 
| Zmienna | Opis | Przykład |
|---|---|---|
| `SECRET_KEY` | Klucz sesji Flask (min. 32 znaki) | `secrets.token_hex(32)` |
| `FLASK_ENV` | Środowisko | `development` / `production` |
| `DB_USER` | Użytkownik MariaDB | `pzw` |
| `DB_PASSWORD` | Hasło MariaDB | — |
| `DB_HOST` | Host bazy (nazwa serwisu Docker) | `db` |
| `DB_PORT` | Port MariaDB | `3306` |
| `DB_NAME` | Nazwa bazy danych | `pzw_db` |
| `LOG_LEVEL` | Poziom logowania | `DEBUG` / `INFO` |
 
## Obsługiwane dyscypliny
 
Spławik, feeder, method feeder, karpiówka, spinning, mucha, podlodowa.
