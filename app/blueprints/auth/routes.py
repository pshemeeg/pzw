from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

from app.blueprints.auth import bp
from app.models import Uzytkownik


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        haslo = request.form.get("haslo", "")

        uzytkownik = Uzytkownik.query.filter_by(email=email).first()

        if uzytkownik is None or not check_password_hash(uzytkownik.haslo_hash, haslo):
            flash("Nieprawidłowy email lub hasło.", "danger")
            return redirect(url_for("auth.login"))

        if not uzytkownik.aktywny:
            flash("Konto jest nieaktywne. Skontaktuj się z administratorem.", "warning")
            return redirect(url_for("auth.login"))

        login_user(uzytkownik)
        next_page = request.args.get("next")
        return redirect(next_page or url_for("main.index"))

    return render_template("auth/login.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Wylogowano pomyślnie.", "success")
    return redirect(url_for("auth.login"))
