"""
CP1: Function Calling
=====================

Ten plik ma DWIE sekcje:

  1. MINI PRZYKŁAD — najprostsze Function Calling (narzędzie bez parametrów).
  2. TWOJE ZADANIE — odkomentuj execute_sql z parametrem sql_query.

Uruchom: python cp1good.py
"""

import json
import sqlite3

from lib.common import MODELS, SCHEMA_DDL
from lib.db import DB_PATH, client, execute_query, validate_sql


# ════════════════════════════════════════════════════════════════════════
# SEKCJA 1: MINI PRZYKŁAD — Function Calling
#
# Najprostsze możliwe narzędzie: zero parametrów, jeden wynik.
# Przeczytaj kod, uruchom, zrozum jak działa.
# ════════════════════════════════════════════════════════════════════════


def get_car_count() -> str:
    """Zwraca liczbę wszystkich samochodów w bazie."""
    conn = sqlite3.connect(DB_PATH)
    count = conn.execute("SELECT COUNT(*) FROM Samochody").fetchone()[0]
    conn.close()
    return str(count)


GET_CAR_COUNT_TOOL = {
    "type": "function",
    "function": {
        "name": "get_car_count",
        "description": "Zwraca liczbę wszystkich samochodów w bazie wypożyczalni",
        "parameters": {"type": "object", "properties": {}},
    },
}


def mini_example(question: str) -> str:
    """MINI PRZYKŁAD: Function Calling z prostym narzędziem."""
    messages = [
        {
            "role": "system",
            "content": "Jesteś asystentem wypożyczalni samochodów. Odpowiadaj po polsku.",
        },
        {"role": "user", "content": question},
    ]

    response = client.chat.completions.create(
        model=MODELS.gpt_4o_mini,
        messages=messages,
        tools=[GET_CAR_COUNT_TOOL],
    )
    message = response.choices[0].message

    # Czy model chce wywołać narzędzie?
    if message.tool_calls:
        tool_call = message.tool_calls[0]
        print(f"  Model wywołał: {tool_call.function.name}")

        # Wykonujemy narzędzie
        result = get_car_count()
        print(f"  Wynik narzędzia: {result}")

        # Zwracamy wynik modelowi
        messages.append(message)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result,
        })

        # Model formułuje odpowiedź
        response = client.chat.completions.create(
            model=MODELS.gpt_4o_mini,
            messages=messages,
        )
        return response.choices[0].message.content

    return message.content


# ════════════════════════════════════════════════════════════════════════
# SEKCJA 2: TWOJE ZADANIE
#
# Odkomentuj oznaczone bloki i uruchom. Wzoruj się na mini_example().
# ════════════════════════════════════════════════════════════════════════


EXECUTE_SQL_TOOL = {
    "type": "function",
    "function": {
        "name": "execute_sql",
        "description": "Wykonuje zapytanie SELECT na bazie wypożyczalni samochodów",
        "parameters": {
            "type": "object",
            "properties": {
                # ── ODKOMENTUJ PONIŻEJ ──
                # "sql_query": {
                #     "type": "string",
                #     "description": "Zapytanie SQL SELECT do wykonania na bazie",
                # }
                # ── KONIEC ──
            },
            "required": ["sql_query"],
        },
    },
}


def ask(question: str) -> str:
    total_tokens = 0  # sumujemy prompt_tokens ze wszystkich wywołań API
    messages = [
        {
            "role": "system",
            "content": f"""Jesteś asystentem wypożyczalni samochodów. Odpowiadaj po polsku.
Schemat bazy danych:

{SCHEMA_DDL}""",
        },
        {"role": "user", "content": question},
    ]

    response = client.chat.completions.create(
        model=MODELS.gpt_4o_mini,
        messages=messages,
        tools=[EXECUTE_SQL_TOOL],
    )
    total_tokens += response.usage.prompt_tokens
    message = response.choices[0].message

    # pętla while, bo model może wywołać narzędzie kilka razy zanim odpowie
    while message.tool_calls:
        tool_call = message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)
        sql = args["sql_query"]
        result = ""
        # ── ODKOMENTUJ PONIŻEJ ──
        # if validate_sql(sql):
        #     result = json.dumps(execute_query(sql), ensure_ascii=False)
        # else:
        #     result = json.dumps({"error": "Niedozwolone zapytanie"})
        # ── KONIEC ──

        messages.append(message)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result,
        })

        response = client.chat.completions.create(
            model=MODELS.gpt_4o_mini,
            messages=messages,
        )
        total_tokens += response.usage.prompt_tokens
        message = response.choices[0].message

    print(f">>> Tokeny w prompcie (suma): {total_tokens}")
    return message.content


# ════════════════════════════════════════════════════════════════════════
# Uruchamianie
# ════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("SEKCJA 1: MINI PRZYKŁAD — Function Calling")
    print("=" * 60)
    print(f"\nQ: Ile samochodów macie w ofercie?")
    print(f"A: {mini_example('Ile samochodów macie w ofercie?')}")

    # ── ODKOMENTUJ PONIŻEJ (po odkomentowaniu bloków wyżej) ──
    # print("\n" + "=" * 60)
    # print("SEKCJA 2: TWOJE ROZWIĄZANIE")
    # print("=" * 60)
    # questions = [
    #     "Ile samochodów jest dostępnych w Płocku?",
    #     "Który klient wypożyczył najwięcej samochodów?",
    #     "Jaka jest średnia stawka dzienna w kategorii SUV?",
    #     "Porównaj liczbę dostępnych aut w Płocku i Warszawie",
    # ]
    # for q in questions:
    #     print(f"\nQ: {q}")
    #     print(f"A: {ask(q)}")

# ════════════════════════════════════════════════════════════════════════
# BONUS
# ════════════════════════════════════════════════════════════════════════
#
# 1. Zadaj pytanie wymagające dwóch zapytań SQL — obserwuj w logach
#    wielokrotne wywołania narzędzia.
#
# 2. Dodaj nowe narzędzie (np. get_branch_info zwracające info o oddziale)
#    — wzoruj się na GET_CAR_COUNT_TOOL.
