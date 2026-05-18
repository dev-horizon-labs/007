import os
import sqlite3

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "wypozyczalnia.db")

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY", "not-needed"),
    base_url=os.environ["OPENAI_BASE_URL"],
)
MODEL = "gpt-4o-mini"

SCHEMA_DDL = """
Oddzialy(id, nazwa, miasto, adres, telefon, aktywny)
KategorieSamochodow(id, nazwa, opis, stawka_dzienna)
Pracownicy(id, imie, nazwisko, email, stanowisko, id_oddzialu, data_zatrudnienia, id_przelozonego, aktywny)
Klienci(id, imie, nazwisko, email, telefon, data_urodzenia, nr_prawa_jazdy, data_rejestracji, usuniety_at)
Samochody(id, marka, model, rok_produkcji, nr_rejestracyjny, kolor, id_kategorii, id_oddzialu, status, przebieg)
  status IN ('dostepny', 'wypozyczony', 'serwis')
  FK: id_kategorii -> KategorieSamochodow, id_oddzialu -> Oddzialy
Wypozyczenia(id, id_klienta, id_samochodu, id_pracownika, data_wypozyczenia, data_planowanego_zwrotu, data_faktycznego_zwrotu, km_wypozyczenie, km_zwrot, status, kwota_calkowita)
  status IN ('aktywne', 'zakonczone', 'anulowane')
  FK: id_klienta -> Klienci, id_samochodu -> Samochody, id_pracownika -> Pracownicy
Platnosci(id, id_wypozyczenia, kwota, data_platnosci, metoda, status)
  metoda IN ('karta', 'gotowka', 'przelew')
  status IN ('oczekujaca', 'zrealizowana', 'anulowana')
"""


def validate_sql(sql: str) -> bool:
    normalized = sql.strip().upper()
    if not normalized.startswith("SELECT"):
        return False
    forbidden = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE"]
    return not any(kw in normalized for kw in forbidden)


def execute_query(sql: str) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(sql).fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        return [{"error": str(e)}]
    finally:
        conn.close()
