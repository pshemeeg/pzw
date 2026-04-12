from app.models import GatunekRyby
import math

def oblicz_punkty_ryby(gatunek, dlugosc_mm):
    gatunek_norm = gatunek.lower().replace(' ', '_').replace('ą', 'a').replace('ę', 'e').replace('ó', 'o').replace('ś', 's').replace('ł', 'l').replace('ż', 'z').replace('ź', 'z').replace('ć', 'c').replace('ń', 'n')
    
    # Próbujemy znaleźć rybę w bazie. Ponieważ nazwy w bazie mogą być ładnie sformatowane (np. "Okoń"), 
    # wyszukujemy po nazwie zignorowaniem wielkości znaków (lub exact match).
    # Żeby nie uderzać do bazy o każdą rybę w pętli (co może być wolne), w produkcji lepiej byłoby to cachować, 
    # ale na razie zrobimy to prosto i poprawnie.
    from app.extensions import db
    zasady = GatunekRyby.query.filter(db.func.lower(db.func.replace(db.func.replace(db.func.replace(db.func.replace(db.func.replace(db.func.replace(db.func.replace(db.func.replace(db.func.replace(GatunekRyby.nazwa, 'ą', 'a'), 'ę', 'e'), 'ó', 'o'), 'ś', 's'), 'ł', 'l'), 'ż', 'z'), 'ź', 'z'), 'ć', 'c'), 'ń', 'n')) == gatunek_norm).first()
    
    # Fallback jeśli nie użyto polskich znaków w bazie, to zróbmy proste ilike
    if not zasady:
        zasady = GatunekRyby.query.filter(GatunekRyby.nazwa.ilike(f"%{gatunek}%")).first()
        
    if not zasady:
        return 0, False

    if dlugosc_mm <= zasady.wymiar_punktowany_mm: # "Ryba zaliczona jeśli dlugosc_mm > min_mm"
        return 0, False
    
    dlugosc_cm = dlugosc_mm / 10.0
    min_cm = zasady.wymiar_punktowany_mm / 10.0
    
    dlugosc_cm_rounded = math.ceil(dlugosc_cm)
    
    punkty = zasady.punkty_bazowe + (dlugosc_cm_rounded - min_cm) * (zasady.punkty_za_mm * 10)
    return int(punkty), True
