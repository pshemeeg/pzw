from flask import render_template, send_file, request, abort
from flask_login import login_required, current_user
from sqlalchemy import desc, func
from datetime import datetime

from app.blueprints.main import bp
from app.extensions import db
from app.models import Zawody, Zawodnik, Sedzia, Uczestnik
from app.blueprints.main.helpers import generate_csv_template


@bp.route("/")
def index():
    # Pokazujemy tylko te, które wg daty są już zakończone
    teraz = datetime.now()
    ostatnie_zawody = [z for z in Zawody.query.order_by(desc(Zawody.data)).all() if z.computed_status == "zakonczone"][:5]
    return render_template("main/index.html", ostatnie_zawody=ostatnie_zawody)


@bp.route("/dashboard")
@login_required
def dashboard():
    teraz = datetime.now()
    wszystkie = Zawody.query.all()
    
    ostatnie_zawody = sorted(wszystkie, key=lambda x: x.updated_at or x.created_at, reverse=True)[:10]
    liczba_zawodow = len(wszystkie)
    liczba_zawodnikow = Zawodnik.query.count()
    liczba_sedziow = Sedzia.query.count()

    # Context Awareness: Moje zawody dzisiaj
    moje_aktywne = []
    if current_user.sedzia:
        sid = current_user.sedzia.id
        moje_aktywne = [z for z in wszystkie if (z.organizator_id == sid or z.sekretarz_id == sid or sid in [s.id for s in z.sedziowie]) and z.computed_status == "w_trakcie"]

    # Statystyki do wykresu: Zawody na miesiąc w bieżącym sezonie
    obecny_rok = teraz.year
    stats_raw = db.session.query(
        func.strftime("%m", Zawody.data), func.count(Zawody.id)
    ).filter(Zawody.sezon == obecny_rok).group_by(func.strftime("%m", Zawody.data)).all()
    
    chart_labels = ["Sty", "Lut", "Mar", "Kwi", "Maj", "Cze", "Lip", "Sie", "Wrz", "Paź", "Lis", "Gru"]
    chart_data = [0] * 12
    for m_str, count in stats_raw:
        chart_data[int(m_str) - 1] = count

    return render_template(
        "main/dashboard.html",
        ostatnie_zawody=ostatnie_zawody,
        liczba_zawodow=liczba_zawodow,
        liczba_zawodnikow=liczba_zawodnikow,
        liczba_sedziow=liczba_sedziow,
        moje_aktywne=moje_aktywne,
        chart_labels=chart_labels,
        chart_data=chart_data
    )


from app.blueprints.zawody.helpers import oblicz_klasyfikacje

@bp.route("/grand-prix")
@login_required
def grand_prix():
    sezon = request.args.get("sezon", datetime.now().year, type=int)
    
    # Pobierz wszystkie zawody GP w tym sezonie
    zawody_gp = Zawody.query.filter_by(grand_prix=True, sezon=sezon).all()
    
    # Mapa: zawodnik_id -> { 'zawodnik': object, 'punkty': [lista_punktow], 'suma': X, 'waga': Y }
    ranking = {}
    
    for z in zawody_gp:
        wyniki_zawodow = oblicz_klasyfikacje(z)
        max_miejsce = len(wyniki_zawodow['indywidualna']) + 1
        
        # Zapamiętaj kto startował
        startujacy_ids = set()
        
        for r in wyniki_zawodow['indywidualna']:
            zid = r['uczestnik'].zawodnik.id
            startujacy_ids.add(zid)
            
            if zid not in ranking:
                ranking[zid] = {
                    'zawodnik': r['uczestnik'].zawodnik,
                    'wyniki_per_zawody': {}, # zawody_id -> miejsce
                    'suma_miejsc': 0,
                    'suma_wag': 0
                }
            
            miejsce = r['miejsce'] if isinstance(r['miejsce'], (int, float)) else max_miejsce
            ranking[zid]['wyniki_per_zawody'][z.id] = miejsce
            ranking[zid]['suma_miejsc'] += miejsce
            ranking[zid]['suma_wag'] += r['suma_wag']
            
        # Obsługa nieobecnych (kara punktowa)
        wszyscy_zawodnicy = Zawodnik.query.all() # Uproszczenie, można zoptymalizować
        for v in wszyscy_zawodnicy:
            if v.id not in startujacy_ids and v.id in ranking:
                ranking[v.id]['wyniki_per_zawody'][z.id] = max_miejsce
                ranking[v.id]['suma_miejsc'] += max_miejsce

    # Sortowanie rankingu: 1. suma miejsc rosnąco, 2. suma wag malejąco
    posortowany_ranking = sorted(
        ranking.values(),
        key=lambda x: (x['suma_miejsc'], -x['suma_wag'])
    )
    
    sezymy_raw = db.session.query(Zawody.sezon).distinct().order_by(Zawody.sezon.desc()).all()
    sezony = [s[0] for s in sezymy_raw]

    return render_template(
        "main/grand_prix.html",
        ranking=posortowany_ranking,
        zawody_gp=zawody_gp,
        sezon=sezon,
        sezony=sezony
    )


@bp.route("/templates/csv/<string:typ>")
@login_required
def download_csv_template(typ):
    """Pobieranie wzorcowych plików CSV."""
    cols_map = {
        "zawodnicy": ["imie", "nazwisko", "kolo", "nr_licencji"],
        "lowiska": ["nazwa", "miejscowosc", "opis"],
        "dyscypliny": ["nazwa", "kod", "typ_wyniku"],
        "ryby": ["nazwa", "wymiar_ochronny_mm", "wymiar_punktowany_mm", "punkty_bazowe", "punkty_za_mm"]
    }
    
    if typ not in cols_map:
        from flask import abort
        abort(404)
        
    mem = generate_csv_template(cols_map[typ])
    return send_file(
        mem,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"szablon_{typ}.csv"
    )



