from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from werkzeug.security import generate_password_hash

from app.blueprints.sedziowie import bp
from app.extensions import db
from app.models import Sedzia, Uzytkownik


@bp.route("/")
@login_required
def lista():
    sedziowie = Sedzia.query.order_by(Sedzia.nazwisko, Sedzia.imie).all()
    return render_template("sedziowie/lista.html", sedziowie=sedziowie)


@bp.route("/nowy", methods=["GET", "POST"])
@login_required
def nowy():
    if request.method == "POST":
        f = request.form

        sedzia = Sedzia(
            imie=f["imie"].strip(),
            nazwisko=f["nazwisko"].strip(),
            telefon=f.get("telefon", "").strip() or None,
            kolo=f.get("kolo", "").strip() or None,
        )
        db.session.add(sedzia)
        db.session.flush()

        email = f.get("email", "").strip().lower()
        haslo = f.get("haslo", "").strip()

        if email and haslo:
            if Uzytkownik.query.filter_by(email=email).first():
                flash("Użytkownik z tym emailem już istnieje.", "danger")
                db.session.rollback()
                return redirect(url_for("sedziowie.nowy"))
            konto = Uzytkownik(
                email=email,
                haslo_hash=generate_password_hash(haslo),
                rola="sedzia",
                aktywny=True,
                sedzia_id=sedzia.id,
            )
            db.session.add(konto)
        elif email and not haslo:
            flash("Podaj hasło aby utworzyć konto.", "warning")
            db.session.rollback()
            return redirect(url_for("sedziowie.nowy"))

        db.session.commit()
        flash("Sędzia został dodany.", "success")
        return redirect(url_for("sedziowie.lista"))

    return render_template("sedziowie/formularz.html", sedzia=None)


@bp.route("/<int:sid>/edytuj", methods=["GET", "POST"])
@login_required
def edytuj(sid):
    sedzia = db.session.get(Sedzia, sid)
    if not sedzia:
        flash("Nie znaleziono sędziego.", "danger")
        return redirect(url_for("sedziowie.lista"))

    if request.method == "POST":
        f = request.form
        sedzia.imie = f["imie"].strip()
        sedzia.nazwisko = f["nazwisko"].strip()
        sedzia.telefon = f.get("telefon", "").strip() or None
        sedzia.kolo = f.get("kolo", "").strip() or None

        email = f.get("email", "").strip().lower()
        haslo = f.get("haslo", "").strip()
        konto = sedzia.uzytkownik

        if email:
            if konto:
                if konto.email != email:
                    zajety = Uzytkownik.query.filter_by(email=email).first()
                    if zajety:
                        flash("Ten email jest już zajęty.", "danger")
                        return redirect(url_for("sedziowie.edytuj", sid=sid))
                    konto.email = email
                if haslo:
                    konto.haslo_hash = generate_password_hash(haslo)
            else:
                if not haslo:
                    flash("Podaj hasło aby utworzyć konto.", "warning")
                    return redirect(url_for("sedziowie.edytuj", sid=sid))
                zajety = Uzytkownik.query.filter_by(email=email).first()
                if zajety:
                    flash("Ten email jest już zajęty.", "danger")
                    return redirect(url_for("sedziowie.edytuj", sid=sid))
                konto = Uzytkownik(
                    email=email,
                    haslo_hash=generate_password_hash(haslo),
                    rola="sedzia",
                    aktywny=True,
                    sedzia_id=sedzia.id,
                )
                db.session.add(konto)
        else:
            if konto and haslo:
                konto.haslo_hash = generate_password_hash(haslo)

        db.session.commit()
        flash("Dane sędziego zostały zaktualizowane.", "success")
        return redirect(url_for("sedziowie.lista"))

    return render_template("sedziowie/formularz.html", sedzia=sedzia)


@bp.route("/<int:sid>/usun", methods=["POST"])
@login_required
def usun(sid):
    sedzia = db.session.get(Sedzia, sid)
    if not sedzia:
        flash("Nie znaleziono sędziego.", "danger")
        return redirect(url_for("sedziowie.lista"))
    db.session.delete(sedzia)
    db.session.commit()
    flash("Sędzia został usunięty.", "success")
    return redirect(url_for("sedziowie.lista"))
