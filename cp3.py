"""
CP3: Pipeline
=============

Łączysz Function Calling (CP1) ze Structured Output (CP2).
Model odpytuje bazę → formatuje wynik → zapisuje raport do pliku markdown.

Uruchom: python cp3.py
"""

import json
import os

from lib.db import SCHEMA_DDL, client, MODEL, execute_query, validate_sql

# Importujesz swoje rozwiązania z CP1 i CP2 — nie kopiujesz kodu!
from cp1 import EXECUTE_SQL_TOOL
from cp2 import ReportRow, RentalReport


# ════════════════════════════════════════════════════════════════════════
# Zapis raportu do markdown (gotowe — nie zmieniaj)
# ════════════════════════════════════════════════════════════════════════


def save_report(report, path: str) -> None:
    """Zapisuje RentalReport do pliku markdown."""
    os.makedirs(os.path.dirname(path), exist_ok=True)

    lines = [
        f"# {report.title}",
        "",
        f"**{report.main_value}**",
        "",
    ]

    if report.rows:
        lines.append("| Nazwa | Wartość | Szczegóły |")
        lines.append("|-------|---------|-----------|")
        for row in report.rows:
            lines.append(f"| {row.label} | {row.value} | {row.detail} |")
        lines.append("")

    lines.append(report.summary)
    lines.append("")
    lines.append("```sql")
    lines.append(report.sql_used)
    lines.append("```")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# ════════════════════════════════════════════════════════════════════════
# TWOJE ZADANIE
#
# Napisz funkcję pipeline(question: str) -> dict, która:
#
# 1. Faza FC (Function Calling):
#    - Wysyła pytanie do modelu z EXECUTE_SQL_TOOL (zaimportowane z cp1)
#    - System prompt powinien zawierać SCHEMA_DDL
#    - Obsługuje tool loop: while message.tool_calls — wykonujesz SQL,
#      zwracasz wynik, model może wywołać narzędzie ponownie
#    - Zapamiętuje ostatni sql_used i raw_data (wynik execute_query)
#
# 2. Faza SO (Structured Output):
#    - Wysyła pytanie + surowe dane do modelu z response_format=RentalReport
#    - RentalReport jest zaimportowany z cp2
#
# 3. Zwraca:
#    {"text_answer": str, "report": RentalReport}
#
# Podpowiedzi:
# - Faza FC to ten sam pattern co good_ask() z CP1, ale zamiast zwracać
#   tekst — zbierasz sql_used i raw_data
# - Faza SO to ten sam pattern co good_report() z CP2
# - validate_sql i execute_query są zaimportowane z lib/db
# ════════════════════════════════════════════════════════════════════════


# TODO: Napisz pipeline(question: str) -> dict
# def pipeline(question: str) -> dict:
#     ...


# ════════════════════════════════════════════════════════════════════════
# Uruchamianie
# ════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    questions = [
        "Ile samochodów jest dostępnych w Płocku?",
        "Kto wypożyczył najwięcej samochodów?",
        "Jaka jest średnia stawka dzienna w każdej kategorii?",
    ]

    for i, q in enumerate(questions, 1):
        print(f"\nQ: {q}")
        result = pipeline(q)

        print(f"  Tekst: {result['text_answer']}")
        r = result["report"]
        print(f"  Raport: {r.title} | {r.main_value}")
        for row in r.rows:
            print(f"    {row.label}: {row.value} ({row.detail})")

        path = f"raporty/raport_{i}.md"
        save_report(r, path)
        print(f"  Zapisano: {path}")
