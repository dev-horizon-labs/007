from enum import StrEnum


# ── Dostępne modele LLM ──────────────────────────────────────────────
# Tutaj definiujemy nazwy modeli OpenAI dostępnych na warsztacie.
# Żeby zmienić model w dowolnym checkpoincie, zamień np.:
#   model=MODELS.gpt_4o_mini  →  model=MODELS.gpt_4_1_mini
# Pełna lista modeli OpenAI: https://platform.openai.com/docs/models
# ────────────────────────────────────────────────────────────────────
class MODELS(StrEnum):
    gpt_4o_mini = "gpt-4o-mini"
    gpt_4_1_mini = "gpt-4.1-mini"
    gpt_4_1_nano = "gpt-4.1-nano"
    gpt_5_mini = "gpt-5-mini"
    gpt_5_nano = "gpt-5-nano"
    gpt_5_4_mini = "gpt-5.4-mini"
    gpt_5_4_nano = "gpt-5.4-nano"



SCHEMA_DDL = """
Baza: SQLite

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
