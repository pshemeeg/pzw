from app import create_app
from app.models import Zawody
from collections import defaultdict

app = create_app()
with app.app_context():
    zawody = Zawody.query.get(1)
    typ_wyniku = zawody.dyscyplina.typ_wyniku
    uczestnicy = zawody.uczestnicy
    tury = list(range(1, zawody.liczba_tur + 1))
    
    wyniki_tur = {t: {} for t in tury}
    
    for u in uczestnicy:
        for stan in u.stanowiska:
            t = stan.tura
            if t not in wyniki_tur: continue
                
            dysk = False
            zero = False
            waga_do_remisow = 0
            wynik_sort = ()
            
            if typ_wyniku == 'wagowy':
                if stan.wynik_wagowy:
                    waga_do_remisow = stan.wynik_wagowy.waga_g
                    wynik_sort = (waga_do_remisow,)
                    dysk = stan.wynik_wagowy.dyskwalifikacja
                    if waga_do_remisow <= 0: zero = True
                else:
                    zero = True
                    wynik_sort = (0,)
            
            wyniki_tur[t][u.id] = {
                'stanowisko': stan,
                'wynik_sort': wynik_sort,
                'dysk': dysk,
                'zero': zero,
                'waga': waga_do_remisow
            }

    pkt_sektorowe = defaultdict(dict)
    
    for t in tury:
        sektory = defaultdict(list)
        for u_id, data in wyniki_tur[t].items():
            sektory[data['stanowisko'].sektor].append(u_id)
            
        for sektor, zawodnicy_ids in sektory.items():
            N = len(zawodnicy_ids)
            z_wynikiem = []
            zera = []
            dyski = []
            
            for uid in zawodnicy_ids:
                data = wyniki_tur[t][uid]
                if data['dysk']:
                    dyski.append(uid)
                elif data['zero']:
                    zera.append(uid)
                else:
                    z_wynikiem.append(uid)
            
            z_wynikiem.sort(key=lambda uid: wyniki_tur[t][uid]['wynik_sort'], reverse=True)
            print(f"Tura {t} Sektor {sektor} -> z_wynikiem: {z_wynikiem}, zera: {zera}")
            
            miejsce_counter = 1
            idx = 0
            while idx < len(z_wynikiem):
                aktualny_wynik = wyniki_tur[t][z_wynikiem[idx]]['wynik_sort']
                grupa = []
                while idx < len(z_wynikiem) and wyniki_tur[t][z_wynikiem[idx]]['wynik_sort'] == aktualny_wynik:
                    grupa.append(z_wynikiem[idx])
                    idx += 1
                dane_miejsce = miejsce_counter
                for uid in grupa:
                    pkt_sektorowe[uid][t] = dane_miejsce
                miejsce_counter += len(grupa)
            
            if zera:
                miejsce_dla_zera = miejsce_counter
                for uid in zera:
                    pkt_sektorowe[uid][t] = miejsce_dla_zera
                miejsce_counter += len(zera)
                
            print(f"Pkt sektorowe po tura {t}: {dict(pkt_sektorowe)}")

