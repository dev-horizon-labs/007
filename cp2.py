"""
CP2: Structured Output
======================

Ten plik ma DWIE sekcje:

  1. MINI PRZYKŁAD — Structured Output z jednym polem (TinyReport).
  2. TWOJE ZADANIE — rozbuduj do pełnego RentalReport.

Uruchom: python cp2.py
"""

import json

from pydantic import BaseModel, Field

from lib.common import MODEL, SCHEMA_DDL
from lib.db import client, execute_query


# ════════════════════════════════════════════════════════════════════════
# Dane testowe — wynik z bazy (hardcoded, żeby skupić się na SO)
# ════════════════════════════════════════════════════════════════════════

TEST_QUESTION = "Ile samochodów jest dostępnych w podziale na kategorie?"
TEST_SQL = """
    SELECT k.nazwa AS kategoria, COUNT(*) AS liczba, k.stawka_dzienna
    FROM Samochody s
    JOIN KategorieSamochodow k ON s.id_kategorii = k.id
    WHERE s.status = 'dostepny'
    GROUP BY k.nazwa
"""
TEST_DATA = execute_query(TEST_SQL)


# ════════════════════════════════════════════════════════════════════════
# SEKCJA 1: MINI PRZYKŁAD — Structured Output
#
# Najprostszy model Pydantic: jedno pole. API gwarantuje format.
# ════════════════════════════════════════════════════════════════════════


class TinyReport(BaseModel):
    title: str = Field(..., description="Tytuł raportu po polsku")


def mini_example(question: str, raw_data: list[dict]) -> TinyReport:
    """MINI PRZYKŁAD: Structured Output z jednym polem."""
    result = client.beta.chat.completions.parse(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "Formatujesz dane z bazy wypożyczalni samochodów w raport.",
            },
            {
                "role": "user",
                "content": f"Pytanie: {question}\n\nDane:\n{json.dumps(raw_data, ensure_ascii=False)}",
            },
        ],
        response_format=TinyReport,
    )
    return result.choices[0].message.parsed


# ════════════════════════════════════════════════════════════════════════
# SEKCJA 2: TWOJE ZADANIE
#
# Rozbuduj TinyReport do pełnego modelu raportu:
#
# 1. Stwórz model ReportRow z polami:
#    - label (str) — nazwa wiersza, np. "SUV", "Jan Kowalski"
#    - value (str) — wartość główna, np. "5", "3420 PLN"
#    - detail (str) — dodatkowa informacja, np. "280 PLN/dzień"
#
# 2. Stwórz model RentalReport z polami:
#    - title (str) — tytuł raportu
#    - main_value (str) — główna odpowiedź, np. "49 samochodów"
#    - rows (list[ReportRow]) — rozbicie danych w tabelę
#    - summary (str) — 1-2 zdania podsumowania
#    - sql_used (str) — zapytanie SQL użyte do pobrania danych
#
# 3. Napisz funkcję good_report() która używa response_format=RentalReport
#
# Podpowiedzi:
# - Użyj Field(description=...) żeby powiedzieć modelowi co wpisać w każde pole
# - Wzoruj się na mini_example() — zmień tylko model Pydantic i dodaj pola
# ════════════════════════════════════════════════════════════════════════


# TODO: Zdefiniuj ReportRow(BaseModel)
# class ReportRow(BaseModel):
#     ...


# TODO: Zdefiniuj RentalReport(BaseModel)
# class RentalReport(BaseModel):
#     ...


# TODO: Napisz funkcję good_report(question, raw_data, sql_used) -> RentalReport
# def good_report(question: str, raw_data: list[dict], sql_used: str) -> RentalReport:
#     ...


# ════════════════════════════════════════════════════════════════════════
# Uruchamianie
# ════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("SEKCJA 1: MINI PRZYKŁAD — Structured Output")
    print("=" * 60)
    tiny = mini_example(TEST_QUESTION, TEST_DATA)
    print(f"Tytuł: {tiny.title}")
    print(f"Typ:   {type(tiny).__name__} (Pythonowy obiekt, nie tekst!)")

    # print("\n" + "=" * 60)
    # print("SEKCJA 2: TWOJE ROZWIĄZANIE")
    # print("=" * 60)
    # report = good_report(TEST_QUESTION, TEST_DATA, TEST_SQL)
    # print(f"Tytuł:  {report.title}")
    # print(f"Główna: {report.main_value}")
    # for row in report.rows:
    #     print(f"  {row.label}: {row.value} ({row.detail})")
    # print(f"Summary: {report.summary}")
    # print(f"SQL:     {report.sql_used}")
