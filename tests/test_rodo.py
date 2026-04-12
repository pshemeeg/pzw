import pytest
from app.models import Zawodnik, Uzytkownik

def test_zawodnik_rodo_display_name():
    z_yes = Zawodnik(id=1, imie="Jan", nazwisko="Kowalski", rodo_zgoda=True)
    z_no = Zawodnik(id=2, imie="Adam", nazwisko="Nowak", rodo_zgoda=False)

    # Logged in user sees everything
    assert z_yes.display_name(is_authenticated=True) == "Kowalski Jan"
    assert z_no.display_name(is_authenticated=True) == "Nowak Adam"

    # Guest sees only those with consent
    assert z_yes.display_name(is_authenticated=False) == "Kowalski Jan"
    assert z_no.display_name(is_authenticated=False) == "Zawodnik#2"

def test_rodo_anonymization_on_page(client, db_session):
    from app.models import Dyscyplina, Zawody, Uczestnik
    from datetime import date
    
    # Setup
    d = Dyscyplina(nazwa="Test", kod="test", typ_wyniku="wagowy")
    db_session.add(d)
    db_session.commit()
    
    z_no = Zawodnik(imie="Tajny", nazwisko="Zawodnik", kolo="K1", rodo_zgoda=False)
    db_session.add(z_no)
    db_session.commit()
    
    comp = Zawody(nazwa="Publiczne", data=date(2020, 1, 1), dyscyplina_id=d.id, status="zakonczone")
    db_session.add(comp)
    db_session.commit()
    
    db_session.add(Uczestnik(zawody_id=comp.id, zawodnik_id=z_no.id))
    db_session.commit()
    
    # Guest view
    response = client.get(f"/zawody/{comp.id}")
    assert response.status_code == 200
    assert b"Zawodnik Tajny" not in response.data
    assert f"Zawodnik#{z_no.id}".encode() in response.data
    
    # Admin view
    admin = Uzytkownik.query.filter_by(rola="admin").first()
    client.post("/auth/login", data={"email": admin.email, "haslo": "admin"})
    response = client.get(f"/zawody/{comp.id}")
    assert b"Zawodnik Tajny" in response.data
