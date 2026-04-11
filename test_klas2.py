from app import create_app
from app.models import Zawody
from app.blueprints.zawody.helpers import oblicz_klasyfikacje
app = create_app()
with app.app_context():
    z = Zawody.query.get(1)
    klas = oblicz_klasyfikacje(z)
    for r in klas['indywidualna']:
        print(f"UID {r['uczestnik'].id} ({r['uczestnik'].zawodnik.nazwisko}) - {r['punkty_tury']}")
