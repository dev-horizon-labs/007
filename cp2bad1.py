"""
CP2 — ANTYWZORZEC: Luźna instrukcja JSON
==========================================

Model dostaje luźną instrukcję "sformatuj jako JSON" — bez schematu.
Skrypt wywołuje model 3 razy i porównuje klucze w odpowiedziach.

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
    """ANTYWZORZEC: luźna instrukcja — model sam wymyśla strukturę JSON."""
    response = client.chat.completions.create(
        model=MODELS.gpt_4o_mini,
        messages=[
            {
                "role": "system",
                "content": "Odpowiedz na pytanie o wypożyczalnię samochodów. Sformatuj odpowiedź jako JSON.",
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


def extract_keys(obj, prefix="") -> set[str]:
    """Rekurencyjnie zbiera ścieżki kluczy z JSON-a."""
    keys = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            path = f"{prefix}.{k}" if prefix else k
            keys.add(path)
            keys |= extract_keys(v, path)
    elif isinstance(obj, list) and obj:
        keys |= extract_keys(obj[0], f"{prefix}[]")
    return keys


if __name__ == "__main__":
    print("=" * 60)
    print("ANTYWZORZEC: Luźna instrukcja JSON")
    print("5 wywołań tego samego promptu — porównanie struktur")
    print("=" * 60)

    results = []
    for i in range(5):
        try:
            report = bad_report_v1(TEST_QUESTION, TEST_DATA)
            keys = extract_keys(report)
            results.append(keys)
            print(f"\nRun {i + 1} — klucze: {sorted(keys)}")
        except json.JSONDecodeError as e:
            results.append(None)
            print(f"\nRun {i + 1} — json.loads() FAIL: {e}")

    valid = [r for r in results if r is not None]
    if len(valid) >= 2 and len(set(frozenset(r) for r in valid)) > 1:
        print("\n✗ Struktury się RÓŻNIĄ między wywołaniami!")
        print("  Bez schematu nie masz gwarancji, że kod parsujący zadziała.")
    elif len(valid) >= 2:
        print("\n⚠ Tym razem struktury się zgadzają — ale nie ma gwarancji.")
        print("  Uruchom jeszcze raz albo zmień pytanie.")
