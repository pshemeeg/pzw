from datetime import date, time
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required

from app.blueprints.zawody import bp
from app.extensions import db
from app.models import Zawody, Dyscyplina, Lowisko, Sedzia, Uczestnik, Zawodnik


def parse_date(s):
    """Konwertuje string 'YYYY-MM-DD' na obiekt date lub None."""
    try:
        return date.fromisoformat(s) if s else None
    except ValueError:
        return None


def parse_time(s):
    """Konwertuje string 'HH:MM' na obiekt time lub None."""
    try:
        return time.fromisoformat(s) if s else None
    except ValueError:
        return None


def zawody_z_formularza(d, zawody=None):
    """Wypełnia obiekt Zawody danymi z formularza. Tworzy nowy jeśli None."""
    if zawody is None:
        zawody = Zawody()
    zawody.nazwa = d["nazwa"].strip()
    zawody.data = parse_date(d.get("data"))
    zawody.dyscyplina_id = int(d["dyscyplina_id"])
    zawody.lowisko_id = int(d["lowisko_id"]) if d.get("lowisko_id") else None
    zawody.organizator_id = (
        int(d["organizator_id"]) if d.get("organizator_id") else None
    )
    zawody.godzina_start = parse_time(d.get("godzina_start"))
    zawody.godzina_koniec = parse_time(d.get("godzina_koniec"))
    zawody.kategoria = d.get("kategoria", "").strip()
    zawody.rejon = d.get("rejon", "").strip()
    zawody.liczba_sektorow = int(d.get("liczba_sektorow", 1))
    zawody.liczba_tur = int(d.get("liczba_tur", 1))
    zawody.grand_prix = bool(d.get("grand_prix"))
    zawody.klasyfikacja_druzynowa = bool(d.get("klasyfikacja_druzynowa"))
    zawody.status = d.get("status", "planowane")
    zawody.uwagi = d.get("uwagi", "").strip()
    return zawody


def get_slowniki():
    """Pobiera dane do list rozwijanych w formularzu."""
    return {
        "dyscypliny": Dyscyplina.query.order_by(Dyscyplina.nazwa).all(),
        "lowiska": Lowisko.query.order_by(Lowisko.nazwa).all(),
        "sedziowie": Sedzia.query.order_by(Sedzia.nazwisko).all(),
    }


@bp.route("/")
@login_required
def lista():
    status = request.args.get("status", "")
    q = request.args.get("q", "")

    query = Zawody.query.order_by(Zawody.data.desc())

    if status:
        query = query.filter_by(status=status)
    if q:
        query = query.filter(Zawody.nazwa.ilike(f"%{q}%"))

    zawody = query.all()
    return render_template(
        "zawody/lista.html",
        zawody=zawody,
        status=status,
        q=q,
    )


@bp.route("/nowe", methods=["GET", "POST"])
@login_required
def nowe():
    if request.method == "POST":
        zawody = zawody_z_formularza(request.form)
        db.session.add(zawody)
        db.session.commit()
        flash("Zawody zostały utworzone.", "success")
        return redirect(url_for("zawody.lista"))

    return render_template("zawody/formularz.html", zawody=None, **get_slowniki())


@bp.route("/<int:zid>")
@login_required
def szczegoly(zid):
    zawody = db.session.get(Zawody, zid) or db.session.get(Zawody, zid)
    if not zawody:
        flash("Nie znaleziono zawodów.", "danger")
        return redirect(url_for("zawody.lista"))
    return render_template("zawody/szczegoly.html", zawody=zawody)


@bp.route("/<int:zid>/edytuj", methods=["GET", "POST"])
@login_required
def edytuj(zid):
    zawody = db.session.get(Zawody, zid)
    if not zawody:
        flash("Nie znaleziono zawodów.", "danger")
        return redirect(url_for("zawody.lista"))

    if request.method == "POST":
        zawody_z_formularza(request.form, zawody)
        db.session.commit()
        flash("Zawody zostały zaktualizowane.", "success")
        return redirect(url_for("zawody.szczegoly", zid=zid))

    return render_template("zawody/formularz.html", zawody=zawody, **get_slowniki())


@bp.route("/<int:zid>/usun", methods=["POST"])
@login_required
def usun(zid):
    zawody = db.session.get(Zawody, zid)
    if not zawody:
        flash("Nie znaleziono zawodów.", "danger")
        return redirect(url_for("zawody.lista"))
    db.session.delete(zawody)
    db.session.commit()
    flash("Zawody zostały usunięte.", "success")
    return redirect(url_for("zawody.lista"))


@bp.route("/<int:zid>/uczestnicy/dodaj", methods=["POST"])
@login_required
def uczestnik_dodaj(zid):
    zawody = db.session.get(Zawody, zid)
    if not zawody:
        flash("Nie znaleziono zawodów.", "danger")
        return redirect(url_for("zawody.lista"))

    zawodnik_id = request.form.get("zawodnik_id")
    if not zawodnik_id:
        flash("Nie wybrano zawodnika.", "danger")
        return redirect(url_for("zawody.szczegoly", zid=zid))

    istniejacy = Uczestnik.query.filter_by(
        zawody_id=zid,
        zawodnik_id=int(zawodnik_id),
    ).first()
    if istniejacy:
        flash("Ten zawodnik jest już zapisany na te zawody.", "warning")
        return redirect(url_for("zawody.szczegoly", zid=zid))

    max_nr = (
        db.session.query(db.func.coalesce(db.func.max(Uczestnik.numer_startowy), 0))
        .filter_by(zawody_id=zid)
        .scalar()
    )

    uczestnik = Uczestnik(
        zawody_id=zid,
        zawodnik_id=int(zawodnik_id),
        druzyna=request.form.get("druzyna", "").strip() or None,
        numer_startowy=max_nr + 1,
    )
    db.session.add(uczestnik)
    db.session.commit()
    flash("Zawodnik został dodany do zawodów.", "success")
    return redirect(url_for("zawody.szczegoly", zid=zid))


@bp.route("/<int:zid>/uczestnicy/<int:uid>/usun", methods=["POST"])
@login_required
def uczestnik_usun(zid, uid):
    uczestnik = db.session.get(Uczestnik, uid)
    if not uczestnik or uczestnik.zawody_id != zid:
        flash("Nie znaleziono uczestnika.", "danger")
        return redirect(url_for("zawody.szczegoly", zid=zid))
    db.session.delete(uczestnik)
    db.session.commit()
    flash("Zawodnik został usunięty z zawodów.", "success")
    return redirect(url_for("zawody.szczegoly", zid=zid))


@bp.route("/<int:zid>/uczestnicy/<int:uid>/edytuj", methods=["POST"])
@login_required
def uczestnik_edytuj(zid, uid):
    uczestnik = db.session.get(Uczestnik, uid)
    if not uczestnik or uczestnik.zawody_id != zid:
        flash("Nie znaleziono uczestnika.", "danger")
        return redirect(url_for("zawody.szczegoly", zid=zid))
    uczestnik.druzyna = request.form.get("druzyna", "").strip() or None
    nr = request.form.get("numer_startowy", "").strip()
    if nr.isdigit():
        uczestnik.numer_startowy = int(nr)
    db.session.commit()
    return redirect(url_for("zawody.szczegoly", zid=zid))
