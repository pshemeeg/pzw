from app.blueprints.zawody.helpers import oblicz_klasyfikacje

class DummyZawody:
    def __init__(self, dyscyplina, liczba_tur, uczestnicy, klasyfikacja_druzynowa=False):
        self.dyscyplina = dyscyplina
        self.liczba_tur = liczba_tur
        self.uczestnicy = uczestnicy
        self.klasyfikacja_druzynowa = klasyfikacja_druzynowa

class DummyDyscyplina:
    def __init__(self, typ_wyniku):
        self.typ_wyniku = typ_wyniku

class DummyUczestnik:
    def __init__(self, id, druzyna=None):
        self.id = id
        self.druzyna = druzyna
        self.stanowiska = []

class DummyStanowisko:
    def __init__(self, tura, sektor, numer, wynik_wagowy=None, wynik_karpie=None, wyniki_ryby=None):
        self.tura = tura
        self.sektor = sektor
        self.numer = numer
        self.wynik_wagowy = wynik_wagowy
        self.wynik_karpie = wynik_karpie
        self.wyniki_ryby = wyniki_ryby

class DummyWynikWagowy:
    def __init__(self, waga_g, dyskwalifikacja=False):
        self.waga_g = waga_g
        self.dyskwalifikacja = dyskwalifikacja

def test_oblicz_klasyfikacje_wagowy():
    dyscyplina = DummyDyscyplina("wagowy")
    
    u1 = DummyUczestnik(1)
    u1.stanowiska = [DummyStanowisko(1, "A", 1, DummyWynikWagowy(1000))] # 1 miejsce (1 pkt)

    u2 = DummyUczestnik(2)
    u2.stanowiska = [DummyStanowisko(1, "A", 2, DummyWynikWagowy(500))] # 2 miejsce (2 pkt)

    u3 = DummyUczestnik(3)
    u3.stanowiska = [DummyStanowisko(1, "A", 3, DummyWynikWagowy(0))] # zero (3 pkt wg sredniej zera?)

    u4 = DummyUczestnik(4)
    u4.stanowiska = [DummyStanowisko(1, "A", 4, DummyWynikWagowy(1500, dyskwalifikacja=True))] # dysk (5 pkt)

    zawody = DummyZawody(dyscyplina, 1, [u1, u2, u3, u4])

    wynik = oblicz_klasyfikacje(zawody)
    
    indywidualna = wynik['indywidualna']
    assert len(indywidualna) == 4
    
    # Check if sorting works properly
    # u1: 1 pkt, u2: 2 pkt, u3: 3 pkt, u4: 5 pkt
    
    # 1. u1
    assert indywidualna[0]['uczestnik'].id == 1
    assert indywidualna[0]['suma_sektorowych'] == 1
    assert indywidualna[0]['miejsce'] == 1

    # 2. u2
    assert indywidualna[1]['uczestnik'].id == 2
    assert indywidualna[1]['suma_sektorowych'] == 2
    assert indywidualna[1]['miejsce'] == 2

    # 3. u3 (zero)
    # ZOSW rules say NC if zero in all rounds. Here we have 1 round, so he is NC.
    assert indywidualna[2]['uczestnik'].id == 3
    assert indywidualna[2]['suma_sektorowych'] == 99999
    assert indywidualna[2]['status'] == 'NC'
    assert indywidualna[2]['miejsce'] == 'NC'

    # 4. u4 (dysk)
    assert indywidualna[3]['uczestnik'].id == 4
    assert indywidualna[3]['suma_sektorowych'] == 99999
    assert indywidualna[3]['status'] == 'NC'

def test_oblicz_klasyfikacje_ex_aequo():
    dyscyplina = DummyDyscyplina("wagowy")
    
    u1 = DummyUczestnik(1)
    u1.stanowiska = [DummyStanowisko(1, "A", 1, DummyWynikWagowy(1000))] # 1.5 pkt

    u2 = DummyUczestnik(2)
    u2.stanowiska = [DummyStanowisko(1, "A", 2, DummyWynikWagowy(1000))] # 1.5 pkt

    u3 = DummyUczestnik(3)
    u3.stanowiska = [DummyStanowisko(1, "A", 3, DummyWynikWagowy(500))] # 3 pkt

    zawody = DummyZawody(dyscyplina, 1, [u1, u2, u3])
    wynik = oblicz_klasyfikacje(zawody)
    indywidualna = wynik['indywidualna']
    
    # Find points for u1 and u2
    pts_u1 = next(r for r in indywidualna if r['uczestnik'].id == 1)['suma_sektorowych']
    pts_u2 = next(r for r in indywidualna if r['uczestnik'].id == 2)['suma_sektorowych']
    pts_u3 = next(r for r in indywidualna if r['uczestnik'].id == 3)['suma_sektorowych']
    
    assert pts_u1 == 1.5
    assert pts_u2 == 1.5
    assert pts_u3 == 3
