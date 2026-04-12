from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask import jsonify
from app.blueprints.zawodnicy import bp
from app.extensions import db
from app.models import Zawodnik


@bp.route("/")
@login_required
def lista():
    q = request.args.get("q", "").strip()
    kolo = request.args.get("kolo", "").strip()

    query = Zawodnik.query.order_by(Zawodnik.nazwisko, Zawodnik.imie)

    if q:
        query = query.filter(
            db.or_(
                Zawodnik.imie.ilike(f"%{q}%"),
                Zawodnik.nazwisko.ilike(f"%{q}%"),
            )
        )
    if kolo:
        query = query.filter(Zawodnik.kolo.ilike(f"%{kolo}%"))

    zawodnicy = query.all()

    kola = db.session.query(Zawodnik.kolo).distinct().order_by(Zawodnik.kolo).all()
    kola = [k[0] for k in kola if k[0]]

    return render_template(
        "zawodnicy/lista.html",
        zawodnicy=zawodnicy,
        q=q,
        kolo=kolo,
        kola=kola,
    )


@bp.route("/nowy", methods=["GET", "POST"])
@login_required
def nowy():
    if request.method == "POST":
        f = request.form
        imie = f["imie"].strip()
        nazwisko = f["nazwisko"].strip()
        kolo = f["kolo"].strip()

        istniejacy = Zawodnik.query.filter_by(
            imie=imie, nazwisko=nazwisko, kolo=kolo
        ).first()
        if istniejacy:
            flash(
                f"{imie} {nazwisko} z koła '{kolo}' już istnieje w bazie.",
                "warning",
            )
            return redirect(url_for("zawodnicy.szczegoly", zid=istniejacy.id))

        nr_lic = f.get("nr_licencji", "").strip()
        if not nr_lic or nr_lic.lower() == "none":
            nr_lic = None

        zawodnik = Zawodnik(
            imie=imie,
            nazwisko=nazwisko,
            kolo=kolo,
            nr_licencji=nr_lic,
            rodo_zgoda=bool(f.get("rodo_zgoda")),
        )
        db.session.add(zawodnik)
        db.session.commit()
        flash("Zawodnik został dodany.", "success")
        return redirect(url_for("zawodnicy.lista"))

    return render_template("zawodnicy/formularz.html", zawodnik=None)


import csv
import io

@bp.route("/import", methods=["POST"])
@login_required
def import_csv():
    if "file" not in request.files:
        flash("Brak pliku w żądaniu.", "danger")
        return redirect(url_for("zawodnicy.lista"))
    
    file = request.files["file"]
    if file.filename == "":
        flash("Nie wybrano pliku.", "danger")
        return redirect(url_for("zawodnicy.lista"))

    if not file.filename.endswith(".csv"):
        flash("Plik musi mieć rozszerzenie .csv", "danger")
        return redirect(url_for("zawodnicy.lista"))

    try:
        stream = io.StringIO(file.stream.read().decode("utf-8"), newline="")
        reader = csv.DictReader(stream)
        
        dodano = 0
        pominieto = 0
        
        for row in reader:
            imie = row.get("imie", "").strip()
            nazwisko = row.get("nazwisko", "").strip()
            kolo = row.get("kolo", "").strip()
            nr_licencji = row.get("nr_licencji", "").strip()
            if not nr_licencji or nr_licencji.lower() == "none":
                nr_licencji = None
            # Default to False for safety if not specified
            rodo_zgoda = row.get("rodo_zgoda", "0").strip().lower() in ["1", "true", "tak", "yes"]
            
            if not imie or not nazwisko or not kolo:
                pominieto += 1
                continue
                
            istniejacy = Zawodnik.query.filter_by(imie=imie, nazwisko=nazwisko, kolo=kolo).first()
            if istniejacy:
                pominieto += 1
                continue
                
            nowy = Zawodnik(imie=imie, nazwisko=nazwisko, kolo=kolo, nr_licencji=nr_licencji, rodo_zgoda=rodo_zgoda)
            db.session.add(nowy)
            dodano += 1
            
        db.session.commit()
        flash(f"Import zakończony. Dodano: {dodano}, Pominięto (duplikaty/błędy): {pominieto}.", "success")
        
    except Exception as e:
        db.session.rollback()
        flash(f"Błąd podczas przetwarzania pliku CSV: {str(e)}", "danger")

    return redirect(url_for("zawodnicy.lista"))

@bp.route("/<int:zid>")
@login_required
def szczegoly(zid):
    zawodnik = db.session.get(Zawodnik, zid)
    if not zawodnik:
        flash("Nie znaleziono zawodnika.", "danger")
        return redirect(url_for("zawodnicy.lista"))
    return render_template("zawodnicy/szczegoly.html", zawodnik=zawodnik)


@bp.route("/<int:zid>/edytuj", methods=["GET", "POST"])
@login_required
def edytuj(zid):
    zawodnik = db.session.get(Zawodnik, zid)
    if not zawodnik:
        flash("Nie znaleziono zawodnika.", "danger")
        return redirect(url_for("zawodnicy.lista"))

    if request.method == "POST":
        f = request.form
        imie = f["imie"].strip()
        nazwisko = f["nazwisko"].strip()
        kolo = f["kolo"].strip()

        duplikat = Zawodnik.query.filter(
            Zawodnik.imie == imie,
            Zawodnik.nazwisko == nazwisko,
            Zawodnik.kolo == kolo,
            Zawodnik.id != zid,
        ).first()
        if duplikat:
            flash(
                f"{imie} {nazwisko} z koła '{kolo}' już istnieje w bazie.",
                "warning",
            )
            return redirect(url_for("zawodnicy.edytuj", zid=zid))

        zawodnik.imie = imie
        zawodnik.nazwisko = nazwisko
        zawodnik.kolo = kolo
        
        nr_lic = f.get("nr_licencji", "").strip()
        if not nr_lic or nr_lic.lower() == "none":
            nr_lic = None
        zawodnik.nr_licencji = nr_lic
        
        zawodnik.rodo_zgoda = bool(f.get("rodo_zgoda"))
        db.session.commit()
        flash("Dane zawodnika zostały zaktualizowane.", "success")
        return redirect(url_for("zawodnicy.szczegoly", zid=zid))

    return render_template("zawodnicy/formularz.html", zawodnik=zawodnik)


@bp.route("/<int:zid>/usun", methods=["POST"])
@login_required
def usun(zid):
    zawodnik = db.session.get(Zawodnik, zid)
    if not zawodnik:
        flash("Nie znaleziono zawodnika.", "danger")
        return redirect(url_for("zawodnicy.lista"))
    db.session.delete(zawodnik)
    db.session.commit()
    flash("Zawodnik został usunięty.", "success")
    return redirect(url_for("zawodnicy.lista"))


@bp.route("/szukaj")
@login_required
def szukaj():
    q = request.args.get("q", "").strip()
    if len(q) < 2:
        return jsonify([])
    zawodnicy = (
        Zawodnik.query.filter(
            db.or_(
                Zawodnik.imie.ilike(f"%{q}%"),
                Zawodnik.nazwisko.ilike(f"%{q}%"),
            )
        )
        .order_by(Zawodnik.nazwisko, Zawodnik.imie)
        .limit(10)
        .all()
    )
    return jsonify(
        [
            {
                "id": z.id,
                "imie": z.imie,
                "nazwisko": z.nazwisko,
                "kolo": z.kolo,
                "label": f"{z.nazwisko} {z.imie} — {z.kolo}",
            }
            for z in zawodnicy
        ]
    )
