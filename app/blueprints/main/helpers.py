import csv
import io
from flask import send_file
from app.models import Zawody, Zawodnik
from app.blueprints.zawody.helpers import oblicz_klasyfikacje

def generate_csv_template(columns):
    """Generuje obiekt BytesIO zawierający plik CSV z nagłówkami."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=columns)
    writer.writeheader()
    
    # Przekonwertuj na BytesIO dla Flask send_file
    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8'))
    mem.seek(0)
    return mem

def calculate_gp_ranking(sezon):
    """
    Oblicza ranking Grand Prix dla danego sezonu.
    Zwraca: (ranking, zawody_gp, detale_zawodow)
    """
    # Pobierz wszystkie zawody GP w tym sezonie, posortowane chronologicznie
    zawody_gp = Zawody.query.filter_by(grand_prix=True, sezon=sezon).order_by(Zawody.data).all()
    
    ranking = {}
    detale_zawodow = {} # zawody_id -> wyniki_zawodow
    
    # Przebieg zmian rankingu po każdych zawodach
    historia_rankingu = [] # lista list (ranking po n-tych zawodach)

    for i, z in enumerate(zawody_gp):
        wyniki_zawodow = oblicz_klasyfikacje(z)
        detale_zawodow[z.id] = wyniki_zawodow
        
        max_miejsce = len(wyniki_zawodow['indywidualna']) + 1
        startujacy_ids = set()
        
        for r in wyniki_zawodow['indywidualna']:
            zid = r['uczestnik'].zawodnik.id
            startujacy_ids.add(zid)
            
            if zid not in ranking:
                ranking[zid] = {
                    'zawodnik': r['uczestnik'].zawodnik,
                    'wyniki_per_zawody': {}, # zawody_id -> miejsce
                    'suma_miejsc': 0,
                    'suma_wag': 0,
                    'historia_pozycji': [] # pozycja po 1, 2, 3 zawodach...
                }
            
            miejsce = r['miejsce'] if isinstance(r['miejsce'], (int, float)) else max_miejsce
            ranking[zid]['wyniki_per_zawody'][z.id] = miejsce
            ranking[zid]['suma_miejsc'] += miejsce
            ranking[zid]['suma_wag'] += r['suma_wag']
            
        # Obsługa nieobecnych (kara punktowa)
        # Pobieramy zawodników, którzy startowali w JAKICHKOLWIEK zawodach GP do tej pory
        for zid, data in ranking.items():
            if data['zawodnik'].id not in startujacy_ids:
                # Jeśli już był w rankingu ale nie startował w TYCH zawodach
                ranking[zid]['wyniki_per_zawody'][z.id] = max_miejsce
                ranking[zid]['suma_miejsc'] += max_miejsce

        # Oblicz pozycję w rankingu PO TYCH zawodach (do śledzenia zmian)
        stan_tymczasowy = sorted(
            ranking.values(),
            key=lambda x: (x['suma_miejsc'], -x['suma_wag'])
        )
        for pos, entry in enumerate(stan_tymczasowy, start=1):
            ranking[entry['zawodnik'].id]['historia_pozycji'].append(pos)

    # Ostateczne sortowanie
    posortowany_ranking = sorted(
        ranking.values(),
        key=lambda x: (x['suma_miejsc'], -x['suma_wag'])
    )
    
    return posortowany_ranking, zawody_gp, detale_zawodow
