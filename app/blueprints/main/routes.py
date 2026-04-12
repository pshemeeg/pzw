from flask import render_template
from flask_login import login_required, current_user
from sqlalchemy import desc, func
from datetime import datetime

from app.blueprints.main import bp
from app.extensions import db
from app.models import Zawody, Zawodnik, Sedzia, Uczestnik


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
