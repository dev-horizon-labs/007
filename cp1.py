"""
CP1: Function Calling
=====================

Ten plik ma DWIE sekcje:

  1. MINI PRZYKŁAD — najprostsze Function Calling (narzędzie bez parametrów).
  2. TWOJE ZADANIE — zbuduj execute_sql z parametrem sql_query.

Uruchom: python cp1.py
"""

import json
import sqlite3

from lib.db import DB_PATH, SCHEMA_DDL, client, MODEL, execute_query, validate_sql


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
        model=MODEL,
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
            model=MODEL,
            messages=messages,
        )
        return response.choices[0].message.content

    return message.content


# ════════════════════════════════════════════════════════════════════════
# SEKCJA 2: TWOJE ZADANIE
#
# Uzupełnij dwa TODO poniżej. Reszta kodu jest gotowa.
# Wzoruj się na mini_example() wyżej.
# ════════════════════════════════════════════════════════════════════════


EXECUTE_SQL_TOOL = {
    "type": "function",
    "function": {
        "name": "execute_sql",
        "description": "Wykonuje zapytanie SELECT na bazie wypożyczalni samochodów",
        "parameters": {
            "type": "object",
            "properties": {
                # TODO 1: dodaj parametr "sql_query"
                # Wzór: "sql_query": {"type": "string", "description": "..."}
            },
            "required": ["sql_query"],
        },
    },
}


def good_ask(question: str) -> str:
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
        model=MODEL,
        messages=messages,
        tools=[EXECUTE_SQL_TOOL],
    )
    message = response.choices[0].message

    while message.tool_calls:
        tool_call = message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)
        sql = args["sql_query"]

        # TODO 2: wykonaj zapytanie i zapisz wynik jako string w 'result'
        # Użyj: validate_sql(sql), execute_query(sql), json.dumps(...)
        result = ...

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

    # print("\n" + "=" * 60)
    # print("SEKCJA 2: TWOJE ROZWIĄZANIE")
    # print("=" * 60)
    # questions = [
    #     "Ile samochodów jest dostępnych w Płocku?",
    #     "Który klient wypożyczył najwięcej samochodów?",
    #     "Jaka jest średnia stawka dzienna w kategorii SUV?",
    # ]
    # for q in questions:
    #     print(f"\nQ: {q}")
    #     print(f"A: {good_ask(q)}")
