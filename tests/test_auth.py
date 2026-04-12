import pytest
from app.models import Uzytkownik
from werkzeug.security import generate_password_hash

def test_login_logout(client, db_session):
    # Create a user
    user = Uzytkownik(email="test@example.com", rola="sedzia")
    user.haslo_hash = generate_password_hash("password")
    db_session.add(user)
    db_session.commit()

    # Test login
    response = client.post("/auth/login", data={
        "email": "test@example.com",
        "haslo": "password"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Zalogowano pomy\xc5\x9blnie" in response.data or b"Dashboard" in response.data

    # Test logout
    response = client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Wylogowano" in response.data or b"Zaloguj si\xc4\x99" in response.data

def test_login_invalid_credentials(client, db_session):
    response = client.post("/auth/login", data={
        "email": "wrong@example.com",
        "haslo": "wrong"
    }, follow_redirects=True)
    assert b"Nieprawid\xc5\x82owy email lub has\xc5\x82o" in response.data
