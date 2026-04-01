from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from app.blueprints.uzytkownicy import bp
from app.extensions import db
from app.models import Uzytkownik


def tylko_admin():
    if not current_user.is_admin():
        abort(403)


@bp.route("/")
@login_required
def lista():
    tylko_admin()
    uzytkownicy = Uzytkownik.query.order_by(Uzytkownik.email).all()
    return render_template("uzytkownicy/lista.html", uzytkownicy=uzytkownicy)


@bp.route("/<int:uid>/edytuj", methods=["GET", "POST"])
@login_required
def edytuj(uid):
    tylko_admin()
    uzytkownik = db.session.get(Uzytkownik, uid)
    if not uzytkownik:
        flash("Nie znaleziono użytkownika.", "danger")
        return redirect(url_for("uzytkownicy.lista"))

    if request.method == "POST":
        f = request.form
        nowy_email = f["email"].strip().lower()

        istniejacy = Uzytkownik.query.filter_by(email=nowy_email).first()
        if istniejacy and istniejacy.id != uid:
            flash("Ten email jest już zajęty.", "danger")
            return redirect(url_for("uzytkownicy.edytuj", uid=uid))

        uzytkownik.email = nowy_email
        uzytkownik.rola = f.get("rola", "sedzia")
        uzytkownik.aktywny = bool(f.get("aktywny"))

        haslo = f.get("haslo", "").strip()
        if haslo:
            uzytkownik.haslo_hash = generate_password_hash(haslo)

        db.session.commit()
        flash("Użytkownik został zaktualizowany.", "success")
        return redirect(url_for("uzytkownicy.lista"))

    return render_template("uzytkownicy/formularz.html", uzytkownik=uzytkownik)


@bp.route("/<int:uid>/usun", methods=["POST"])
@login_required
def usun(uid):
    tylko_admin()
    if uid == current_user.id:
        flash("Nie możesz usunąć własnego konta.", "danger")
        return redirect(url_for("uzytkownicy.lista"))
    uzytkownik = db.session.get(Uzytkownik, uid)
    if not uzytkownik:
        flash("Nie znaleziono użytkownika.", "danger")
        return redirect(url_for("uzytkownicy.lista"))
    db.session.delete(uzytkownik)
    db.session.commit()
    flash("Użytkownik został usunięty.", "success")
    return redirect(url_for("uzytkownicy.lista"))
