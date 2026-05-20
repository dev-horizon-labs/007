"""
CP2: Structured Output
======================

Ten plik ma TRZY sekcje:

  1. ANTYWZORZEC  — json.loads() na tekście LLM. Uruchom KILKA RAZY.
  2. MINI PRZYKŁAD — Structured Output z jednym polem (TinyReport).
  3. TWOJE ZADANIE — rozbuduj do pełnego RentalReport.

Uruchom: python cp2.py
"""

import json

from pydantic import BaseModel, Field

from lib.db import SCHEMA_DDL, client, MODEL, execute_query


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
# SEKCJA 1: ANTYWZORZEC — json.loads() na tekście LLM
#
# Dwa warianty — oba próbują wyciągnąć JSON z tekstu modelu.
# Uruchom KILKA RAZY. Czy za każdym razem działa?
#
# v1: luźna instrukcja — model owija JSON w markdown lub dodaje tekst
# v2: sprzeczne instrukcje — model wyjaśnia I zwraca JSON naraz
# ════════════════════════════════════════════════════════════════════════


def bad_report_v1(question: str, raw_data: list[dict]) -> dict:
    """ANTYWZORZEC v1: luźna instrukcja — model owija JSON w markdown lub dodaje tekst."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": """Odpowiedz na pytanie o wypożyczalnię samochodów.
Sformatuj odpowiedź jako JSON z polami: title, main_value, rows, summary.""",
            },
            {
                "role": "user",
                "content": f"Pytanie: {question}\n\nDane:\n{json.dumps(raw_data, ensure_ascii=False)}",
            },
        ],
    )

    text = response.choices[0].message.content

    # Odkomentuj żeby zobaczyć co model naprawdę zwraca:
    # print(f">>> Surowy tekst z modelu:\n{text}\n<<<")

    return json.loads(text)


def bad_report_v2(question: str, raw_data: list[dict]) -> dict:
    """ANTYWZORZEC v2: sprzeczne instrukcje — model wyjaśnia I zwraca JSON."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": """Jesteś analitykiem wypożyczalni samochodów.
Odpowiedz na pytanie użytkownika. Wyjaśnij swoje wnioski i podaj dane.
Dane podaj w formacie JSON: {title, main_value, rows: [{label, value, detail}], summary}""",
            },
            {
                "role": "user",
                "content": f"Pytanie: {question}\n\nDane:\n{json.dumps(raw_data, ensure_ascii=False)}",
            },
        ],
    )

    text = response.choices[0].message.content

    # Odkomentuj żeby zobaczyć co model naprawdę zwraca:
    # print(f">>> Surowy tekst z modelu:\n{text}\n<<<")

    return json.loads(text)


# ════════════════════════════════════════════════════════════════════════
# SEKCJA 2: MINI PRZYKŁAD — Structured Output
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
# SEKCJA 3: TWOJE ZADANIE
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
    for name, fn in [("v1 (luźna instrukcja)", bad_report_v1), ("v2 (sprzeczne instrukcje)", bad_report_v2)]:
        print("=" * 60)
        print(f"SEKCJA 1: ANTYWZORZEC {name}")
        print("Uruchom kilka razy — czy zawsze działa?")
        print("=" * 60)
        try:
            report = fn(TEST_QUESTION, TEST_DATA)
            print(f"Tytuł:  {report['title']}")
            print(f"Główna: {report['main_value']}")
            for row in report["rows"]:
                print(f"  {row['label']}: {row['value']} ({row.get('detail', '')})")
            print(f"Summary: {report['summary']}")
        except json.JSONDecodeError as e:
            print(f"BŁĄD PARSOWANIA: {e}")
            print("Model nie zwrócił czystego JSON-a.")
            print("Odkomentuj print() w bad_report_*() żeby zobaczyć co zwrócił.")
        except KeyError as e:
            print(f"BRAK POLA: {e}")
            print("Model zwrócił JSON, ale z innymi nazwami pól.")
        print()

    print("\n" + "=" * 60)
    print("SEKCJA 2: MINI PRZYKŁAD — Structured Output")
    print("=" * 60)
    tiny = mini_example(TEST_QUESTION, TEST_DATA)
    print(f"Tytuł: {tiny.title}")
    print(f"Typ:   {type(tiny).__name__} (Pythonowy obiekt, nie tekst!)")

    # print("\n" + "=" * 60)
    # print("SEKCJA 3: TWOJE ROZWIĄZANIE")
    # print("=" * 60)
    # report = good_report(TEST_QUESTION, TEST_DATA, TEST_SQL)
    # print(f"Tytuł:  {report.title}")
    # print(f"Główna: {report.main_value}")
    # for row in report.rows:
    #     print(f"  {row.label}: {row.value} ({row.detail})")
    # print(f"Summary: {report.summary}")
    # print(f"SQL:     {report.sql_used}")
