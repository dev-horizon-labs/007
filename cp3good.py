"""
CP3: Pipeline
=============

Łączysz Function Calling (CP1) ze Structured Output (CP2).
Model odpytuje bazę → formatuje wynik → zapisuje raport do pliku markdown.

Uruchom: python cp3good.py
"""

import json
import os

from lib.common import MODEL, SCHEMA_DDL
from lib.db import client, execute_query, validate_sql

# Importy z CP1 i CP2 — działają po odkomentowaniu rozwiązań w tamtych plikach
from cp1good import EXECUTE_SQL_TOOL
from cp2good import ReportRow, RentalReport, full_report


# ════════════════════════════════════════════════════════════════════════
# Zapis raportu do markdown
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
# Pipeline łączy FC (cp1) i SO (cp2):
#   Faza 1: pytanie → model wywołuje SQL → surowe dane
#   Faza 2: surowe dane → full_report() → RentalReport
# ════════════════════════════════════════════════════════════════════════


def pipeline(question: str) -> dict:
    # Faza 1: Function Calling — model odpytuje bazę
    messages = [
        {
            "role": "system",
            "content": f"Jesteś asystentem wypożyczalni samochodów. Odpowiadaj po polsku.\nSchemat bazy danych:\n\n{SCHEMA_DDL}",
        },
        {"role": "user", "content": question},
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=[EXECUTE_SQL_TOOL],
    )
    message = response.choices[0].message

    sql_used = ""
    raw_data = []

    while message.tool_calls:
        tool_call = message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)
        sql = args["sql_query"]

        if validate_sql(sql):
            sql_used = sql
            raw_data = execute_query(sql)
            result = json.dumps(raw_data, ensure_ascii=False)
        else:
            result = json.dumps({"error": "Niedozwolone zapytanie"})

        messages.append(message)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result,
        })

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
        )
        message = response.choices[0].message

    text_answer = message.content

    # Faza 2: Structured Output — formatowanie raportu
    report = full_report(question, raw_data, sql_used)

    return {"text_answer": text_answer, "report": report}


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


# ════════════════════════════════════════════════════════════════════════
# BONUS
# ════════════════════════════════════════════════════════════════════════
#
# 1. Dodaj własne pytanie do listy — np. 'Który oddział ma najwyższe
#    przychody?'
#
# 2. Zmodyfikuj save_report żeby dodawał datę generowania do nagłówka.
