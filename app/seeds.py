from app.extensions import db
from app.models import GatunekRyby

def run_seeds():
    if GatunekRyby.query.first():
        return # already seeded
    
    ryby = [
        {'nazwa': 'Sum', 'wymiar_punktowany_mm': 700, 'punkty_bazowe': 1000, 'punkty_za_mm': 10.0},
        {'nazwa': 'Głowacica', 'wymiar_punktowany_mm': 700, 'punkty_bazowe': 1000, 'punkty_za_mm': 10.0},
        {'nazwa': 'Szczupak', 'wymiar_punktowany_mm': 500, 'punkty_bazowe': 500, 'punkty_za_mm': 5.0},
        {'nazwa': 'Sandacz', 'wymiar_punktowany_mm': 500, 'punkty_bazowe': 500, 'punkty_za_mm': 5.0},
        {'nazwa': 'Boleń', 'wymiar_punktowany_mm': 400, 'punkty_bazowe': 400, 'punkty_za_mm': 5.0},
        {'nazwa': 'Lipień', 'wymiar_punktowany_mm': 300, 'punkty_bazowe': 300, 'punkty_za_mm': 5.0},
        {'nazwa': 'Pstrąg potokowy', 'wymiar_punktowany_mm': 300, 'punkty_bazowe': 300, 'punkty_za_mm': 5.0},
        {'nazwa': 'Okoń', 'wymiar_punktowany_mm': 200, 'punkty_bazowe': 100, 'punkty_za_mm': 2.0},
        {'nazwa': 'Kleń', 'wymiar_punktowany_mm': 250, 'punkty_bazowe': 250, 'punkty_za_mm': 5.0},
        {'nazwa': 'Jaź', 'wymiar_punktowany_mm': 250, 'punkty_bazowe': 250, 'punkty_za_mm': 5.0},
        {'nazwa': 'Brzana', 'wymiar_punktowany_mm': 300, 'punkty_bazowe': 300, 'punkty_za_mm': 5.0},
        {'nazwa': 'Łosoś', 'wymiar_punktowany_mm': 600, 'punkty_bazowe': 600, 'punkty_za_mm': 10.0},
        {'nazwa': 'Troć', 'wymiar_punktowany_mm': 350, 'punkty_bazowe': 350, 'punkty_za_mm': 5.0},
        {'nazwa': 'Troć jeziorowa', 'wymiar_punktowany_mm': 500, 'punkty_bazowe': 500, 'punkty_za_mm': 5.0},
        {'nazwa': 'Pstrąg tęczowy', 'wymiar_punktowany_mm': 300, 'punkty_bazowe': 300, 'punkty_za_mm': 5.0},
    ]
    
    for r in ryby:
        gatunek = GatunekRyby(
            nazwa=r['nazwa'],
            wymiar_ochronny_mm=r['wymiar_punktowany_mm'],
            wymiar_punktowany_mm=r['wymiar_punktowany_mm'],
            punkty_bazowe=r['punkty_bazowe'],
            punkty_za_mm=r['punkty_za_mm']
        )
        db.session.add(gatunek)
    
    db.session.commit()
    print("Gatunki ryb zostały dodane do bazy danych.")
