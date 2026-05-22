"""
CP2 — ANTYWZORZEC: Luźna instrukcja JSON
==========================================

Model dostaje luźną instrukcję "sformatuj jako JSON".
Uruchom KILKA RAZY — czy json.loads() zawsze działa?

Uruchom: python cp2bad1.py
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


def bad_report_v1(question: str, raw_data: list[dict]) -> dict:
    """ANTYWZORZEC: luźna instrukcja — model owija JSON w markdown lub dodaje tekst."""
    response = client.chat.completions.create(
        model=MODELS.gpt_4o_mini,
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
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(text)


if __name__ == "__main__":
    print("=" * 60)
    print("ANTYWZORZEC: Luźna instrukcja JSON")
    print("Uruchom kilka razy — czy nazwy pól są zawsze takie same?")
    print("Sprawdź logi — jak model interpretuje 'sformatuj jako JSON'?")
    print("=" * 60)
    try:
        report = bad_report_v1(TEST_QUESTION, TEST_DATA)
    except (json.JSONDecodeError, KeyError) as e:
        print(f"\n✗ json.loads() / dostęp do pól nie zadziałał: {e}")
        print("  Uruchom jeszcze raz — wynik może być inny za każdym razem.")
        raise SystemExit(1)

    print(f"Tytuł:  {report.get('title', '???')}")
    print(f"Główna: {report.get('main_value', '???')}")
    for row in report.get("rows", []):
        print(f"  {row.get('label', '???')}: {row.get('value', '???')} ({row.get('detail', '')})")
    print(f"Summary: {report.get('summary', '???')}")
    print("\n⚠ Zadziałało tym razem — ale czy nazwy pól zawsze będą takie same?")
