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
# Zbuduj narzędzie execute_sql, które:
# - Przyjmuje parametr sql_query (string)
# - Wykonuje zapytanie SELECT na bazie (użyj validate_sql + execute_query z lib/db.py)
# - Zwraca wyniki jako JSON
#
# Podpowiedzi:
# - Definicja narzędzia: wzoruj się na GET_CAR_COUNT_TOOL, dodaj parametr sql_query
# - System prompt: dodaj SCHEMA_DDL żeby model wiedział jakie tabele są w bazie
# - Tool loop: model może chcieć wywołać narzędzie wielokrotnie — obsłuż to w pętli while
# ════════════════════════════════════════════════════════════════════════


# TODO: Zdefiniuj EXECUTE_SQL_TOOL (dict z opisem narzędzia)
# EXECUTE_SQL_TOOL = ...


# TODO: Napisz funkcję good_ask(question: str) -> str
# def good_ask(question: str) -> str:
#     ...


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
