from flask import request, redirect, url_for, flash, abort
from flask_login import login_required
from app.extensions import db
from app.models import Stanowisko, WynikWagowy, WynikKarpie, WynikRyba
from app.blueprints.wyniki import bp
from app.blueprints.wyniki.scoring import oblicz_punkty_ryby

@bp.route('/stanowisko/<int:sid>/wagowy', methods=['POST'])
@login_required
def zapisz_wagowy(sid):
    stanowisko = db.session.get(Stanowisko, sid)
    if not stanowisko:
        abort(404)

    waga_g = request.form.get('waga_g', type=int)
    dyskwalifikacja = request.form.get('dyskwalifikacja') == 'on'
    uwagi = request.form.get('uwagi')

    if waga_g is None:
        flash('Nieprawidłowa waga.', 'danger')
        return redirect(url_for('zawody.szczegoly', zid=stanowisko.zawody_id))

    wynik = stanowisko.wynik_wagowy
    if not wynik:
        wynik = WynikWagowy(stanowisko_id=sid)
        db.session.add(wynik)

    wynik.waga_g = waga_g
    wynik.dyskwalifikacja = dyskwalifikacja
    wynik.uwagi = uwagi

    db.session.commit()
    flash('Zapisano wynik wagowy.', 'success')
    return redirect(url_for('zawody.szczegoly', zid=stanowisko.zawody_id))

@bp.route('/stanowisko/<int:sid>/karpie', methods=['POST'])
@login_required
def zapisz_karpie(sid):
    stanowisko = db.session.get(Stanowisko, sid)
    if not stanowisko:
        abort(404)

    liczba_sztuk = request.form.get('liczba_sztuk', type=int)
    waga_g = request.form.get('waga_g', type=int)
    najciezsza_g = request.form.get('najciezsza_g', type=int)
    punkty_karne = request.form.get('punkty_karne', type=int, default=0)
    uwagi = request.form.get('uwagi')

    if None in [liczba_sztuk, waga_g, najciezsza_g]:
        flash('Wypełnij wszystkie wymagane pola.', 'danger')
        return redirect(url_for('zawody.szczegoly', zid=stanowisko.zawody_id))

    wynik = stanowisko.wynik_karpie
    if not wynik:
        wynik = WynikKarpie(stanowisko_id=sid)
        db.session.add(wynik)

    wynik.liczba_sztuk = liczba_sztuk
    wynik.waga_g = waga_g
    wynik.najciezsza_g = najciezsza_g
    wynik.punkty_karne = punkty_karne
    wynik.uwagi = uwagi

    db.session.commit()
    flash('Zapisano wynik karpiowy.', 'success')
    return redirect(url_for('zawody.szczegoly', zid=stanowisko.zawody_id))

@bp.route('/stanowisko/<int:sid>/ryby', methods=['POST'])
@login_required
def zapisz_ryby(sid):
    stanowisko = db.session.get(Stanowisko, sid)
    if not stanowisko:
        abort(404)

    gatunki = request.form.getlist('gatunek[]')
    dlugosci = request.form.getlist('dlugosc_mm[]')

    # Usuwamy stare ryby
    for r in stanowisko.wyniki_ryby:
        db.session.delete(r)

    # Dodajemy nowe
    for gat, dl in zip(gatunki, dlugosci):
        gat = gat.strip()
        if not gat or not dl:
            continue
        try:
            dl_mm = int(dl)
        except ValueError:
            continue

        punkty, zaliczona = oblicz_punkty_ryby(gat, dl_mm)
        nowa_ryba = WynikRyba(
            stanowisko_id=sid,
            gatunek=gat,
            dlugosc_mm=dl_mm,
            punkty=punkty,
            zaliczona=zaliczona
        )
        db.session.add(nowa_ryba)

    db.session.commit()
    flash('Zapisano ryby stanowiska.', 'success')
    return redirect(url_for('zawody.szczegoly', zid=stanowisko.zawody_id))
