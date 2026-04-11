WYMIARY_OCHRONNE = {
    'szczupak': 500, 'sandacz': 500, 'sum': 700, 'bolen': 400,
    'brzana': 300, 'lipien': 300, 'pstrag_potokowy': 300,
    'pstrag_teczowy': 300, 'glowacica': 700, 'losos': 600,
    'troc': 350, 'troc_jeziorowa': 500, 'okon': 200, 'klen': 250,
    'jaz': 250
}

# Values in prompt are given in cm. In the DB, length is in mm.
# PUNKTACJA_SPINNING = {'sum': {'min_cm': 70, 'base': 1000, 'per_cm': 100}, ...}
# We will use mm for lengths directly to avoid floating point issues.
PUNKTACJA_SPINNING = {
    'sum':          {'min_mm': 700, 'base': 1000, 'per_mm': 10}, # per_cm=100 -> per_mm=10
    'glowacica':    {'min_mm': 700, 'base': 1000, 'per_mm': 10},
    'szczupak':     {'min_mm': 500, 'base': 500,  'per_mm': 5},
    'sandacz':      {'min_mm': 500, 'base': 500,  'per_mm': 5},
    'bolen':        {'min_mm': 400, 'base': 400,  'per_mm': 5},
    'lipien':       {'min_mm': 300, 'base': 300,  'per_mm': 5},
    'pstrag_potokowy': {'min_mm': 300, 'base': 300, 'per_mm': 5},
    'okon':         {'min_mm': 200, 'base': 100,  'per_mm': 2},
    'klen':         {'min_mm': 250, 'base': 250,  'per_mm': 5},
    'jaz':          {'min_mm': 250, 'base': 250,  'per_mm': 5},
    'brzana':       {'min_mm': 300, 'base': 300,  'per_mm': 5},
    'losos':        {'min_mm': 600, 'base': 600,  'per_mm': 10},
    'troc':         {'min_mm': 350, 'base': 350,  'per_mm': 5},
    'troc_jeziorowa': {'min_mm': 500, 'base': 500, 'per_mm': 5},
    'pstrag_teczowy': {'min_mm': 300, 'base': 300, 'per_mm': 5},
}

def oblicz_punkty_ryby(gatunek, dlugosc_mm):
    gatunek = gatunek.lower().replace(' ', '_').replace('ą', 'a').replace('ę', 'e').replace('ó', 'o').replace('ś', 's').replace('ł', 'l').replace('ż', 'z').replace('ź', 'z').replace('ć', 'c').replace('ń', 'n')
    if gatunek not in PUNKTACJA_SPINNING:
        return 0, False

    zasady = PUNKTACJA_SPINNING[gatunek]
    if dlugosc_mm <= zasady['min_mm']: # "Ryba zaliczona jeśli dlugosc_cm > min_cm (nie >=)"
        return 0, False
    
    # calculation in cm for points per extra cm
    # "punkty = base + (dlugosc_cm - min_cm) * per_cm"
    # To properly handle per_cm with mm, we should calculate extra_cm
    # usually spinning competitions measure to the nearest full mm or round up to cm?
    # Actually, often it's "za każdy rozpoczęty centymetr".
    # Let's just calculate: base + floor((dlugosc_mm - min_mm) / 10) * per_cm
    # The prompt formula: punkty = base + (dlugosc_cm - min_cm) * per_cm
    # Wait, if min_cm=50, and length is 50.1 cm (501 mm), it's 1 extra cm or 0.1?
    # Let's stick strictly to what mathematically matches:
    dlugosc_cm = dlugosc_mm / 10.0
    min_cm = zasady['min_mm'] / 10.0
    
    # Usually in spinning sport in Poland, lengths are rounded up to the nearest full cm.
    import math
    dlugosc_cm_rounded = math.ceil(dlugosc_cm)
    
    punkty = zasady['base'] + (dlugosc_cm_rounded - min_cm) * (zasady['per_mm'] * 10)
    return int(punkty), True
