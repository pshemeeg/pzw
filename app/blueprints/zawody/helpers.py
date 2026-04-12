from collections import defaultdict

def oblicz_klasyfikacje(zawody):
    """
    Zwraca słownik z klasyfikacją indywidualną i drużynową (jeśli dotyczy).
    """
    typ_wyniku = zawody.dyscyplina.typ_wyniku
    
    uczestnicy = zawody.uczestnicy
    if not uczestnicy:
        return {'indywidualna': [], 'druzynowa': []}
        
    tury = list(range(1, zawody.liczba_tur + 1))
    
    # 1. Zebranie wyników per tura per uczestnik
    # wyniki_tur[tura][uczestnik_id] = {'stanowisko': Stanowisko, 'wynik': tuple, 'dysk': bool, 'zero': bool, 'waga': int}
    wyniki_tur = {t: {} for t in tury}
    
    for u in uczestnicy:
        for stan in u.stanowiska:
            t = stan.tura
            if t not in wyniki_tur:
                continue
                
            dysk = False
            zero = False
            waga_do_remisow = 0
            wynik_sort = ()
            
            if typ_wyniku == 'wagowy':
                if stan.wynik_wagowy:
                    waga_do_remisow = stan.wynik_wagowy.waga_g
                    wynik_sort = (waga_do_remisow,)
                    dysk = stan.wynik_wagowy.dyskwalifikacja
                    if waga_do_remisow <= 0:
                        zero = True
                else:
                    zero = True
                    wynik_sort = (0,)
                    
            elif typ_wyniku == 'karpie':
                if stan.wynik_karpie:
                    waga_do_remisow = stan.wynik_karpie.waga_g
                    # Waga decyduje, potem najcięższa ryba, ewentualnie punkty karne odejmowane od wagi?
                    # "Liczba sztuk, waga łączna, najcięższa ryba, punkty karne"
                    # Zakładam standardowo waga_g wyższa to lepiej.
                    # Zastosujmy proste sortowanie po (waga, najciezsza). Punkty karne potraktujmy jako karę do wagi.
                    wynik_sort = (max(0, waga_do_remisow - stan.wynik_karpie.punkty_karne), stan.wynik_karpie.najciezsza_g)
                    if waga_do_remisow <= 0:
                        zero = True
                else:
                    zero = True
                    wynik_sort = (0, 0)
                    
            elif typ_wyniku == 'punktowy':
                if stan.wyniki_ryby:
                    suma_pkt = sum(r.punkty for r in stan.wyniki_ryby if r.zaliczona)
                    suma_dlugosci = sum(r.dlugosc_mm for r in stan.wyniki_ryby if r.zaliczona)
                    # Do remisów użyjemy sumy punktów (zamiast wagi)
                    waga_do_remisow = suma_pkt
                    wynik_sort = (suma_pkt,)
                    if suma_pkt <= 0:
                        zero = True
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

    # 2. Obliczanie punktów sektorowych per tura
    # pkt_sektorowe[u_id][tura] = int/float
    pkt_sektorowe = defaultdict(dict)
    
    for t in tury:
        # Grupujemy zawodników w turze po sektorach
        sektory = defaultdict(list)
        for u_id, data in wyniki_tur[t].items():
            sektory[data['stanowisko'].sektor].append(u_id)
            
        # ZOSW: Do obliczania miejsc dla zer i dyskwalifikacji przy nierównych sektorach
        # bierze się pod uwagę pojemność najliczniejszego sektora w danej turze.
        max_sektor_size = 0
        if sektory:
            max_sektor_size = max(len(zaw) for zaw in sektory.values())
            
        for sektor, zawodnicy_ids in sektory.items():
            N = len(zawodnicy_ids)
            
            # Dzielimy na 3 grupy: DYS, ZERO, Z_WYNIKIEM
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
            
            # Sortowanie Z_WYNIKIEM malejąco
            z_wynikiem.sort(key=lambda uid: wyniki_tur[t][uid]['wynik_sort'], reverse=True)
            
            # Nadawanie punktów dla Z_WYNIKIEM
            miejsce_counter = 1
            idx = 0
            while idx < len(z_wynikiem):
                aktualny_wynik = wyniki_tur[t][z_wynikiem[idx]]['wynik_sort']
                grupa = []
                while idx < len(z_wynikiem) and wyniki_tur[t][z_wynikiem[idx]]['wynik_sort'] == aktualny_wynik:
                    grupa.append(z_wynikiem[idx])
                    idx += 1
                
                # Wszyscy ex aequo dostają średnią z zajmowanych miejsc
                start_m = miejsce_counter
                end_m = miejsce_counter + len(grupa) - 1
                srednia_miejsc = sum(range(start_m, end_m + 1)) / len(grupa)
                
                for uid in grupa:
                    pkt_sektorowe[uid][t] = srednia_miejsc
                
                miejsce_counter += len(grupa)
            
            # Nadawanie punktów dla ZERO (do max_sektor_size wg ZOSW)
            if zera:
                start_m = miejsce_counter
                end_m = max_sektor_size  # Obliczamy średnią do najliczniejszego sektora
                
                # Jeśli z jakiegoś powodu start_m > end_m, to znaczy że sector size logic is weird,
                # ale standardowo start_m <= max_sektor_size.
                if start_m <= end_m:
                    liczba_wolnych = end_m - start_m + 1
                    srednia_zera = sum(range(start_m, end_m + 1)) / liczba_wolnych
                else:
                    srednia_zera = start_m
                    
                for uid in zera:
                    pkt_sektorowe[uid][t] = srednia_zera
            
            # Nadawanie punktów dla DYSK
            if dyski:
                # Dyskwalifikacja = liczba zawodników w najliczniejszym sektorze + 1
                miejsce_dla_dysk = max_sektor_size + 1
                for uid in dyski:
                    pkt_sektorowe[uid][t] = miejsce_dla_dysk


    # 3. Klasyfikacja indywidualna
    indywidualna = []
    for u in uczestnicy:
        # Suma punktów sektorowych ze wszystkich tur, jeśli uczestniczył i ma stanowiska we wszystkich turach
        punkty_u = []
        wagi_u = []
        zera_lub_dyski = 0
        ma_wszystkie_tury = True
        
        for t in tury:
            if t in pkt_sektorowe[u.id]:
                p = pkt_sektorowe[u.id][t]
                punkty_u.append(p)
                data = wyniki_tur[t][u.id]
                wagi_u.append(data['waga'])
                if data['zero'] or data['dysk']:
                    zera_lub_dyski += 1
            else:
                ma_wszystkie_tury = False
                break
                
        # N/C jeśli zawodnik nie miał stanowiska, lub miał 0 / DYS we wszystkich turach
        if not ma_wszystkie_tury or zera_lub_dyski == len(tury):
            status = 'NC'
            suma_pkt = 99999  # do sortowania na koniec
            suma_wag = 0
        else:
            status = 'OK'
            suma_pkt = sum(punkty_u)
            suma_wag = sum(wagi_u)
            
        max_ryba_mm = 0
        if typ_wyniku == 'punktowy':
            for stan in u.stanowiska:
                for ryba in stan.wyniki_ryby:
                    if ryba.zaliczona and ryba.dlugosc_mm > max_ryba_mm:
                        max_ryba_mm = ryba.dlugosc_mm

        indywidualna.append({
            'uczestnik': u,
            'suma_sektorowych': suma_pkt,
            'suma_wag': suma_wag,
            'punkty_tury': {t: pkt_sektorowe[u.id].get(t, '-') for t in tury},
            'najdluzsza_ryba_cm': round(max_ryba_mm / 10, 1) if max_ryba_mm > 0 else 0,
            'status': status
        })
        
    # Sortowanie: 1. suma_sektorowych rosnąco, 2. suma_wag malejąco
    indywidualna.sort(key=lambda x: (x['suma_sektorowych'], -x['suma_wag']))
    
    # Oznaczenie miejsc
    miejsce = 1
    for r in indywidualna:
        if r['status'] == 'OK':
            r['miejsce'] = miejsce
            miejsce += 1
        else:
            r['miejsce'] = 'NC'

    # 4. Klasyfikacja drużynowa
    druzynowa = []
    if zawody.klasyfikacja_druzynowa:
        # Grupujemy zawodników po nazwie drużyny
        druzyny = defaultdict(list)
        for r in indywidualna:
            d = r['uczestnik'].druzyna
            if d:
                druzyny[d].append(r)
                
        for nazwa_druzyny, czlonkowie in druzyny.items():
            if len(czlonkowie) == 3:
                # Sprawdzamy czy którykolwiek jest NC
                if any(c['status'] == 'NC' for c in czlonkowie):
                    druzynowa.append({
                        'druzyna': nazwa_druzyny,
                        'suma_sektorowych': 99999,
                        'suma_wag': 0,
                        'zawodnicy': czlonkowie,
                        'status': 'NC',
                        'miejsce': 'NC'
                    })
                else:
                    suma_sekt_d = sum(c['suma_sektorowych'] for c in czlonkowie)
                    suma_wag_d = sum(c['suma_wag'] for c in czlonkowie)
                    druzynowa.append({
                        'druzyna': nazwa_druzyny,
                        'suma_sektorowych': suma_sekt_d,
                        'suma_wag': suma_wag_d,
                        'zawodnicy': czlonkowie,
                        'status': 'OK'
                    })
                    
        # Sortowanie drużyn
        druzynowa.sort(key=lambda x: (x['suma_sektorowych'], -x['suma_wag']))
        m_druz = 1
        for d in druzynowa:
            if d['status'] == 'OK':
                d['miejsce'] = m_druz
                m_druz += 1

    return {
        'indywidualna': indywidualna,
        'druzynowa': druzynowa
    }
