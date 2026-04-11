from app import create_app
from app.models import Zawody, Uczestnik, Stanowisko
from collections import defaultdict
from app.blueprints.zawody.helpers import oblicz_klasyfikacje

app = create_app()
with app.app_context():
    z = Zawody.query.get(1)
    print(f"ZAWODY {z.id} - {z.nazwa}")
    for u in z.uczestnicy:
        print(f" U: {u.id} - {u.zawodnik.nazwisko}")
        for s in u.stanowiska:
            waga = s.wynik_wagowy.waga_g if s.wynik_wagowy else 'Brak'
            print(f"   Tura {s.tura} Sektor {s.sektor} Nr {s.numer} -> waga: {waga}")

    print("--- OBLICZ KLASYFIKACJE ---")
    klas = oblicz_klasyfikacje(z)
    for i in klas['indywidualna']:
        print(f"{i['miejsce']}. U{i['uczestnik'].id} {i['uczestnik'].zawodnik.nazwisko} -> {i['punkty_tury']} sum: {i['suma_sektorowych']} wag: {i['suma_wag']}")
