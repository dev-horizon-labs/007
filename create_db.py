"""Tworzy bazę wypozyczalnia.db z schematem SQLite i realistycznymi danymi."""

import random
import sqlite3
from datetime import datetime, timedelta

random.seed(42)

DB_PATH = "data/wypozyczalnia.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS Oddzialy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nazwa TEXT NOT NULL,
    miasto TEXT NOT NULL,
    adres TEXT NOT NULL,
    telefon TEXT,
    aktywny INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS KategorieSamochodow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nazwa TEXT NOT NULL UNIQUE,
    opis TEXT,
    stawka_dzienna REAL NOT NULL CHECK (stawka_dzienna > 0)
);

CREATE TABLE IF NOT EXISTS Pracownicy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    imie TEXT NOT NULL,
    nazwisko TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    stanowisko TEXT NOT NULL,
    id_oddzialu INTEGER NOT NULL REFERENCES Oddzialy(id),
    data_zatrudnienia TEXT NOT NULL,
    id_przelozonego INTEGER REFERENCES Pracownicy(id),
    aktywny INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS Klienci (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    imie TEXT NOT NULL,
    nazwisko TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    telefon TEXT,
    data_urodzenia TEXT NOT NULL,
    nr_prawa_jazdy TEXT NOT NULL UNIQUE,
    data_rejestracji TEXT NOT NULL,
    usuniety_at TEXT
);

CREATE TABLE IF NOT EXISTS Samochody (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    marka TEXT NOT NULL,
    model TEXT NOT NULL,
    rok_produkcji INTEGER NOT NULL CHECK (rok_produkcji BETWEEN 1990 AND 2026),
    nr_rejestracyjny TEXT NOT NULL UNIQUE,
    kolor TEXT,
    id_kategorii INTEGER NOT NULL REFERENCES KategorieSamochodow(id),
    id_oddzialu INTEGER NOT NULL REFERENCES Oddzialy(id),
    status TEXT NOT NULL DEFAULT 'dostepny' CHECK (status IN ('dostepny', 'wypozyczony', 'serwis')),
    przebieg INTEGER NOT NULL DEFAULT 0 CHECK (przebieg >= 0)
);

CREATE TABLE IF NOT EXISTS Wypozyczenia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_klienta INTEGER NOT NULL REFERENCES Klienci(id),
    id_samochodu INTEGER NOT NULL REFERENCES Samochody(id),
    id_pracownika INTEGER NOT NULL REFERENCES Pracownicy(id),
    data_wypozyczenia TEXT NOT NULL,
    data_planowanego_zwrotu TEXT NOT NULL,
    data_faktycznego_zwrotu TEXT,
    km_wypozyczenie INTEGER NOT NULL,
    km_zwrot INTEGER,
    status TEXT NOT NULL DEFAULT 'aktywne' CHECK (status IN ('aktywne', 'zakonczone', 'anulowane')),
    kwota_calkowita REAL
);

CREATE TABLE IF NOT EXISTS Platnosci (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_wypozyczenia INTEGER NOT NULL REFERENCES Wypozyczenia(id),
    kwota REAL NOT NULL CHECK (kwota > 0),
    data_platnosci TEXT NOT NULL,
    metoda TEXT NOT NULL CHECK (metoda IN ('karta', 'gotowka', 'przelew')),
    status TEXT NOT NULL DEFAULT 'oczekujaca' CHECK (status IN ('oczekujaca', 'zrealizowana', 'anulowana'))
);

CREATE INDEX IF NOT EXISTS IX_Pracownicy_Oddzial ON Pracownicy(id_oddzialu);
CREATE INDEX IF NOT EXISTS IX_Samochody_Kategoria ON Samochody(id_kategorii);
CREATE INDEX IF NOT EXISTS IX_Samochody_Oddzial ON Samochody(id_oddzialu);
CREATE INDEX IF NOT EXISTS IX_Samochody_Status ON Samochody(status);
CREATE INDEX IF NOT EXISTS IX_Wypozyczenia_Klient ON Wypozyczenia(id_klienta);
CREATE INDEX IF NOT EXISTS IX_Wypozyczenia_Samochod ON Wypozyczenia(id_samochodu);
CREATE INDEX IF NOT EXISTS IX_Wypozyczenia_Status ON Wypozyczenia(status);
CREATE INDEX IF NOT EXISTS IX_Platnosci_Wypozyczenie ON Platnosci(id_wypozyczenia);
"""

# ── Dane seed ──────────────────────────────────────────────────────────

ODDZIALY = [
    ("Wypożyczalnia Płock Centrum", "Płock", "ul. Tumska 12", "24-262-00-01"),
    ("Wypożyczalnia Płock Południe", "Płock", "ul. Otolińska 25", "24-262-00-02"),
    ("Wypożyczalnia Warszawa Mokotów", "Warszawa", "ul. Puławska 145", "22-555-10-01"),
    ("Wypożyczalnia Warszawa Wola", "Warszawa", "ul. Kasprzaka 31", "22-555-10-02"),
    ("Wypożyczalnia Łódź Śródmieście", "Łódź", "ul. Piotrkowska 80", "42-630-00-01"),
    ("Wypożyczalnia Gdańsk Wrzeszcz", "Gdańsk", "ul. Grunwaldzka 99", "58-340-00-01"),
]

KATEGORIE = [
    ("Ekonomiczny", "Małe, oszczędne samochody miejskie", 120.00),
    ("Kompaktowy", "Średniej wielkości samochody do codziennego użytku", 180.00),
    ("SUV", "Samochody terenowe i crossovery", 280.00),
    ("Premium", "Luksusowe samochody wyższej klasy", 450.00),
    ("Dostawczy", "Samochody dostawcze i vany", 200.00),
    ("Elektryczny", "Samochody elektryczne i hybrydowe plug-in", 220.00),
]

IMIONA_M = ["Adam", "Bartosz", "Cezary", "Damian", "Emil", "Filip", "Grzegorz",
            "Hubert", "Igor", "Jakub", "Kamil", "Łukasz", "Marek", "Norbert",
            "Oskar", "Piotr", "Rafał", "Szymon", "Tomasz", "Wojciech",
            "Artur", "Dawid", "Jan", "Krzysztof", "Michał", "Paweł", "Robert",
            "Sebastian", "Wiktor", "Zbigniew"]
IMIONA_K = ["Anna", "Barbara", "Celina", "Dorota", "Ewa", "Fiona", "Grażyna",
            "Hanna", "Iwona", "Joanna", "Karolina", "Lucyna", "Małgorzata",
            "Natalia", "Olga", "Paulina", "Renata", "Sylwia", "Teresa", "Urszula",
            "Agnieszka", "Beata", "Danuta", "Elżbieta", "Katarzyna", "Magdalena",
            "Monika", "Patrycja", "Weronika", "Zofia"]
NAZWISKA_M = ["Nowak", "Kowalski", "Wiśniewski", "Wójcik", "Kowalczyk",
              "Kamiński", "Lewandowski", "Zieliński", "Szymański", "Woźniak",
              "Dąbrowski", "Kozłowski", "Jankowski", "Mazur", "Kwiatkowski",
              "Krawczyk", "Piotrowski", "Grabowski", "Pawlak", "Michalski",
              "Zając", "Król", "Jabłoński", "Wieczorek", "Majewski",
              "Olszewski", "Stępień", "Malinowski", "Jaworski", "Adamczyk"]
NAZWISKA_K = ["Nowak", "Kowalska", "Wiśniewska", "Wójcik", "Kowalczyk",
              "Kamińska", "Lewandowska", "Zielińska", "Szymańska", "Woźniak",
              "Dąbrowska", "Kozłowska", "Jankowska", "Mazur", "Kwiatkowska",
              "Krawczyk", "Piotrowska", "Grabowska", "Pawlak", "Michalska",
              "Zając", "Król", "Jabłońska", "Wieczorek", "Majewska",
              "Olszewska", "Stępień", "Malinowska", "Jaworska", "Adamczyk"]

STANOWISKA = ["Kierownik oddziału", "Konsultant", "Konsultant", "Konsultant", "Mechanik"]

MARKI_MODELE = {
    "Ekonomiczny": [
        ("Toyota", "Yaris"), ("Fiat", "500"), ("Opel", "Corsa"),
        ("Volkswagen", "Polo"), ("Skoda", "Fabia"), ("Hyundai", "i20"),
        ("Renault", "Clio"), ("Peugeot", "208"), ("Kia", "Rio"),
    ],
    "Kompaktowy": [
        ("Toyota", "Corolla"), ("Volkswagen", "Golf"), ("Skoda", "Octavia"),
        ("Ford", "Focus"), ("Mazda", "3"), ("Hyundai", "i30"),
        ("Opel", "Astra"), ("Kia", "Ceed"), ("Peugeot", "308"),
    ],
    "SUV": [
        ("Toyota", "RAV4"), ("Volkswagen", "Tiguan"), ("Skoda", "Kodiaq"),
        ("Hyundai", "Tucson"), ("Kia", "Sportage"), ("Ford", "Kuga"),
        ("Mazda", "CX-5"), ("Nissan", "Qashqai"), ("Peugeot", "3008"),
    ],
    "Premium": [
        ("BMW", "Seria 5"), ("Mercedes", "Klasa E"), ("Audi", "A6"),
        ("Volvo", "S90"), ("BMW", "Seria 3"), ("Mercedes", "Klasa C"),
        ("Audi", "A4"), ("Lexus", "ES"),
    ],
    "Dostawczy": [
        ("Renault", "Kangoo"), ("Volkswagen", "Caddy"), ("Ford", "Transit Connect"),
        ("Fiat", "Doblo"), ("Opel", "Combo"), ("Peugeot", "Partner"),
        ("Citroen", "Berlingo"), ("Mercedes", "Citan"),
    ],
    "Elektryczny": [
        ("Tesla", "Model 3"), ("Volkswagen", "ID.3"), ("Hyundai", "Ioniq 5"),
        ("Kia", "EV6"), ("BMW", "iX3"), ("Nissan", "Leaf"),
        ("Renault", "Megane E-Tech"), ("Skoda", "Enyaq"),
    ],
}

KOLORY = ["biały", "czarny", "srebrny", "szary", "czerwony", "niebieski",
          "granatowy", "zielony", "brązowy", "beżowy"]

DOMENY = ["gmail.com", "wp.pl", "onet.pl", "o2.pl", "interia.pl", "outlook.com"]


def rand_date(start: str, end: str) -> str:
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.strptime(end, "%Y-%m-%d")
    d = s + timedelta(days=random.randint(0, (e - s).days))
    return d.strftime("%Y-%m-%d")


def rand_datetime(start: str, end: str) -> str:
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.strptime(end, "%Y-%m-%d")
    d = s + timedelta(seconds=random.randint(0, int((e - s).total_seconds())))
    return d.strftime("%Y-%m-%d %H:%M:%S")


def rand_phone() -> str:
    return f"{random.randint(500,899)}-{random.randint(100,999)}-{random.randint(100,999)}"


def rand_plate() -> str:
    letters = "ABCDEFGHIJKLMNOPRSTUWZ"
    prefix = random.choice(["WP", "WA", "EL", "GD", "WE", "WI", "EP"])
    return f"{prefix} {random.randint(10000, 99999)}{random.choice(letters)}"


def rand_license() -> str:
    return f"{random.randint(10000, 99999)}/{random.randint(10, 99)}/{random.randint(1000, 9999)}"


def main():
    import os
    os.makedirs("data", exist_ok=True)

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)

    # ── Oddziały ───────────────────────────────────────────────────
    for nazwa, miasto, adres, tel in ODDZIALY:
        conn.execute(
            "INSERT INTO Oddzialy (nazwa, miasto, adres, telefon) VALUES (?, ?, ?, ?)",
            (nazwa, miasto, adres, tel),
        )
    num_oddzialow = len(ODDZIALY)

    # ── Kategorie ──────────────────────────────────────────────────
    for nazwa, opis, stawka in KATEGORIE:
        conn.execute(
            "INSERT INTO KategorieSamochodow (nazwa, opis, stawka_dzienna) VALUES (?, ?, ?)",
            (nazwa, opis, stawka),
        )
    num_kategorii = len(KATEGORIE)

    # ── Pracownicy (~30) ───────────────────────────────────────────
    pracownik_id = 0
    kierownicy = []
    used_emails_p = set()

    for oddzial_id in range(1, num_oddzialow + 1):
        for i, stanowisko in enumerate(STANOWISKA):
            is_male = random.random() < 0.6
            imie = random.choice(IMIONA_M if is_male else IMIONA_K)
            nazwisko = random.choice(NAZWISKA_M if is_male else NAZWISKA_K)
            email = f"{imie.lower()}.{nazwisko.lower()}@wypozyczalnia.pl"
            while email in used_emails_p:
                email = f"{imie.lower()}.{nazwisko.lower()}{random.randint(1,99)}@wypozyczalnia.pl"
            used_emails_p.add(email)

            data_zatr = rand_date("2018-01-01", "2025-06-01")
            przelozony = kierownicy[-1] if (i > 0 and kierownicy) else None

            conn.execute(
                """INSERT INTO Pracownicy
                   (imie, nazwisko, email, stanowisko, id_oddzialu, data_zatrudnienia, id_przelozonego)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (imie, nazwisko, email, stanowisko, oddzial_id, data_zatr, przelozony),
            )
            pracownik_id += 1
            if stanowisko == "Kierownik oddziału":
                kierownicy.append(pracownik_id)

    num_pracownikow = pracownik_id

    # ── Klienci (120) ──────────────────────────────────────────────
    used_emails_k = set()
    used_licenses = set()
    num_klientow = 120

    for _ in range(num_klientow):
        is_male = random.random() < 0.55
        imie = random.choice(IMIONA_M if is_male else IMIONA_K)
        nazwisko = random.choice(NAZWISKA_M if is_male else NAZWISKA_K)
        domena = random.choice(DOMENY)
        email = f"{imie.lower()}.{nazwisko.lower()}@{domena}"
        while email in used_emails_k:
            email = f"{imie.lower()}.{nazwisko.lower()}{random.randint(1,999)}@{domena}"
        used_emails_k.add(email)

        nr_pj = rand_license()
        while nr_pj in used_licenses:
            nr_pj = rand_license()
        used_licenses.add(nr_pj)

        data_ur = rand_date("1965-01-01", "2002-12-31")
        data_rej = rand_datetime("2020-01-01", "2026-04-01")
        usuniety = None
        if random.random() < 0.05:
            usuniety = rand_datetime("2025-01-01", "2026-05-01")

        conn.execute(
            """INSERT INTO Klienci
               (imie, nazwisko, email, telefon, data_urodzenia, nr_prawa_jazdy, data_rejestracji, usuniety_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (imie, nazwisko, email, rand_phone(), data_ur, nr_pj, data_rej, usuniety),
        )

    # ── Samochody (80) ─────────────────────────────────────────────
    used_plates = set()
    num_samochodow = 80
    kategorie_nazwy = [k[0] for k in KATEGORIE]

    for _ in range(num_samochodow):
        kat_id = random.randint(1, num_kategorii)
        kat_nazwa = kategorie_nazwy[kat_id - 1]
        marka, model = random.choice(MARKI_MODELE[kat_nazwa])
        rok = random.randint(2018, 2025)
        plate = rand_plate()
        while plate in used_plates:
            plate = rand_plate()
        used_plates.add(plate)
        kolor = random.choice(KOLORY)
        oddzial = random.randint(1, num_oddzialow)
        status = random.choices(["dostepny", "wypozyczony", "serwis"], weights=[60, 30, 10])[0]
        przebieg = random.randint(5000, 180000)

        conn.execute(
            """INSERT INTO Samochody
               (marka, model, rok_produkcji, nr_rejestracyjny, kolor, id_kategorii, id_oddzialu, status, przebieg)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (marka, model, rok, plate, kolor, kat_id, oddzial, status, przebieg),
        )

    # ── Wypożyczenia (300) ─────────────────────────────────────────
    num_wypozyczen = 300

    for _ in range(num_wypozyczen):
        klient_id = random.randint(1, num_klientow)
        samochod_id = random.randint(1, num_samochodow)
        pracownik_id = random.randint(1, num_pracownikow)

        data_wyp = rand_datetime("2024-01-01", "2026-05-15")
        dni = random.choices([1, 2, 3, 5, 7, 14, 21], weights=[10, 20, 25, 20, 15, 7, 3])[0]
        data_plan = (datetime.strptime(data_wyp, "%Y-%m-%d %H:%M:%S") + timedelta(days=dni)).strftime("%Y-%m-%d %H:%M:%S")

        km_wyp = random.randint(5000, 180000)

        r = random.random()
        if r < 0.65:
            opoznienie = random.randint(-1, 3)
            data_fakt = (datetime.strptime(data_plan, "%Y-%m-%d %H:%M:%S") + timedelta(days=opoznienie)).strftime("%Y-%m-%d %H:%M:%S")
            km_zwr = km_wyp + random.randint(50, 2000)
            status = "zakonczone"
            kat_id_sam = conn.execute("SELECT id_kategorii FROM Samochody WHERE id = ?", (samochod_id,)).fetchone()[0]
            stawka = conn.execute("SELECT stawka_dzienna FROM KategorieSamochodow WHERE id = ?", (kat_id_sam,)).fetchone()[0]
            kwota = round(stawka * dni * random.uniform(0.9, 1.1), 2)
        elif r < 0.85:
            data_fakt = None
            km_zwr = None
            status = "aktywne"
            kwota = None
        else:
            data_fakt = None
            km_zwr = None
            status = "anulowane"
            kwota = None

        conn.execute(
            """INSERT INTO Wypozyczenia
               (id_klienta, id_samochodu, id_pracownika, data_wypozyczenia,
                data_planowanego_zwrotu, data_faktycznego_zwrotu,
                km_wypozyczenie, km_zwrot, status, kwota_calkowita)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (klient_id, samochod_id, pracownik_id, data_wyp, data_plan,
             data_fakt, km_wyp, km_zwr, status, kwota),
        )

    # ── Płatności (dla zakończonych wypożyczeń) ────────────────────
    zakonczenia = conn.execute(
        "SELECT id, kwota_calkowita, data_faktycznego_zwrotu FROM Wypozyczenia WHERE status = 'zakonczone'"
    ).fetchall()

    for wyp_id, kwota, data_zwrotu in zakonczenia:
        if kwota is None:
            continue
        metoda = random.choice(["karta", "karta", "karta", "przelew", "gotowka"])

        if random.random() < 0.9:
            plat_status = "zrealizowana"
        else:
            plat_status = "oczekujaca"

        data_plat = data_zwrotu or rand_datetime("2024-01-01", "2026-05-15")

        conn.execute(
            """INSERT INTO Platnosci
               (id_wypozyczenia, kwota, data_platnosci, metoda, status)
               VALUES (?, ?, ?, ?, ?)""",
            (wyp_id, kwota, data_plat, metoda, plat_status),
        )

    conn.commit()

    # ── Raport ─────────────────────────────────────────────────────
    tables = ["Oddzialy", "KategorieSamochodow", "Pracownicy", "Klienci",
              "Samochody", "Wypozyczenia", "Platnosci"]
    print("Baza utworzona:", DB_PATH)
    for t in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t}: {count} rekordów")

    conn.close()


if __name__ == "__main__":
    main()
