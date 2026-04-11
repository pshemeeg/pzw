from flask import request, redirect, url_for, flash, abort
from flask_login import login_required
from app.extensions import db
from app.models import Stanowisko, WynikWagowy, WynikKarpie, WynikRyba, Zawody
from app.blueprints.wyniki import bp
from app.blueprints.wyniki.scoring import oblicz_punkty_ryby

@bp.route('/zawody/<int:zid>/tura/<int:tura>/wagowy', methods=['POST'])
@login_required
def zapisz_zbiorczo_wagowy(zid, tura):
    zawody = db.session.get(Zawody, zid)
    if not zawody:
        abort(404)
        
    stanowiska = Stanowisko.query.filter_by(zawody_id=zid, tura=tura).all()
    for s in stanowiska:
        waga_str = request.form.get(f'waga_{s.id}')
        dysk = request.form.get(f'dysk_{s.id}') == 'on'
        uwagi = request.form.get(f'uwagi_{s.id}')
        
        if waga_str and waga_str.strip():
            waga_g = int(waga_str)
            wynik = s.wynik_wagowy
            if not wynik:
                wynik = WynikWagowy(stanowisko_id=s.id)
                db.session.add(wynik)
            wynik.waga_g = waga_g
            wynik.dyskwalifikacja = dysk
            wynik.uwagi = uwagi
        else:
            # If waga is empty but it was previously set, we can either delete it or leave it.
            # Usually, clearing the field means removing the result.
            if s.wynik_wagowy:
                db.session.delete(s.wynik_wagowy)

    db.session.commit()
    flash(f'Zapisano zbiorczo wyniki wagowe (Tura {tura}).', 'success')
    return redirect(url_for('zawody.szczegoly', zid=zid) + '#wyniki')

@bp.route('/zawody/<int:zid>/tura/<int:tura>/karpie', methods=['POST'])
@login_required
def zapisz_zbiorczo_karpie(zid, tura):
    zawody = db.session.get(Zawody, zid)
    if not zawody:
        abort(404)

    stanowiska = Stanowisko.query.filter_by(zawody_id=zid, tura=tura).all()
    for s in stanowiska:
        sztuki_str = request.form.get(f'sztuki_{s.id}')
        waga_str = request.form.get(f'waga_{s.id}')
        naj_str = request.form.get(f'naj_{s.id}')
        karne_str = request.form.get(f'karne_{s.id}')
        uwagi = request.form.get(f'uwagi_{s.id}')

        if sztuki_str and waga_str and naj_str:
            wynik = s.wynik_karpie
            if not wynik:
                wynik = WynikKarpie(stanowisko_id=s.id)
                db.session.add(wynik)
            wynik.liczba_sztuk = int(sztuki_str)
            wynik.waga_g = int(waga_str)
            wynik.najciezsza_g = int(naj_str)
            wynik.punkty_karne = int(karne_str) if karne_str else 0
            wynik.uwagi = uwagi
        else:
            if s.wynik_karpie:
                db.session.delete(s.wynik_karpie)

    db.session.commit()
    flash(f'Zapisano zbiorczo wyniki karpiowe (Tura {tura}).', 'success')
    return redirect(url_for('zawody.szczegoly', zid=zid) + '#wyniki')

@bp.route('/zawody/<int:zid>/tura/<int:tura>/stanowisko/<int:sid>/punktowy', methods=['POST'])
@login_required
def zapisz_zbiorczo_punktowy(zid, tura, sid):
    stanowisko = db.session.get(Stanowisko, sid)
    if not stanowisko or stanowisko.zawody_id != zid:
        abort(404)

    gatunki = request.form.getlist('gatunek[]')
    dlugosci = request.form.getlist('dlugosc_mm[]')

    for r in stanowisko.wyniki_ryby:
        db.session.delete(r)

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
    flash(f'Zapisano ryby dla zawodnika {stanowisko.uczestnik.zawodnik.nazwisko}.', 'success')
    return redirect(url_for('zawody.szczegoly', zid=zid) + '#wyniki')
