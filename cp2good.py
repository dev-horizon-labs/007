"""
CP2: Structured Output
======================

Ten plik ma DWIE sekcje:

  1. MINI PRZYKŁAD — Structured Output z jednym polem (TinyReport).
  2. TWOJE ZADANIE — odkomentuj pełny RentalReport.

Uruchom: python cp2good.py
"""

import json

from pydantic import BaseModel, Field

from lib.common import MODELS
from lib.db import client, execute_query


# ════════════════════════════════════════════════════════════════════════
# Dane testowe — wynik zapytania SQL wpisany bezpośrednio w kod,
# żeby skupić się na nauce Structured Output, a nie na pisaniu SQL.
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
    # .parse() to gotowy wrapper — automatycznie konwertuje response na obiekt Pydantic (.parsed).
    # Jeśli chcesz sam to napisać, to ścieżka bez .parse(): 
    # client.chat.completions.create() + json.loads() + Model(**data)
    # Docs: https://developers.openai.com/api/docs/guides/structured-outputs

    # ── PROMPT SYSTEMOWY — tu definiujesz rolę i kontekst dla modelu ────
    system_content = "Formatujesz dane z bazy wypożyczalni samochodów w raport."
    # ────────────────────────────────────────────────────────────────────

    result = client.chat.completions.parse(
        model=MODELS.gpt_4o_mini,
        messages=[
            {
                "role": "system",
                "content": system_content,
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
# Odkomentuj oznaczone bloki i uruchom w terminalu komendę:
#
# python cp2good.py
#
# ════════════════════════════════════════════════════════════════════════


## ── ODKOMENTUJ PONIŻEJ ──
## ReportRow - model Pydantic przedstawiający jeden wiersz raportu

# class ReportRow(BaseModel):
#     label: str = Field(..., description="Nazwa wiersza, np. 'SUV', 'Jan Kowalski'")
#     value: str = Field(..., description="Wartość główna, np. '5', '3420 PLN'")
#     detail: str = Field(..., description="Dodatkowa informacja, np. '280 PLN/dzień'")

## ── KONIEC ──


## ── ODKOMENTUJ PONIŻEJ ──
## RentalReport - model Pydantic przedstawiający pełny raport

# class RentalReport(BaseModel):
#     title: str = Field(..., description="Tytuł raportu po polsku")
#     main_value: str = Field(..., description="Główna odpowiedź, np. '49 samochodów'")
#     rows: list[ReportRow] = Field(..., description="Rozbicie danych w tabelę")
#     summary: str = Field(..., description="1-2 zdania podsumowania")
#     sql_used: str = Field(..., description="Zapytanie SQL użyte do pobrania danych")

## ── KONIEC ──


## ── ODKOMENTUJ PONIŻEJ ──
## full_report() - funkcja, która używa response_format=RentalReport i zwraca RentalReport


# def full_report(question: str, raw_data: list[dict], sql_used: str) -> RentalReport:
#     result = client.chat.completions.parse(
#         model=MODELS.gpt_4o_mini,
#         messages=[
#             {
#                 "role": "system",
#                 "content": "Formatujesz dane z bazy wypożyczalni samochodów w raport.",
#             },
#             {
#                 "role": "user",
#                 "content": f"Pytanie: {question}\n\nDane:\n{json.dumps(raw_data, ensure_ascii=False)}\n\nSQL:\n{sql_used}",
#             },
#         ],
#         response_format=RentalReport,
#     )
#     return result.choices[0].message.parsed

## ── KONIEC ──


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
    # report = full_report(TEST_QUESTION, TEST_DATA, TEST_SQL)
    # print(f"Tytuł:  {report.title}")
    # print(f"Główna: {report.main_value}")
    # for row in report.rows:
    #     print(f"  {row.label}: {row.value} ({row.detail})")
    # print(f"Summary: {report.summary}")
    # print(f"SQL:     {report.sql_used}")

# ════════════════════════════════════════════════════════════════════════
# BONUS
# ════════════════════════════════════════════════════════════════════════
#
# 1. Dodaj pole trend: str do ReportRow (np. '↑', '↓', '→')
#    Jak model je wypełni bez dodatkowych informacji?
#
# 2. Zmień opisy w Field(description=...) na angielskie — czy model
#    dalej odpowiada po polsku?
#
# 3. Dodaj do ReportRow pole action_hint: str.
#    Niech model dla każdego wiersza zaproponuje krótką decyzję biznesową,
#    np. "promować", "dokupić", "sprawdzić ceny", ale tylko na podstawie danych wejściowych.