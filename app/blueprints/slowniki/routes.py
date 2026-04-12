from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required

from app.blueprints.slowniki import bp
from app.extensions import db
from app.models import Dyscyplina, Lowisko, GatunekRyby


@bp.route("/")
@login_required
def index():
    dyscypliny = Dyscyplina.query.order_by(Dyscyplina.nazwa).all()
    lowiska = Lowisko.query.order_by(Lowisko.nazwa).all()
    ryby = GatunekRyby.query.order_by(GatunekRyby.nazwa).all()
    return render_template(
        "slowniki/index.html", dyscypliny=dyscypliny, lowiska=lowiska, ryby=ryby
    )


@bp.route("/lowiska/nowe", methods=["GET", "POST"])
@login_required
def lowisko_nowe():
    if request.method == "POST":
        lowisko = Lowisko(
            nazwa=request.form["nazwa"].strip(),
            miejscowosc=request.form["miejscowosc"].strip(),
            opis=request.form.get("opis", "").strip() or None,
        )
        db.session.add(lowisko)
        db.session.commit()
        flash("Łowisko zostało dodane.", "success")
        return redirect(url_for("slowniki.index"))
    return render_template("slowniki/lowisko_form.html", lowisko=None)


@bp.route("/lowiska/<int:lid>/edytuj", methods=["GET", "POST"])
@login_required
def lowisko_edytuj(lid):
    lowisko = db.session.get(Lowisko, lid)
    if not lowisko:
        flash("Nie znaleziono łowiska.", "danger")
        return redirect(url_for("slowniki.index"))
    if request.method == "POST":
        lowisko.nazwa = request.form["nazwa"].strip()
        lowisko.miejscowosc = request.form["miejscowosc"].strip()
        lowisko.opis = request.form.get("opis", "").strip() or None
        db.session.commit()
        flash("Łowisko zostało zaktualizowane.", "success")
        return redirect(url_for("slowniki.index"))
    return render_template("slowniki/lowisko_form.html", lowisko=lowisko)


@bp.route("/lowiska/<int:lid>/usun", methods=["POST"])
@login_required
def lowisko_usun(lid):
    lowisko = db.session.get(Lowisko, lid)
    if not lowisko:
        flash("Nie znaleziono łowiska.", "danger")
        return redirect(url_for("slowniki.index"))
    db.session.delete(lowisko)
    db.session.commit()
    flash("Łowisko zostało usunięte.", "success")
    return redirect(url_for("slowniki.index"))


@bp.route("/dyscypliny/nowe", methods=["GET", "POST"])
@login_required
def dyscyplina_nowa():
    if request.method == "POST":
        dyscyplina = Dyscyplina(
            nazwa=request.form["nazwa"].strip(),
            kod=request.form["kod"].strip().lower(),
            typ_wyniku=request.form["typ_wyniku"],
        )
        db.session.add(dyscyplina)
        db.session.commit()
        flash("Dyscyplina została dodana.", "success")
        return redirect(url_for("slowniki.index"))
    return render_template("slowniki/dyscyplina_form.html", dyscyplina=None)


@bp.route("/dyscypliny/<int:did>/edytuj", methods=["GET", "POST"])
@login_required
def dyscyplina_edytuj(did):
    dyscyplina = db.session.get(Dyscyplina, did)
    if not dyscyplina:
        flash("Nie znaleziono dyscypliny.", "danger")
        return redirect(url_for("slowniki.index"))
    if request.method == "POST":
        dyscyplina.nazwa = request.form["nazwa"].strip()
        dyscyplina.kod = request.form["kod"].strip().lower()
        dyscyplina.typ_wyniku = request.form["typ_wyniku"]
        db.session.commit()
        flash("Dyscyplina została zaktualizowana.", "success")
        return redirect(url_for("slowniki.index"))
    return render_template("slowniki/dyscyplina_form.html", dyscyplina=dyscyplina)


@bp.route("/dyscypliny/<int:did>/usun", methods=["POST"])
@login_required
def dyscyplina_usun(did):
    dyscyplina = db.session.get(Dyscyplina, did)
    if not dyscyplina:
        flash("Nie znaleziono dyscypliny.", "danger")
        return redirect(url_for("slowniki.index"))
    db.session.delete(dyscyplina)
    db.session.commit()
    flash("Dyscyplina została usunięta.", "success")
    return redirect(url_for("slowniki.index"))

@bp.route("/ryby/nowe", methods=["GET", "POST"])
@login_required
def ryba_nowa():
    if request.method == "POST":
        ryba = GatunekRyby(
            nazwa=request.form["nazwa"].strip(),
            wymiar_ochronny_mm=int(request.form.get("wymiar_ochronny_mm") or 0),
            wymiar_punktowany_mm=int(request.form.get("wymiar_punktowany_mm") or 0),
            punkty_bazowe=int(request.form.get("punkty_bazowe") or 0),
            punkty_za_mm=float(request.form.get("punkty_za_mm") or 0.0),
        )
        db.session.add(ryba)
        db.session.commit()
        flash("Gatunek ryby został dodany.", "success")
        return redirect(url_for("slowniki.index"))
    return render_template("slowniki/ryba_form.html", ryba=None)


@bp.route("/ryby/<int:rid>/edytuj", methods=["GET", "POST"])
@login_required
def ryba_edytuj(rid):
    ryba = db.session.get(GatunekRyby, rid)
    if not ryba:
        flash("Nie znaleziono gatunku.", "danger")
        return redirect(url_for("slowniki.index"))
    if request.method == "POST":
        ryba.nazwa = request.form["nazwa"].strip()
        ryba.wymiar_ochronny_mm = int(request.form.get("wymiar_ochronny_mm") or 0)
        ryba.wymiar_punktowany_mm = int(request.form.get("wymiar_punktowany_mm") or 0)
        ryba.punkty_bazowe = int(request.form.get("punkty_bazowe") or 0)
        ryba.punkty_za_mm = float(request.form.get("punkty_za_mm") or 0.0)
        db.session.commit()
        flash("Gatunek ryby został zaktualizowany.", "success")
        return redirect(url_for("slowniki.index"))
    return render_template("slowniki/ryba_form.html", ryba=ryba)


@bp.route("/ryby/<int:rid>/usun", methods=["POST"])
@login_required
def ryba_usun(rid):
    ryba = db.session.get(GatunekRyby, rid)
    if not ryba:
        flash("Nie znaleziono gatunku.", "danger")
        return redirect(url_for("slowniki.index"))
    db.session.delete(ryba)
    db.session.commit()
    flash("Gatunek ryby został usunięty.", "success")
    return redirect(url_for("slowniki.index"))
