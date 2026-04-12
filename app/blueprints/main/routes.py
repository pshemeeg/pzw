from flask import render_template
from flask_login import login_required, current_user
from sqlalchemy import desc

from app.blueprints.main import bp
from app.extensions import db
from app.models import Zawody, Zawodnik, Sedzia


@bp.route("/")
def index():
    ostatnie_zawody = Zawody.query.filter_by(status="zakonczone").order_by(desc(Zawody.data)).limit(5).all()
    return render_template("main/index.html", ostatnie_zawody=ostatnie_zawody)


@bp.route("/dashboard")
@login_required
def dashboard():
    ostatnie_zawody = Zawody.query.order_by(desc(Zawody.data)).limit(10).all()
    liczba_zawodow = Zawody.query.count()
    liczba_zawodnikow = Zawodnik.query.count()
    liczba_sedziow = Sedzia.query.count()

    return render_template(
        "main/dashboard.html",
        ostatnie_zawody=ostatnie_zawody,
        liczba_zawodow=liczba_zawodow,
        liczba_zawodnikow=liczba_zawodnikow,
        liczba_sedziow=liczba_sedziow,
    )
