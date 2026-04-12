from app import create_app
from app.seeds import seed_gatunki_ryb

app = create_app()
with app.app_context():
    seed_gatunki_ryb()
