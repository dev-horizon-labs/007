"""
CP0: Ping Pong
==============

Sprawdzamy, czy połączenie z modelem działa.

Uruchom w terminalu komendę: 

python cp0.py

"""

from lib.common import MODELS
from lib.db import client


def ping(question: str) -> str:
    response = client.chat.completions.create(
        model=MODELS.gpt_4o_mini,
        messages=[
            {"role": "system", "content": "Odpowiadaj po polsku, krótko i na temat."},
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    print("=" * 60)
    print("CP0: Ping Pong — test połączenia z modelem")
    print("=" * 60)

    answer = ping("Powiedz 'pong' i nic więcej.")
    print(f"\nQ: Powiedz 'pong' i nic więcej.")
    print(f"A: {answer}")
