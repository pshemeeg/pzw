from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.blueprints.profil import bp
from app.extensions import db
from app.models import Dyscyplina, Sedzia

@bp.route("/ustawienia", methods=["GET", "POST"])
@login_required
def ustawienia():
    if request.method == "POST":
        f = request.form
        
        # Przygotuj strukturę JSON
        nowe_ustawienia = {
            "domyslna_dyscyplina_id": f.get("domyslna_dyscyplina_id", type=int),
            "domyslna_liczba_sektorow": f.get("domyslna_liczba_sektorow", 1, type=int),
            "domyslna_liczba_tur": f.get("domyslna_liczba_tur", 1, type=int),
            "domyslny_sedzia_glowny_id": f.get("domyslny_sedzia_glowny_id", type=int),
            "domyslny_sedzia_sekretarz_id": f.get("domyslny_sedzia_sekretarz_id", type=int),
            "domyslna_kategoria": f.get("domyslna_kategoria", "").strip(),
            "domyslny_organizator_kolo": f.get("domyslny_organizator_kolo", "").strip(),
            "domyslne_lowisko_id": f.get("domyslne_lowisko_id", type=int),
        }
        
        current_user.ustawienia = nowe_ustawienia
        db.session.commit()
        flash("Ustawienia zostały zapisane.", "success")
        return redirect(url_for("profil.ustawienia"))

    dyscypliny = Dyscyplina.query.order_by(Dyscyplina.nazwa).all()
    sedziowie = Sedzia.query.order_by(Sedzia.nazwisko).all()
    
    # Pobierz obecne ustawienia lub zainicjuj pustym słownikiem
    u = current_user.ustawienia or {}
    
    return render_template(
        "profil/ustawienia.html", 
        dyscypliny=dyscypliny, 
        sedziowie=sedziowie,
        u=u
    )
