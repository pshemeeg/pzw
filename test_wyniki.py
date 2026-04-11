from app import create_app
from app.extensions import db
from app.models import Zawody, Uczestnik, Stanowisko, WynikWagowy

app = create_app()
with app.app_context():
    z = Zawody.query.get(3) # or the recent one
    if z:
        print(f"Zawody {z.id} ({z.nazwa})")
        for u in z.uczestnicy:
            print(f"Uczestnik {u.zawodnik.nazwisko}:")
            for s in u.stanowiska:
                if s.wynik_wagowy:
                    print(f"  Tura {s.tura}: {s.wynik_wagowy.waga_g}g (stanowisko.id={s.id})")
                else:
                    print(f"  Tura {s.tura}: brak (stanowisko.id={s.id})")
