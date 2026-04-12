import pytest
from app.models import Uzytkownik, Dyscyplina

def test_user_settings_save(client, db_session):
    # Setup
    admin = Uzytkownik.query.filter_by(rola="admin").first()
    client.post("/auth/login", data={"email": admin.email, "haslo": "admin"})

    d = Dyscyplina(nazwa="SettingsTest", kod="st", typ_wyniku="wagowy")
    db_session.add(d)
    db_session.commit()

    # Save settings
    response = client.post("/profil/ustawienia", data={
        "domyslna_dyscyplina_id": d.id,
        "domyslna_liczba_sektorow": 3,
        "domyslna_liczba_tur": 2,
        "domyslna_kategoria": "seniorzy"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Ustawienia zosta\xc5\x82y zapisane" in response.data

    # Verify in DB
    db_session.refresh(admin)
    assert admin.ustawienia["domyslna_dyscyplina_id"] == d.id
    assert admin.ustawienia["domyslna_liczba_sektorow"] == 3

def test_competition_form_uses_defaults(client, db_session):
    # Setup
    admin = Uzytkownik.query.filter_by(rola="admin").first()
    client.post("/auth/login", data={"email": admin.email, "haslo": "admin"})

    d = Dyscyplina(nazwa="DefaultTest", kod="dt", typ_wyniku="wagowy")
    db_session.add(d)
    db_session.commit()

    # Set defaults
    admin.ustawienia = {
        "domyslna_dyscyplina_id": d.id,
        "domyslna_liczba_sektorow": 5
    }
    db_session.commit()

    # Open new competition form
    response = client.get("/zawody/nowe")
    assert response.status_code == 200
    # Check if correct discipline is selected and sector count is set
    assert f'value="{d.id}"'.encode() in response.data
    assert b'selected' in response.data
    assert b'name="liczba_sektorow"' in response.data
    assert b'value="5"' in response.data
