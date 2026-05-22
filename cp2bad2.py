"""
CP2 — ANTYWZORZEC: Sprzeczne instrukcje
=========================================

Model ma wyjaśnić wnioski I jednocześnie zwrócić czysty JSON.
Uruchom KILKA RAZY — czy json.loads() zawsze działa?

Uruchom: python cp2bad2.py
"""

import json

from lib.common import MODELS
from lib.db import client, execute_query


TEST_QUESTION = "Ile samochodów jest dostępnych w podziale na kategorie?"
TEST_SQL = """
    SELECT k.nazwa AS kategoria, COUNT(*) AS liczba, k.stawka_dzienna
    FROM Samochody s
    JOIN KategorieSamochodow k ON s.id_kategorii = k.id
    WHERE s.status = 'dostepny'
    GROUP BY k.nazwa
"""
TEST_DATA = execute_query(TEST_SQL)


def bad_report_v2(question: str, raw_data: list[dict]) -> dict:
    """ANTYWZORZEC: sprzeczne instrukcje — model wyjaśnia I zwraca JSON."""
    response = client.chat.completions.create(
        model=MODELS.gpt_4o_mini,
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
    return json.loads(text)


if __name__ == "__main__":
    print("=" * 60)
    print("ANTYWZORZEC: Sprzeczne instrukcje")
    print("Prompt mówi: 'wyjaśnij wnioski' + 'podaj JSON' — co wygra?")
    print("Sprawdź logi — czy model zwrócił TYLKO JSON?")
    print("=" * 60)
    try:
        report = bad_report_v2(TEST_QUESTION, TEST_DATA)
        print(f"Tytuł:  {report['title']}")
        print(f"Główna: {report['main_value']}")
        for row in report["rows"]:
            print(f"  {row['label']}: {row['value']} ({row.get('detail', '')})")
        print(f"Summary: {report['summary']}")
    except json.JSONDecodeError:
        print("\n✗ json.loads() FAIL — model zwrócił tekst + JSON zamiast czystego JSON-a.")
        print("  Sprzeczne instrukcje ('wyjaśnij' + 'podaj JSON') = model próbuje oba naraz.")
        print("  Sprawdź logi (cp2bad2.logs.txt) żeby zobaczyć co dokładnie zwrócił.")
