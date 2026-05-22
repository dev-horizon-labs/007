"""
CP3: Pipeline
=============

Łączysz Function Calling (CP1) ze Structured Output (CP2).
Model odpytuje bazę → formatuje wynik → zapisuje raport do pliku markdown.

Uruchom: python cp3good.py
"""

import json
import os

from lib.common import MODELS, SCHEMA_DDL
from lib.db import client, execute_query, validate_sql

# Importy z CP1 i CP2 — działają po odkomentowaniu rozwiązań w tamtych plikach
from cp1good import EXECUTE_SQL_TOOL
from cp2good import ReportRow, RentalReport, full_report


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
        model=MODELS.gpt_4o_mini,
        messages=messages,
        tools=[EXECUTE_SQL_TOOL],
    )
    message = response.choices[0].message

    sql_used = ""
    raw_data = []

    while message.tool_calls:
        messages.append(message)
        for tool_call in message.tool_calls:
            args = json.loads(tool_call.function.arguments)
            sql = args["sql_query"]

            if validate_sql(sql):
                sql_used = sql
                raw_data = execute_query(sql)
                result = json.dumps(raw_data, ensure_ascii=False)
            else:
                result = json.dumps({"error": "Niedozwolone zapytanie"})

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

        response = client.chat.completions.create(
            model=MODELS.gpt_4o_mini,
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
        "Który oddział generuje najwyższe przychody z wypożyczeń?",
        "Jakie samochody są wypożyczone najdłużej ponad planowany termin zwrotu?",
    ]

    all_sections = []
    for q in questions:
        print(f"\nQ: {q}")
        result = pipeline(q)

        print(f"  Tekst: {result['text_answer']}")
        r = result["report"]
        print(f"  Raport: {r.title} | {r.main_value}")
        for row in r.rows:
            print(f"    {row.label}: {row.value} ({row.detail})")

        all_sections.append(r)

    path = "raporty/raport.md"
    os.makedirs("raporty", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in all_sections:
            f.write(f"# {r.title}\n\n")
            f.write(f"**{r.main_value}**\n\n")
            if r.rows:
                f.write("| Nazwa | Wartość | Szczegóły |\n")
                f.write("|-------|---------|----------|\n")
                for row in r.rows:
                    f.write(f"| {row.label} | {row.value} | {row.detail} |\n")
                f.write("\n")
            f.write(f"{r.summary}\n\n")
            f.write(f"```sql\n{r.sql_used}\n```\n\n---\n\n")
    print(f"\nZapisano zbiorczy raport: {path}")


# ════════════════════════════════════════════════════════════════════════
# BONUS
# ════════════════════════════════════════════════════════════════════════
#
# 1. Dodaj własne pytanie do listy — np. 'Który oddział ma najwyższe
#    przychody?'
#
# 2. Zmodyfikuj save_report żeby dodawał datę generowania do nagłówka.
