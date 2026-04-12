# PZW — System Obsługi Zawodów Wędkarskich
 
Profesjonalna aplikacja webowa do kompleksowego zarządzania zawodami wędkarskimi, w pełni zgodna z Zasadami Organizacji Sportu Wędkarskiego (ZOSW) PZW.
 
## Główne Funkcjonalności
 
- **Zarządzanie Zawodami:** Tworzenie zawodów jedno i wieloturowych, wybór dyscyplin (Spławik, Feeder, Spinning, Mucha, Karpiówka).
- **Automatyzacja:** Inteligentne losowanie stanowisk z uwzględnieniem zasady drużynowej.
- **System Wyników:** Wprowadzanie wagi, sztuk lub długości ryb bezpośrednio na łowisku (RWD - mobile first).
- **Klasyfikacja Grand Prix:** Automatyczne wyliczanie rankingów rocznych i trendów zawodników.
- **RODO & Prywatność:** Wbudowany system anonimizacji danych dla osób bez zgody marketingowej w widokach publicznych.
- **Centrum Dokumentów:** Generator protokołów PDF (WeasyPrint), wzory oświadczeń RODO oraz kompletna instrukcja obsługi.
- **Import Danych:** Masowy import zawodników i łowisk z plików CSV.
- **Personalizacja:** Ustawienia profilu sędziego z domyślnymi wartościami dla nowych zawodów.
 
## Stack technologiczny
 
- **Backend:** Python 3.12 + Flask
- **Frontend:** TailwindCSS + Alpine.js + Chart.js (Dashboard)
- **Baza Danych:** SQLAlchemy (SQLite dla dev/test, MariaDB/MySQL dla prod)
- **Raporty:** WeasyPrint (Silnik PDF)
- **Konteneryzacja:** Docker + Docker Compose
 
## Struktura projektu
 
```
pzw/
├── app/
│   ├── blueprints/
│   │   ├── auth/            # Autoryzacja i sesje
│   │   ├── zawody/          # Logika zawodów i losowania
│   │   ├── zawodnicy/       # Baza członków i importy
│   │   ├── wyniki/          # Scoring i punktacja ZOSW
│   │   ├── cms/             # Regulaminy i pomoc
│   │   ├── profil/          # Ustawienia sędziego
│   │   └── main/            # Dashboard i Strona Główna
│   ├── templates/           # Nowoczesne szablony Jinja2
│   └── static/              # CSS, JS, Branding
├── tests/                   # Pakiet testów automatycznych (pytest)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```
 
## Szybki start (Lokalnie)
 
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask db upgrade
flask run
```
 
## Uruchomienie przez Docker
 
```bash
docker compose up --build
```
 
## Testy
 
Uruchomienie pełnego pakietu testów (scenariusze GP, RODO, Scoring):
```bash
pytest tests/ -v
```
 
---
Wszelkie prawa zastrzeżone © 2026. Projekt hobbystyczny wspierany przez AI.
