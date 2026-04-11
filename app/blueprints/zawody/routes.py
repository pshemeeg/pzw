from datetime import date, time
from flask import render_template, redirect, url_for, request, flash, abort
from flask_login import login_required
import random
from app.blueprints.zawody import bp
from app.extensions import db
from app.models import (
    Zawody,
    Dyscyplina,
    Lowisko,
    Sedzia,
    Uczestnik,
    Zawodnik,
    Stanowisko,
)


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
    zawody.nr_zawodow = d.get("nr_zawodow", "").strip() or None
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


from app.blueprints.zawody.helpers import oblicz_klasyfikacje

@bp.route("/<int:zid>/protokol")
@login_required
def protokol(zid):
    zawody = db.session.get(Zawody, zid)
    if not zawody:
        abort(404)
        
    klasyfikacja = oblicz_klasyfikacje(zawody)
    
    return render_template(
        "zawody/protokol.html",
        zawody=zawody,
        klasyfikacja=klasyfikacja,
    )

@bp.route("/<int:zid>")
@login_required
def szczegoly(zid):
    zawody = db.session.get(Zawody, zid)
    if not zawody:
        flash("Nie znaleziono zawodów.", "danger")
        return redirect(url_for("zawody.lista"))

    druzyny = []
    if zawody.klasyfikacja_druzynowa:
        druzyny = [
            r[0]
            for r in db.session.query(Uczestnik.druzyna)
            .filter(
                Uczestnik.zawody_id == zid,
                Uczestnik.druzyna.isnot(None),
            )
            .distinct()
            .order_by(Uczestnik.druzyna)
            .all()
        ]

    klasyfikacja = oblicz_klasyfikacje(zawody)

    return render_template(
        "zawody/szczegoly.html",
        zawody=zawody,
        druzyny=druzyny,
        klasyfikacja=klasyfikacja,
    )


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

    druzyna = request.form.get("druzyna", "").strip() or None

    if zawody.klasyfikacja_druzynowa:
        if not druzyna:
            flash(
                "W zawodach drużynowych każdy zawodnik musi mieć przypisaną drużynę.",
                "danger",
            )
            return redirect(url_for("zawody.szczegoly", zid=zid))
        liczba_w_druzynie = Uczestnik.query.filter_by(
            zawody_id=zid,
            druzyna=druzyna,
        ).count()
        if liczba_w_druzynie >= 3:
            flash(
                f"Drużyna '{druzyna}' ma już 3 zawodników — jest kompletna.", "warning"
            )
            return redirect(url_for("zawody.szczegoly", zid=zid))

    max_nr = (
        db.session.query(db.func.coalesce(db.func.max(Uczestnik.numer_startowy), 0))
        .filter_by(zawody_id=zid)
        .scalar()
    )

    uczestnik = Uczestnik(
        zawody_id=zid,
        zawodnik_id=int(zawodnik_id),
        druzyna=druzyna,
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


@bp.route("/<int:zid>/losuj", methods=["POST"])
@login_required
def losuj(zid):
    zawody = db.session.get(Zawody, zid)
    if not zawody:
        flash("Nie znaleziono zawodów.", "danger")
        return redirect(url_for("zawody.lista"))

    tura = int(request.form.get("tura", 1))
    tryb = request.form.get("tryb", "auto")

    uczestnicy = (
        Uczestnik.query.filter_by(zawody_id=zid)
        .order_by(Uczestnik.numer_startowy)
        .all()
    )

    if not uczestnicy:
        flash("Brak uczestników — dodaj zawodników przed losowaniem.", "warning")
        return redirect(url_for("zawody.szczegoly", zid=zid))

    n = len(uczestnicy)
    k = zawody.liczba_sektorow
    sektory = [chr(65 + i) for i in range(k)]

    if tryb == "auto":
        losowi = list(uczestnicy)
        random.shuffle(losowi)
        base = n // k
        extra = n % k
        sizes = {s: base + (1 if i < extra else 0) for i, s in enumerate(sektory)}
        nowe = []
        idx = 0
        for sek in sektory:
            for pos in range(1, sizes[sek] + 1):
                if idx < len(losowi):
                    nowe.append((losowi[idx].id, tura, sek, pos))
                    idx += 1

    elif tryb == "druzynowe":
        druzyny = {}
        bez_druzyny = []
        for u in uczestnicy:
            d = (u.druzyna or "").strip()
            if d:
                druzyny.setdefault(d, []).append(u)
            else:
                bez_druzyny.append(u)

        if bez_druzyny:
            names = ", ".join(
                u.zawodnik.imie + " " + u.zawodnik.nazwisko for u in bez_druzyny
            )
            flash(f"Zawodnicy bez drużyny: {names}", "danger")
            return redirect(url_for("zawody.szczegoly", zid=zid))

        for nazwa, czlonkowie in druzyny.items():
            if len(czlonkowie) != k:
                flash(
                    f"Drużyna '{nazwa}' ma {len(czlonkowie)} zawodników "
                    f"(wymagane {k} — tyle ile sektorów).",
                    "danger",
                )
                return redirect(url_for("zawody.szczegoly", zid=zid))

        lista_druzyn = list(druzyny.items())
        random.shuffle(lista_druzyn)
        sektor_kolejka = {s: [] for s in sektory}

        for nazwa, czlonkowie in lista_druzyn:
            shuffled = list(czlonkowie)
            random.shuffle(shuffled)
            for s_idx, uczestnik in enumerate(shuffled):
                sektor_kolejka[sektory[s_idx]].append(uczestnik.id)

        nowe = []
        for sek in sektory:
            kolejka = sektor_kolejka[sek]
            random.shuffle(kolejka)
            for pos, uid in enumerate(kolejka, start=1):
                nowe.append((uid, tura, sek, pos))

    else:
        flash("Nieznany tryb losowania.", "danger")
        return redirect(url_for("zawody.szczegoly", zid=zid))

    Stanowisko.query.filter_by(zawody_id=zid, tura=tura).delete()

    for uczestnik_id, t, sek, pos in nowe:
        stan = Stanowisko(
            zawody_id=zid,
            uczestnik_id=uczestnik_id,
            tura=t,
            sektor=sek,
            numer=pos,
        )
        db.session.add(stan)

    db.session.commit()
    flash(
        f"Losowanie tury {tura} zakończone — przydzielono {len(nowe)} stanowisk.",
        "success",
    )
    return redirect(url_for("zawody.szczegoly", zid=zid) + "#stanowiska")


@bp.route("/<int:zid>/stanowiska_recznie", methods=["POST"])
@login_required
def stanowiska_recznie(zid):
    zawody = db.session.get(Zawody, zid)
    if not zawody:
        flash("Nie znaleziono zawodów.", "danger")
        return redirect(url_for("zawody.lista"))

    tura = int(request.form.get("tura", 1))
    
    uczestnicy = Uczestnik.query.filter_by(zawody_id=zid).all()
    obecne_stanowiska = Stanowisko.query.filter_by(zawody_id=zid, tura=tura).all()
    stan_dict = {s.uczestnik_id: s for s in obecne_stanowiska}

    # Tymczasowe "odsunięcie" obecnych stanowisk, aby uniknąć konfliktów UniqueConstraint
    # podczas zamiany miejsc (swap) w bazie, np. SQLite.
    for s in obecne_stanowiska:
        s.tura += 10000
    db.session.flush()

    count = 0
    zajete_stanowiska = set()
    bledy = []

    for u in uczestnicy:
        sek = request.form.get(f"sektor_{tura}_{u.id}")
        nr = request.form.get(f"numer_{tura}_{u.id}")
        
        stan = stan_dict.get(u.id)

        if sek and sek.strip() and nr and nr.strip():
            try:
                nr_int = int(nr)
                if nr_int <= 0:
                    bledy.append(f"Nieprawidłowy numer stanowiska ({nr_int}) dla zawodnika {u.zawodnik.nazwisko}.")
                    continue

                sek_str = sek.strip().upper()
                klucz = (sek_str, nr_int)
                if klucz in zajete_stanowiska:
                    bledy.append(f"Stanowisko {sek_str}{nr_int} zostało przypisane więcej niż raz.")
                    continue
                
                zajete_stanowiska.add(klucz)

                if stan:
                    stan.sektor = sek_str
                    stan.numer = nr_int
                    stan.tura = tura  # Przywracamy poprawną turę
                else:
                    stan = Stanowisko(
                        zawody_id=zid,
                        uczestnik_id=u.id,
                        tura=tura,
                        sektor=sek_str,
                        numer=nr_int,
                    )
                    db.session.add(stan)
                count += 1
            except ValueError:
                pass
        else:
            if stan:
                db.session.delete(stan)

    if bledy:
        db.session.rollback()
        for b in set(bledy):
            flash(b, "danger")
        return redirect(url_for("zawody.szczegoly", zid=zid) + "#stanowiska")

    db.session.commit()
    flash(f"Zapisano ręczne przypisanie stanowisk (Tura {tura}, {count} stanowisk).", "success")
    return redirect(url_for("zawody.szczegoly", zid=zid) + "#stanowiska")
