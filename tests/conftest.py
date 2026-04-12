import pytest
from app import create_app
from app.extensions import db
from app.models import Uzytkownik, Zawody, Dyscyplina, Zawodnik, Uczestnik, Lowisko

@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def db_session(app):
    with app.app_context():
        # Setup basic DB state for tests
        admin = Uzytkownik(username="admin", is_admin=True)
        admin.set_password("admin")
        db.session.add(admin)

        dyscyplina = Dyscyplina(nazwa="Spławik", kod="splawik", typ_wyniku="wagowy")
        db.session.add(dyscyplina)
        db.session.commit()
        
        yield db.session
        
        db.session.rollback()
        # Clean up tables
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
