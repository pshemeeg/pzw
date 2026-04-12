import pytest
import io
from app.models import Zawodnik, Uzytkownik

def test_import_zawodnicy_csv(client, db_session):
    # Setup: Login as admin
    admin = Uzytkownik.query.filter_by(rola="admin").first()
    client.post("/auth/login", data={"email": admin.email, "haslo": "admin"})

    # Prepare CSV data
    csv_content = "imie,nazwisko,kolo,nr_licencji\nJan,Kowalski,Kolo 1,WA-1\nAdam,Nowak,Kolo 2,WA-2"
    data = {
        'file': (io.BytesIO(csv_content.encode('utf-8')), 'test.csv')
    }

    response = client.post("/zawodnicy/import", data=data, content_type='multipart/form-data', follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Import zako\xc5\x84czony" in response.data
    
    # Verify DB
    j_kowalski = Zawodnik.query.filter_by(nazwisko="Kowalski").first()
    assert j_kowalski is not None
    assert j_kowalski.kolo == "Kolo 1"
    
    a_nowak = Zawodnik.query.filter_by(nazwisko="Nowak").first()
    assert a_nowak is not None
    assert a_nowak.nr_licencji == "WA-2"

def test_import_zawodnicy_csv_duplicates(client, db_session):
    # Setup: Login as admin
    admin = Uzytkownik.query.filter_by(rola="admin").first()
    client.post("/auth/login", data={"email": admin.email, "haslo": "admin"})

    # Add one existing
    db_session.add(Zawodnik(imie="Jan", nazwisko="Kowalski", kolo="Kolo 1"))
    db_session.commit()

    # Prepare CSV data with a duplicate
    csv_content = "imie,nazwisko,kolo,nr_licencji\nJan,Kowalski,Kolo 1,WA-1\nAdam,Nowak,Kolo 2,WA-2"
    data = {
        'file': (io.BytesIO(csv_content.encode('utf-8')), 'test.csv')
    }

    response = client.post("/zawodnicy/import", data=data, content_type='multipart/form-data', follow_redirects=True)
    
    assert b"Dodano: 1" in response.data
    assert b"Pomini\xc4\x99to (duplikaty/b\xc5\x82\xc4\x99dy): 1" in response.data
