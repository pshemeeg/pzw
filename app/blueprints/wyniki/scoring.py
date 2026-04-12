import math
from app.models import GatunekRyby
from app.extensions import db


def oblicz_punkty_ryby(gatunek, dlugosc_mm):
    """
    Oblicza punkty za rybę na podstawie zasad z bazy danych.
    Zwraca (punkty, czy_zaliczona).
    """
    # Normalizacja nazwy do wyszukiwania (uproszczona)
    gatunek_norm = gatunek.strip().lower()

    # Próbujemy znaleźć rybę w bazie.
    # W produkcji lepiej byłoby to cachować.
    zasady = GatunekRyby.query.filter(
        GatunekRyby.nazwa.ilike(gatunek_norm)
    ).first()

    # Fallback na proste wyszukiwanie fragmentu
    if not zasady:
        zasady = GatunekRyby.query.filter(
            GatunekRyby.nazwa.ilike(f"%{gatunek_norm}%")
        ).first()

    if not zasady:
        return 0, False

    # Ryba zaliczona jeśli dlugosc_mm > min_mm
    if dlugosc_mm <= zasady.wymiar_punktowany_mm:
        return 0, False

    dlugosc_cm = dlugosc_mm / 10.0
    min_cm = zasady.wymiar_punktowany_mm / 10.0

    # PZW: Zaokrąglamy długość w górę do pełnych cm
    dlugosc_cm_rounded = math.ceil(dlugosc_cm)

    # Wzór: punkty_bazowe + (dlugosc_cm - min_cm) * pkt_za_cm
    # pkt_za_mm * 10 = pkt_za_cm
    punkty = zasady.punkty_bazowe + (
        dlugosc_cm_rounded - min_cm
    ) * (zasady.punkty_za_mm * 10)

    return int(punkty), True
