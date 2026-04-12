import pytest
from app.models import Zawodnik, Uczestnik, Zawody, Dyscyplina
from datetime import date

def test_delete_zawodnik_cascades_to_uczestnicy(client, db_session):
    # Setup
    d = Dyscyplina(nazwa="CascadeTest", kod="ctest", typ_wyniku="wagowy")
    db_session.add(d)
    db_session.commit()
    
    z = Zawodnik(imie="Jan", nazwisko="DoUsuniecia", kolo="K1")
    db_session.add(z)
    db_session.commit()
    
    comp = Zawody(nazwa="Zawody Testowe", data=date(2026, 1, 1), dyscyplina_id=d.id)
    db_session.add(comp)
    db_session.commit()
    
    u = Uczestnik(zawody_id=comp.id, zawodnik_id=z.id)
    db_session.add(u)
    db_session.commit()
    
    # Ensure participant exists
    assert Uczestnik.query.filter_by(zawodnik_id=z.id).count() == 1
    
    # Delete zawodnik
    from app.models import Uzytkownik
    admin = Uzytkownik.query.filter_by(rola="admin").first()
    client.post("/auth/login", data={"email": admin.email, "haslo": "admin"})
    
    response = client.post(f"/zawodnicy/{z.id}/usun", follow_redirects=True)
    assert response.status_code == 200
    
    # Verify zawodnik is gone
    assert db_session.get(Zawodnik, z.id) is None
    
    # Verify participant record is also gone (cascade worked)
    assert Uczestnik.query.filter_by(zawodnik_id=z.id).count() == 0
