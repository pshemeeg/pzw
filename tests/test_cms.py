import pytest
from app.models import Dokument, Uzytkownik

def test_cms_auto_create_for_admin(client, db_session):
    # Setup admin
    admin = Uzytkownik.query.filter_by(rola="admin").first()
    client.post("/auth/login", data={"email": admin.email, "haslo": "admin"})

    # Access non-existent but expected page
    response = client.get("/strony/regulamin")
    assert response.status_code == 200
    assert b"Regulamin Systemu" in response.data
    
    # Check DB
    doc = Dokument.query.filter_by(kod="regulamin").first()
    assert doc is not None
    assert doc.tytul == "Regulamin Systemu"

def test_cms_edit_document(client, db_session):
    # Setup admin
    admin = Uzytkownik.query.filter_by(rola="admin").first()
    client.post("/auth/login", data={"email": admin.email, "haslo": "admin"})

    # Create document
    doc = Dokument(kod="test", tytul="Old Title", tresc="Old Content")
    db_session.add(doc)
    db_session.commit()

    # Edit
    response = client.post(f"/strony/test/edytuj", data={
        "tytul": "New Title",
        "tresc": "New Content"
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"New Title" in response.data
    assert b"New Content" in response.data
    
    db_session.refresh(doc)
    assert doc.tytul == "New Title"

def test_cms_guest_access(client, db_session):
    # Create document
    doc = Dokument(kod="public", tytul="Public Doc", tresc="Secret Content")
    db_session.add(doc)
    db_session.commit()

    # Guest access
    response = client.get("/strony/public")
    assert response.status_code == 200
    assert b"Public Doc" in response.data
    
    # Guest cannot edit
    response = client.get("/strony/public/edytuj")
    assert response.status_code == 302 # Redirect to login
