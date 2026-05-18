"""
CP3: Pipeline + Gradio UI
=========================

Łączysz Function Calling (CP1) ze Structured Output (CP2).
Model odpytuje bazę → formatuje wynik w raport → Gradio wyświetla.

Uruchom: python cp3.py
Gradio: python cp3.py --ui

Ten plik NIE ma antywzorca — to zadanie integracyjne.
"""

import json

from pydantic import BaseModel, Field

from lib.db import SCHEMA_DDL, client, MODEL, execute_query, validate_sql


# ════════════════════════════════════════════════════════════════════════
# KROK 1: Skopiuj swoje rozwiązania z CP1 i CP2
#
# Z CP1 potrzebujesz:
# - EXECUTE_SQL_TOOL (definicja narzędzia)
# - Logikę tool loop (model wywołuje narzędzie → wykonujesz → zwracasz wynik)
#
# Z CP2 potrzebujesz:
# - ReportRow i RentalReport (modele Pydantic)
# - Logikę Structured Output (client.beta.chat.completions.parse)
# ════════════════════════════════════════════════════════════════════════


# TODO: Wklej EXECUTE_SQL_TOOL z CP1
# EXECUTE_SQL_TOOL = ...


# TODO: Wklej ReportRow i RentalReport z CP2
# class ReportRow(BaseModel):
#     ...
# class RentalReport(BaseModel):
#     ...


# ════════════════════════════════════════════════════════════════════════
# KROK 2: Function Calling — pobierz dane z bazy
#
# Napisz funkcję, która:
# - Wysyła pytanie do modelu z narzędziem execute_sql
# - Obsługuje tool loop (while message.tool_calls)
# - Zwraca: (odpowiedź tekstową, ostatni SQL, surowe dane z bazy)
# ════════════════════════════════════════════════════════════════════════


# TODO: Napisz fc_query(question: str) -> tuple[str, str, list[dict]]
# def fc_query(question: str) -> tuple[str, str, list[dict]]:
#     ...


# ════════════════════════════════════════════════════════════════════════
# KROK 3: Structured Output — ustrukturyzuj wynik
#
# Napisz funkcję, która:
# - Dostaje pytanie, surowe dane z bazy i SQL
# - Używa response_format=RentalReport
# - Zwraca obiekt RentalReport
# ════════════════════════════════════════════════════════════════════════


# TODO: Napisz so_format(question, raw_data, sql_used) -> RentalReport
# def so_format(question: str, raw_data: list[dict], sql_used: str) -> RentalReport:
#     ...


# ════════════════════════════════════════════════════════════════════════
# KROK 4: Pipeline — połącz FC + SO
# ════════════════════════════════════════════════════════════════════════


# TODO: Napisz pipeline(question: str) -> dict
# def pipeline(question: str) -> dict:
#     # 1. FC — pobierz dane
#     text_answer, sql_used, raw_data = fc_query(question)
#
#     # 2. SO — ustrukturyzuj
#     report = so_format(question, raw_data, sql_used)
#
#     return {
#         "text_answer": text_answer,
#         "report": report,
#     }


# ════════════════════════════════════════════════════════════════════════
# Gradio UI — gotowe, nie trzeba zmieniać
#
# Wyświetla side-by-side: tekst (FC only) vs raport (FC + SO)
# Uruchom: python cp3.py --ui
# ════════════════════════════════════════════════════════════════════════


def build_gradio_app():
    import gradio as gr

    def on_text(question):
        text, _, _ = fc_query(question)
        return text

    def on_report(question):
        result = pipeline(question)
        text = result["text_answer"]
        report = result["report"]
        header = f"## {report.title}\n### {report.main_value}"
        table = [[r.label, r.value, r.detail] for r in report.rows]
        return text, header, table, report.summary, report.sql_used

    with gr.Blocks(title="dev_horizon labs — Text-to-SQL") as app:
        gr.Markdown("# Asystent wypożyczalni samochodów")
        question = gr.Textbox(
            label="Twoje pytanie",
            placeholder="Ile samochodów jest dostępnych w Płocku?",
        )

        with gr.Row():
            btn_text = gr.Button("Tekst (FC only)", variant="secondary")
            btn_report = gr.Button("Raport (FC + SO)", variant="primary")

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Odpowiedź tekstowa")
                text_output = gr.Markdown()

            with gr.Column():
                gr.Markdown("### Raport strukturalny")
                report_header = gr.Markdown()
                report_table = gr.Dataframe(
                    headers=["", "Wartość", "Szczegóły"],
                    interactive=False,
                )
                report_summary = gr.Markdown()
                report_sql = gr.Code(language="sql", label="SQL")

        btn_text.click(fn=on_text, inputs=question, outputs=text_output)
        btn_report.click(
            fn=on_report,
            inputs=question,
            outputs=[text_output, report_header, report_table, report_summary, report_sql],
        )

    return app


# ════════════════════════════════════════════════════════════════════════
# Uruchamianie
# ════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    if "--ui" in sys.argv:
        app = build_gradio_app()
        app.launch(server_name="0.0.0.0", server_port=7860)
    else:
        questions = [
            "Ile samochodów jest dostępnych w Płocku?",
            "Kto wypożyczył najwięcej samochodów?",
            "Jaka jest średnia stawka dzienna w każdej kategorii?",
        ]

        for q in questions:
            print(f"\nQ: {q}")
            result = pipeline(q)
            print(f"  Tekst: {result['text_answer']}")
            r = result["report"]
            print(f"  Raport: {r.title} | {r.main_value}")
            for row in r.rows:
                print(f"    {row.label}: {row.value} ({row.detail})")
