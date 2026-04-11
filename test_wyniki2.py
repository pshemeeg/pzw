from app import create_app
from app.extensions import db
from app.models import Zawody

app = create_app()
with app.app_context():
    z = Zawody.query.filter(Zawody.liczba_tur > 1).order_by(Zawody.id.desc()).first()
    if z:
        print(f"Zawody {z.id} ({z.nazwa}), tury: {z.liczba_tur}")
        for u in z.uczestnicy:
            print(f"Uczestnik {u.zawodnik.nazwisko}:")
            for s in u.stanowiska:
                if z.dyscyplina.typ_wyniku == 'wagowy':
                    waga = s.wynik_wagowy.waga_g if s.wynik_wagowy else 'brak'
                    print(f"  Tura {s.tura}: {waga}g")
                elif z.dyscyplina.typ_wyniku == 'punktowy':
                    waga = [r.punkty for r in s.wyniki_ryby] if s.wyniki_ryby else 'brak'
                    print(f"  Tura {s.tura}: {waga} pkt")
    else:
        print("Brak zawodów z wieloma turami.")
