from app.extensions import db
from app.models import Dyscyplina, Lowisko


def seed_dyscypliny():
    dyscypliny = [
        {"nazwa": "Spławik", "kod": "splawik", "typ_wyniku": "wagowy"},
        {"nazwa": "Feeder", "kod": "feeder", "typ_wyniku": "wagowy"},
        {"nazwa": "Method feeder", "kod": "method", "typ_wyniku": "wagowy"},
        {"nazwa": "Karpiówka", "kod": "karpie", "typ_wyniku": "karpie"},
        {"nazwa": "Spinning", "kod": "spinning", "typ_wyniku": "punktowy"},
        {"nazwa": "Mucha", "kod": "mucha", "typ_wyniku": "punktowy"},
        {"nazwa": "Podlodowa", "kod": "podlodowa", "typ_wyniku": "wagowy"},
    ]
    for d in dyscypliny:
        if not Dyscyplina.query.filter_by(kod=d["kod"]).first():
            db.session.add(Dyscyplina(**d))
    db.session.commit()


def seed_lowiska():
    lowiska = [
        {"nazwa": "Zalew Zegrzyński", "miejscowosc": "Zegrze"},
        {"nazwa": "Wisła — Warszawa", "miejscowosc": "Warszawa"},
        {"nazwa": "Narew — Pułtusk", "miejscowosc": "Pułtusk"},
        {"nazwa": "Jeziorko Czerniakowskie", "miejscowosc": "Warszawa"},
        {"nazwa": "Zalew Sulejowski", "miejscowosc": "Sulejów"},
    ]
    for l in lowiska:
        if not Lowisko.query.filter_by(nazwa=l["nazwa"]).first():
            db.session.add(Lowisko(**l))
    db.session.commit()


def run_seeds():
    seed_dyscypliny()
    seed_lowiska()
