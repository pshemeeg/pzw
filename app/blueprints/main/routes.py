import io
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


from app.blueprints.main.helpers import generate_csv_template, calculate_gp_ranking

@bp.route("/grand-prix")
@login_required
def grand_prix():
    sezon = request.args.get("sezon", datetime.now().year, type=int)
    ranking, zawody_gp, detale_zawodow = calculate_gp_ranking(sezon)
    
    sezymy_raw = db.session.query(Zawody.sezon).distinct().order_by(Zawody.sezon.desc()).all()
    sezony = [s[0] for s in sezymy_raw]

    return render_template(
        "main/grand_prix.html",
        ranking=ranking,
        zawody_gp=zawody_gp,
        detale_zawodow=detale_zawodow,
        sezon=sezon,
        sezony=sezony
    )

@bp.route("/grand-prix/pdf")
@login_required
def grand_prix_pdf():
    sezon = request.args.get("sezon", datetime.now().year, type=int)
    typ = request.args.get("typ", "prosty") # 'prosty' lub 'zaawansowany'
    
    ranking, zawody_gp, detale_zawodow = calculate_gp_ranking(sezon)
    
    rendered_html = render_template(
        "main/grand_prix_pdf.html",
        ranking=ranking,
        zawody_gp=zawody_gp,
        detale_zawodow=detale_zawodow,
        sezon=sezon,
        typ=typ,
        now_datetime=datetime.now()
    )

    try:
        from weasyprint import HTML
        pdf_file = HTML(string=rendered_html).write_pdf()
        return send_file(
            io.BytesIO(pdf_file),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"grand_prix_{sezon}_{typ}.pdf"
        )
    except Exception as e:
        from flask import flash, redirect, url_for
        flash(f"Błąd generowania PDF: {str(e)}", "danger")
        return redirect(url_for("main.grand_prix", sezon=sezon))


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



