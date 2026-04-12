from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.blueprints.cms import bp
from app.extensions import db
from app.models import Dokument

@bp.route("/<string:kod>")
def view(kod):
    dokument = Dokument.query.filter_by(kod=kod).first()
    if not dokument:
        if current_user.is_authenticated and current_user.is_admin():
            # Auto-create if admin visits non-existent but expected page
            if kod in ['regulamin', 'polityka', 'dokumentacja', 'szablony']:
                tytuly = {
                    'regulamin': 'Regulamin Systemu',
                    'polityka': 'Polityka Prywatności',
                    'dokumentacja': 'Dokumentacja i Pomoc',
                    'szablony': 'Szablony Dokumentów'
                }
                dokument = Dokument(kod=kod, tytul=tytuly[kod], tresc='Treść w przygotowaniu...')
                db.session.add(dokument)
                db.session.commit()
            else:
                abort(404)
        else:
            abort(404)
    
    return render_template("cms/view.html", dokument=dokument)

@bp.route("/<string:kod>/edytuj", methods=["GET", "POST"])
@login_required
def edytuj(kod):
    if not current_user.is_admin():
        abort(403)
        
    dokument = Dokument.query.filter_by(kod=kod).first()
    if not dokument:
        abort(404)
        
    if request.method == "POST":
        dokument.tytul = request.form.get("tytul")
        dokument.tresc = request.form.get("tresc")
        db.session.commit()
        flash(f"Dokument '{dokument.tytul}' został zaktualizowany.", "success")
        return redirect(url_for("cms.view", kod=kod))
        
    return render_template("cms/formularz.html", dokument=dokument)
