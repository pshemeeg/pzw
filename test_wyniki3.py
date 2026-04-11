from app import create_app
from app.extensions import db
from app.models import Zawody
from app.blueprints.zawody.helpers import oblicz_klasyfikacje

app = create_app()
with app.app_context():
    z = Zawody.query.filter(Zawody.liczba_tur > 1).order_by(Zawody.id.desc()).first()
    if z:
        print(f"Zawody {z.id} ({z.nazwa}), tury: {z.liczba_tur}")
        
        # Manually trace wyniki_tur
        typ_wyniku = z.dyscyplina.typ_wyniku
        tury = list(range(1, z.liczba_tur + 1))
        wyniki_tur = {t: {} for t in tury}
        
        for u in z.uczestnicy:
            for stan in u.stanowiska:
                t = stan.tura
                if t not in wyniki_tur:
                    continue
                waga_do_remisow = 0
                if stan.wynik_wagowy:
                    waga_do_remisow = stan.wynik_wagowy.waga_g
                wyniki_tur[t][u.id] = {
                    'stanowisko_id': stan.id,
                    'waga': waga_do_remisow
                }
                
        for t in tury:
            print(f"TURA {t}")
            for u_id, d in wyniki_tur[t].items():
                print(f"  u_id {u_id}: waga={d['waga']}, stan={d['stanowisko_id']}")

