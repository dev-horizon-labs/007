"""
CP1 — ANTYWZORZEC: Prompt Stuffing
===================================

Kod wrzuca WSZYSTKIE dane z bazy do promptu.
Uruchom i sprawdź odpowiedzi — czy są poprawne?

Uruchom: python cp1bad.py
"""

import sqlite3

from lib.common import MODEL
from lib.db import DB_PATH, client


def get_all_data() -> str:
    """Pobiera WSZYSTKIE dane z bazy i zwraca jako tekst."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    tables = [
        "Oddzialy", "KategorieSamochodow", "Samochody",
        "Klienci", "Pracownicy", "Wypozyczenia", "Platnosci",
    ]
    dump = ""
    for table in tables:
        rows = conn.execute(f"SELECT * FROM {table}").fetchall()
        dump += f"\n=== {table} ({len(rows)} wierszy) ===\n"
        for row in rows:
            dump += str(dict(row)) + "\n"
    conn.close()
    return dump


def bad_ask(question: str) -> str:
    """ANTYWZORZEC: wrzuca wszystkie dane do promptu."""
    all_data = get_all_data()

    # Odkomentuj żeby zobaczyć ile tekstu leci do modelu:
    # print(f">>> Rozmiar danych w prompcie: {len(all_data)} znaków")

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": f"""Jesteś asystentem wypożyczalni samochodów.
Oto WSZYSTKIE dane z naszej bazy:

{all_data}

Odpowiedz na pytanie użytkownika. Odpowiadaj po polsku, krótko i na temat.""",
            },
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    questions = [
        "Ile samochodów jest dostępnych w Płocku?",
        "Który klient wypożyczył najwięcej samochodów?",
        "Jaka jest średnia stawka dzienna w kategorii SUV?",
    ]

    print("=" * 60)
    print("ANTYWZORZEC: Prompt Stuffing")
    print("Wszystkie dane z bazy lecą do promptu.")
    print("=" * 60)
    for q in questions:
        print(f"\nQ: {q}")
        print(f"A: {bad_ask(q)}")
