from datetime import datetime, timezone
from app.extensions import db
from flask_login import UserMixin


class Dyscyplina(db.Model):
    __tablename__ = "dyscypliny"

    id = db.Column(db.Integer, primary_key=True)
    nazwa = db.Column(db.String(64), nullable=False, unique=True)
    kod = db.Column(db.String(16), nullable=False, unique=True)
    typ_wyniku = db.Column(db.String(16), nullable=False)

    def __repr__(self):
        return f"<Dyscyplina {self.kod}>"


class Lowisko(db.Model):
    __tablename__ = "lowiska"

    id = db.Column(db.Integer, primary_key=True)
    nazwa = db.Column(db.String(128), nullable=False)
    miejscowosc = db.Column(db.String(128), nullable=False)
    opis = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Lowisko {self.nazwa}>"


class Zawodnik(db.Model):
    __tablename__ = "zawodnicy"

    id = db.Column(db.Integer, primary_key=True)
    imie = db.Column(db.String(64), nullable=False)
    nazwisko = db.Column(db.String(64), nullable=False)
    kolo = db.Column(db.String(128), nullable=False)
    nr_licencji = db.Column(db.String(32), nullable=True, unique=True)
    rodo_zgoda = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint("imie", "nazwisko", "kolo", name="uq_zawodnik"),
    )

    def __repr__(self):
        return f"<Zawodnik {self.imie} {self.nazwisko}>"

    def display_name(self, is_authenticated=False):
        """Zwraca imię i nazwisko lub postać zanonimizowaną zgodnie z RODO."""
        if is_authenticated or self.rodo_zgoda:
            return f"{self.nazwisko} {self.imie}"
        return f"Zawodnik#{self.id}"


class Sedzia(db.Model):
    __tablename__ = "sedziowie"

    id = db.Column(db.Integer, primary_key=True)
    imie = db.Column(db.String(64), nullable=False)
    nazwisko = db.Column(db.String(64), nullable=False)
    telefon = db.Column(db.String(32), nullable=True)
    kolo = db.Column(db.String(128), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    uzytkownik = db.relationship("Uzytkownik", back_populates="sedzia", uselist=False)

    def __repr__(self):
        return f"<Sedzia {self.imie} {self.nazwisko}>"


class Uzytkownik(db.Model, UserMixin):
    __tablename__ = "uzytkownicy"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), nullable=False, unique=True)
    haslo_hash = db.Column(db.String(255), nullable=False)
    rola = db.Column(db.String(16), nullable=False, default="sedzia")
    aktywny = db.Column(db.Boolean, default=True)
    ostatnie_logowanie = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    sedzia_id = db.Column(db.Integer, db.ForeignKey("sedziowie.id"), nullable=True)
    sedzia = db.relationship(
        "Sedzia",
        back_populates="uzytkownik",
    )
    ustawienia = db.Column(db.JSON, nullable=True)

    def __repr__(self):
        return f"<Uzytkownik {self.email}>"

    def is_admin(self):
        return self.rola == "admin"


zawody_sedziowie = db.Table(
    "zawody_sedziowie",
    db.Column("zawody_id", db.Integer, db.ForeignKey("zawody.id"), primary_key=True),
    db.Column("sedzia_id", db.Integer, db.ForeignKey("sedziowie.id"), primary_key=True),
    db.Column("rola_na_zawodach", db.String(32), nullable=False, default="sektorowy"),
)


class Zawody(db.Model):
    __tablename__ = "zawody"

    id = db.Column(db.Integer, primary_key=True)
    nr_zawodow = db.Column(db.String(32), nullable=True)
    nazwa = db.Column(db.String(256), nullable=False)
    data = db.Column(db.Date, nullable=False)
    data_do = db.Column(db.Date, nullable=True)
    godzina_start = db.Column(db.Time, nullable=True)
    godzina_koniec = db.Column(db.Time, nullable=True)
    kategoria = db.Column(db.String(64), nullable=True)
    rejon = db.Column(db.String(64), nullable=True)
    liczba_sektorow = db.Column(db.Integer, nullable=False, default=1)
    liczba_tur = db.Column(db.Integer, nullable=False, default=1)
    grand_prix = db.Column(db.Boolean, default=False)
    klasyfikacja_druzynowa = db.Column(db.Boolean, default=False)
    sezon = db.Column(db.Integer, nullable=False, default=lambda: datetime.now(timezone.utc).year)
    status = db.Column(db.String(16), nullable=False, default="planowane")
    uwagi = db.Column(db.Text, nullable=True)
    sedziowie_sektorowi = db.Column(db.Text, nullable=True)
    sedziowie_kontrolni = db.Column(db.Text, nullable=True)
    organizator_kolo = db.Column(db.String(128), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    dyscyplina_id = db.Column(
        db.Integer, db.ForeignKey("dyscypliny.id"), nullable=False
    )
    lowisko_id = db.Column(db.Integer, db.ForeignKey("lowiska.id"), nullable=True)
    organizator_id = db.Column(db.Integer, db.ForeignKey("sedziowie.id"), nullable=True)
    sekretarz_id = db.Column(db.Integer, db.ForeignKey("sedziowie.id"), nullable=True)

    dyscyplina = db.relationship("Dyscyplina", backref="zawody")
    lowisko = db.relationship("Lowisko", backref="zawody")
    organizator = db.relationship("Sedzia", foreign_keys=[organizator_id])
    sekretarz = db.relationship("Sedzia", foreign_keys=[sekretarz_id])
    sedziowie = db.relationship(
        "Sedzia",
        secondary=zawody_sedziowie,
        backref="zawody",
    )
    uczestnicy = db.relationship(
        "Uczestnik",
        back_populates="zawody",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Zawody {self.nr_zawodow} {self.nazwa}>"

    @property
    def computed_status(self):
        """Dynamicznie wylicza status zawodów na podstawie daty i czasu."""
        teraz = datetime.now()
        
        # Jeśli data jest w przyszłości -> planowane
        data_start = datetime.combine(self.data, self.godzina_start or datetime.min.time())
        if teraz < data_start:
            return "planowane"
            
        # Jeśli mamy data_do i jest w przeszłości -> zakonczone
        koniec_dnia = self.data_do or self.data
        godzina_stop = self.godzina_koniec or datetime.max.time()
        data_koniec = datetime.combine(koniec_dnia, godzina_stop)
        
        if teraz > data_koniec:
            return "zakonczone"
            
        # W przeciwnym razie -> w trakcie
        return "w_trakcie"

    @property
    def status_display(self):
        s = self.computed_status
        mapping = {
            "planowane": ("Planowane", "bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400", "bg-gray-400"),
            "w_trakcie": ("W trakcie", "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400", "bg-blue-500"),
            "zakonczone": ("Zakończone", "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400", "bg-green-500"),
        }
        return mapping.get(s, ("Nieznany", "bg-gray-100 text-gray-600", "bg-gray-400"))


class GatunekRyby(db.Model):
    __tablename__ = "gatunki_ryb"

    id = db.Column(db.Integer, primary_key=True)
    nazwa = db.Column(db.String(64), nullable=False, unique=True)
    wymiar_ochronny_mm = db.Column(db.Integer, nullable=False, default=0)
    wymiar_punktowany_mm = db.Column(db.Integer, nullable=False, default=0)
    punkty_bazowe = db.Column(db.Integer, nullable=False, default=0)
    punkty_za_mm = db.Column(db.Float, nullable=False, default=0.0)

    def __repr__(self):
        return f"<GatunekRyby {self.nazwa}>"


class Uczestnik(db.Model):
    __tablename__ = "uczestnicy"

    id = db.Column(db.Integer, primary_key=True)
    numer_startowy = db.Column(db.Integer, nullable=True)
    druzyna = db.Column(db.String(128), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    zawody_id = db.Column(db.Integer, db.ForeignKey("zawody.id"), nullable=False)
    zawodnik_id = db.Column(db.Integer, db.ForeignKey("zawodnicy.id"), nullable=False)

    zawody = db.relationship("Zawody", back_populates="uczestnicy")
    zawodnik = db.relationship("Zawodnik", backref="udzialy")
    stanowiska = db.relationship(
        "Stanowisko",
        back_populates="uczestnik",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        db.UniqueConstraint("zawody_id", "zawodnik_id", name="uq_uczestnik"),
    )

    def __repr__(self):
        return f"<Uczestnik {self.zawodnik_id} @ zawody {self.zawody_id}>"


class Stanowisko(db.Model):
    __tablename__ = "stanowiska"

    id = db.Column(db.Integer, primary_key=True)
    tura = db.Column(db.Integer, nullable=False, default=1)
    sektor = db.Column(db.String(8), nullable=False)
    numer = db.Column(db.Integer, nullable=False)

    zawody_id = db.Column(db.Integer, db.ForeignKey("zawody.id"), nullable=False)
    uczestnik_id = db.Column(db.Integer, db.ForeignKey("uczestnicy.id"), nullable=False)

    uczestnik = db.relationship("Uczestnik", back_populates="stanowiska")
    wynik_wagowy = db.relationship(
        "WynikWagowy",
        back_populates="stanowisko",
        uselist=False,
        cascade="all, delete-orphan",
    )
    wynik_karpie = db.relationship(
        "WynikKarpie",
        back_populates="stanowisko",
        uselist=False,
        cascade="all, delete-orphan",
    )
    wyniki_ryby = db.relationship(
        "WynikRyba",
        back_populates="stanowisko",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        db.UniqueConstraint(
            "zawody_id",
            "tura",
            "sektor",
            "numer",
            name="uq_stanowisko",
        ),
    )

    def __repr__(self):
        return f"<Stanowisko {self.sektor}{self.numer} tura {self.tura}>"


class WynikWagowy(db.Model):
    __tablename__ = "wyniki_wagowe"

    id = db.Column(db.Integer, primary_key=True)
    waga_g = db.Column(db.Integer, nullable=False, default=0)
    dyskwalifikacja = db.Column(db.Boolean, default=False)
    uwagi = db.Column(db.Text, nullable=True)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    stanowisko_id = db.Column(
        db.Integer, db.ForeignKey("stanowiska.id"), nullable=False
    )
    stanowisko = db.relationship("Stanowisko", back_populates="wynik_wagowy")

    def __repr__(self):
        return f"<WynikWagowy {self.waga_g}g>"


class WynikKarpie(db.Model):
    __tablename__ = "wyniki_karpie"

    id = db.Column(db.Integer, primary_key=True)
    liczba_sztuk = db.Column(db.Integer, nullable=False, default=0)
    waga_g = db.Column(db.Integer, nullable=False, default=0)
    najciezsza_g = db.Column(db.Integer, nullable=False, default=0)
    punkty_karne = db.Column(db.Integer, nullable=False, default=0)
    uwagi = db.Column(db.Text, nullable=True)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    stanowisko_id = db.Column(
        db.Integer, db.ForeignKey("stanowiska.id"), nullable=False
    )
    stanowisko = db.relationship("Stanowisko", back_populates="wynik_karpie")

    def __repr__(self):
        return f"<WynikKarpie {self.liczba_sztuk} szt. {self.waga_g}g>"


class WynikRyba(db.Model):
    __tablename__ = "wyniki_ryby"

    id = db.Column(db.Integer, primary_key=True)
    gatunek = db.Column(db.String(64), nullable=False)
    dlugosc_mm = db.Column(db.Integer, nullable=False)
    punkty = db.Column(db.Integer, nullable=False, default=0)
    zaliczona = db.Column(db.Boolean, default=True)
    uwagi = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    stanowisko_id = db.Column(
        db.Integer, db.ForeignKey("stanowiska.id"), nullable=False
    )
    stanowisko = db.relationship("Stanowisko", back_populates="wyniki_ryby")

    def __repr__(self):
        return f"<WynikRyba {self.gatunek} {self.dlugosc_mm}mm {self.punkty}pkt>"


class Dokument(db.Model):
    __tablename__ = "dokumenty"

    id = db.Column(db.Integer, primary_key=True)
    kod = db.Column(db.String(32), unique=True, nullable=False) # e.g., 'regulamin', 'polityka'
    tytul = db.Column(db.String(128), nullable=False)
    tresc = db.Column(db.Text, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<Dokument {self.kod} {self.tytul}>"

