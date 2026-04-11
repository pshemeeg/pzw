from app import create_app
from app.extensions import db
from app.models import Zawody
from app.blueprints.zawody.helpers import oblicz_klasyfikacje

app = create_app()
with app.app_context():
    z = Zawody.query.filter(Zawody.liczba_tur > 1).order_by(Zawody.id.desc()).first()
    if z:
        print(f"Zawody {z.id} ({z.nazwa}), tury: {z.liczba_tur}")
        klas = oblicz_klasyfikacje(z)
        for r in klas['indywidualna']:
            print(f"{r['miejsce']}. {r['uczestnik'].zawodnik.nazwisko} - punkty_tury: {r['punkty_tury']}, suma_sektorowych: {r['suma_sektorowych']}, suma_wag: {r['suma_wag']}")
    else:
        print("Brak zawodów z wieloma turami.")
