import pytest
import io
from app.models import Lowisko, Dyscyplina, GatunekRyby, Uzytkownik

def test_import_lowiska_csv(client, db_session):
    admin = Uzytkownik.query.filter_by(rola="admin").first()
    client.post("/auth/login", data={"email": admin.email, "haslo": "admin"})

    csv_content = "nazwa,miejscowosc,opis\nStaw 1,Miasto A,Fajne\nStaw 2,Miasto B,Super"
    data = {
        'file': (io.BytesIO(csv_content.encode('utf-8')), 'lowiska.csv')
    }

    response = client.post("/slowniki/import/lowiska", data=data, content_type='multipart/form-data', follow_redirects=True)
    assert b"Import lowiska zako\xc5\x84czony" in response.data
    
    assert Lowisko.query.filter_by(nazwa="Staw 1").first() is not None

def test_import_dyscypliny_csv(client, db_session):
    admin = Uzytkownik.query.filter_by(rola="admin").first()
    client.post("/auth/login", data={"email": admin.email, "haslo": "admin"})

    csv_content = "nazwa,kod,typ_wyniku\nFeeder,feeder,wagowy\nSpinning,spin,punktowy"
    data = {
        'file': (io.BytesIO(csv_content.encode('utf-8')), 'dyscypliny.csv')
    }

    response = client.post("/slowniki/import/dyscypliny", data=data, content_type='multipart/form-data', follow_redirects=True)
    # Check if added
    assert Dyscyplina.query.filter_by(kod="feeder").first() is not None
    assert Dyscyplina.query.filter_by(kod="spin").first() is not None

def test_import_ryby_csv(client, db_session):
    admin = Uzytkownik.query.filter_by(rola="admin").first()
    client.post("/auth/login", data={"email": admin.email, "haslo": "admin"})

    csv_content = "nazwa,wymiar_ochronny_mm,wymiar_punktowany_mm,punkty_bazowe,punkty_za_mm\nSzczupak,500,500,750,10.0"
    data = {
        'file': (io.BytesIO(csv_content.encode('utf-8')), 'ryby.csv')
    }

    response = client.post("/slowniki/import/ryby", data=data, content_type='multipart/form-data', follow_redirects=True)
    assert b"Import ryby zako\xc5\x84czony" in response.data
    
    szczupak = GatunekRyby.query.filter_by(nazwa="Szczupak").first()
    assert szczupak is not None
    assert szczupak.punkty_bazowe == 750
