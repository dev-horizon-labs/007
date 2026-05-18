"""
dev_horizon labs — UI
Uruchamia się automatycznie w Codespaces (port 7860).
"""

import importlib
import traceback

import gradio as gr


def check_progress():
    """Sprawdza które checkpointy są zaimplementowane."""
    checks = [
        ("cp1", "good_ask", "CP1: Function Calling"),
        ("cp2", "good_report", "CP2: Structured Output"),
        ("cp3", "pipeline", "CP3: Pipeline"),
    ]
    results = {}
    for module_name, func_name, label in checks:
        try:
            mod = importlib.import_module(module_name)
            importlib.reload(mod)
            results[label] = hasattr(mod, func_name) and callable(getattr(mod, func_name))
        except Exception:
            results[label] = False

    done = sum(1 for v in results.values() if v)
    parts = [("✅" if ok else "⬜") + " " + label for label, ok in results.items()]
    return f"**Progres: {done}/3** — " + " · ".join(parts)


def _reload(module_name):
    mod = importlib.import_module(module_name)
    importlib.reload(mod)
    return mod


# ── CP1 handlers ──

def cp1_bad(question):
    try:
        mod = _reload("cp1")
        return mod.bad_ask(question), check_progress()
    except Exception as e:
        return f"**Błąd:** {e}", check_progress()


def cp1_good(question):
    try:
        mod = _reload("cp1")
        fn = getattr(mod, "good_ask", None)
        if fn is None:
            return "⏳ Zaimplementuj `good_ask()` w **cp1.py** (sekcja 3)", check_progress()
        return fn(question), check_progress()
    except Exception as e:
        return f"**Błąd:** {e}\n```\n{traceback.format_exc()}\n```", check_progress()


# ── CP2 handlers ──

def cp2_bad():
    try:
        mod = _reload("cp2")
        report = mod.bad_report(mod.TEST_QUESTION, mod.TEST_DATA)
        lines = [f"**{report['title']}**", f"*{report['main_value']}*", ""]
        for row in report.get("rows", []):
            lines.append(f"- **{row['label']}**: {row['value']} ({row.get('detail', '')})")
        lines.append(f"\n_{report.get('summary', '')}_")
        return "\n".join(lines), check_progress()
    except Exception as e:
        return f"**Błąd:** {e}\n\nTo jest antywzorzec — `json.loads()` nie zawsze działa!", check_progress()


def cp2_good():
    try:
        mod = _reload("cp2")
        fn = getattr(mod, "good_report", None)
        if fn is None:
            return "⏳ Zaimplementuj `good_report()` w **cp2.py** (sekcja 3)", check_progress()
        report = fn(mod.TEST_QUESTION, mod.TEST_DATA, mod.TEST_SQL)
        lines = [f"## {report.title}", f"### {report.main_value}", ""]
        lines.append("| Nazwa | Wartość | Szczegóły |")
        lines.append("|-------|---------|-----------|")
        for row in report.rows:
            lines.append(f"| {row.label} | {row.value} | {row.detail} |")
        lines.append(f"\n{report.summary}")
        lines.append(f"\n```sql\n{report.sql_used}\n```")
        return "\n".join(lines), check_progress()
    except Exception as e:
        return f"**Błąd:** {e}\n```\n{traceback.format_exc()}\n```", check_progress()


# ── CP3 handlers ──

def cp3_run(question):
    empty = ("", "", [], "", "")
    try:
        mod = _reload("cp3")
        fn = getattr(mod, "pipeline", None)
        if fn is None:
            return ("⏳ Zaimplementuj `pipeline()` w **cp3.py** (krok 4)", *empty[1:], check_progress())
        result = fn(question)
        text = result["text_answer"]
        report = result["report"]
        header = f"## {report.title}\n### {report.main_value}"
        table = [[r.label, r.value, r.detail] for r in report.rows]
        return text, header, table, report.summary, report.sql_used, check_progress()
    except Exception as e:
        return (f"**Błąd:** {e}\n```\n{traceback.format_exc()}\n```", *empty[1:], check_progress())


# ── UI ──

with gr.Blocks(title="dev_horizon labs", theme=gr.themes.Soft()) as app:
    gr.Markdown("# dev_horizon labs — Text-to-SQL")
    gr.Markdown("Wyniki z checkpointów. Edytuj `cp1.py` / `cp2.py` / `cp3.py`, zapisz, kliknij przycisk.")

    progress = gr.Markdown(check_progress())
    refresh_btn = gr.Button("Sprawdź progres", size="sm", variant="secondary")
    refresh_btn.click(fn=check_progress, outputs=progress)

    with gr.Tab("CP1: Function Calling"):
        gr.Markdown("Model odpytuje bazę SQL zamiast zgadywać z danych w prompcie.")
        q1 = gr.Textbox(label="Pytanie", value="Ile samochodów jest dostępnych w Płocku?")
        with gr.Row():
            btn1_bad = gr.Button("Antywzorzec (prompt stuffing)", variant="secondary")
            btn1_good = gr.Button("Twoje rozwiązanie (FC)", variant="primary")
        out1 = gr.Markdown(label="Odpowiedź")
        btn1_bad.click(fn=cp1_bad, inputs=q1, outputs=[out1, progress])
        btn1_good.click(fn=cp1_good, inputs=q1, outputs=[out1, progress])

    with gr.Tab("CP2: Structured Output"):
        gr.Markdown("Model zwraca ustrukturyzowany raport zamiast tekstu do parsowania.")
        gr.Markdown("*Dane testowe — nie musisz wpisywać pytania.*")
        with gr.Row():
            btn2_bad = gr.Button("Antywzorzec (json.loads)", variant="secondary")
            btn2_good = gr.Button("Twoje rozwiązanie (SO)", variant="primary")
        out2 = gr.Markdown(label="Raport")
        btn2_bad.click(fn=cp2_bad, outputs=[out2, progress])
        btn2_good.click(fn=cp2_good, outputs=[out2, progress])

    with gr.Tab("CP3: Pipeline"):
        gr.Markdown("FC + SO = pełny pipeline. Model odpytuje bazę i formatuje raport.")
        q3 = gr.Textbox(label="Pytanie", value="Ile samochodów jest dostępnych w Płocku?")
        btn3 = gr.Button("Pipeline (FC + SO)", variant="primary")

        with gr.Row():
            with gr.Column():
                gr.Markdown("#### Odpowiedź tekstowa")
                out3_text = gr.Markdown()
            with gr.Column():
                gr.Markdown("#### Raport")
                out3_header = gr.Markdown()
                out3_table = gr.Dataframe(
                    headers=["", "Wartość", "Szczegóły"], interactive=False
                )
                out3_summary = gr.Markdown()
                out3_sql = gr.Code(language="sql", label="SQL")

        btn3.click(
            fn=cp3_run,
            inputs=q3,
            outputs=[out3_text, out3_header, out3_table, out3_summary, out3_sql, progress],
        )

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)
