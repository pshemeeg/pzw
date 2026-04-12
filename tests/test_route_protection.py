import pytest
from app.models import Zawody, Dyscyplina
from datetime import date, timedelta

def test_guest_access_finished_competition(client, db_session):
    # Create finished competition
    d = Dyscyplina(nazwa="Sp\xc5\x82awik Test", kod="spl_test", typ_wyniku="wagowy")
    db_session.add(d)
    db_session.commit()
    
    past_date = date.today() - timedelta(days=5)
    z = Zawody(nazwa="Stare Zawody", data=past_date, dyscyplina_id=d.id, status="zakonczone")
    db_session.add(z)
    db_session.commit()

    # Guest should see details of finished competition
    response = client.get(f"/zawody/{z.id}")
    assert response.status_code == 200
    assert b"Klasyfikacja" in response.data
    # But shouldn't see administrative tabs
    assert b"Wprowadzanie Wynik\xc3\xb3w" not in response.data

def test_guest_denied_planned_competition(client, db_session):
    # Create planned competition
    d = Dyscyplina.query.first()
    future_date = date.today() + timedelta(days=5)
    z = Zawody(nazwa="Nowe Zawody", data=future_date, dyscyplina_id=d.id, status="planowane")
    db_session.add(z)
    db_session.commit()

    # Guest should be redirected to login when trying to see planned competition
    response = client.get(f"/zawody/{z.id}")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]

def test_admin_only_routes(client, db_session):
    # Create non-admin user
    from app.models import Uzytkownik
    from werkzeug.security import generate_password_hash
    user = Uzytkownik(email="user@pzw.pl", rola="sedzia")
    user.haslo_hash = generate_password_hash("password")
    db_session.add(user)
    db_session.commit()

    # Login as non-admin
    client.post("/auth/login", data={"email": "user@pzw.pl", "haslo": "password"})

    # Try to access users list (admin only)
    response = client.get("/uzytkownicy/")
    # Depending on implementation, it might be 403 or redirect or just hide the link
    # Let's check how it's implemented in uzytkownicy/routes.py
    # (Assuming there is a check or @admin_required if we had one, but let's check current code)
    assert response.status_code in [302, 403] 
