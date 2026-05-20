import os
import sys
import sqlite3
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "wypozyczalnia.db")

_raw_client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY", "not-needed"),
    base_url=os.environ["OPENAI_BASE_URL"],
)
MODEL = "gpt-4o-mini"

SCHEMA_DDL = """
Oddzialy(id, nazwa, miasto, adres, telefon, aktywny)
KategorieSamochodow(id, nazwa, opis, stawka_dzienna)
Pracownicy(id, imie, nazwisko, email, stanowisko, id_oddzialu, data_zatrudnienia, id_przelozonego, aktywny)
Klienci(id, imie, nazwisko, email, telefon, data_urodzenia, nr_prawa_jazdy, data_rejestracji, usuniety_at)
Samochody(id, marka, model, rok_produkcji, nr_rejestracyjny, kolor, id_kategorii, id_oddzialu, status, przebieg)
  status IN ('dostepny', 'wypozyczony', 'serwis')
  FK: id_kategorii -> KategorieSamochodow, id_oddzialu -> Oddzialy
Wypozyczenia(id, id_klienta, id_samochodu, id_pracownika, data_wypozyczenia, data_planowanego_zwrotu, data_faktycznego_zwrotu, km_wypozyczenie, km_zwrot, status, kwota_calkowita)
  status IN ('aktywne', 'zakonczone', 'anulowane')
  FK: id_klienta -> Klienci, id_samochodu -> Samochody, id_pracownika -> Pracownicy
Platnosci(id, id_wypozyczenia, kwota, data_platnosci, metoda, status)
  metoda IN ('karta', 'gotowka', 'przelew')
  status IN ('oczekujaca', 'zrealizowana', 'anulowana')
"""


# ── Logging ────────────────────────────────────────────────────────────

_LOG_DIR = os.path.join(os.path.dirname(__file__), "..")


def _get_log_path():
    name = os.path.basename(sys.argv[0]).removesuffix(".py")
    return os.path.join(_LOG_DIR, f"{name}.logs.txt")


def _fmt_message(msg):
    if isinstance(msg, dict):
        role = msg.get("role", "?")
        content = msg.get("content", "")
        if role == "tool":
            return f"[tool call_id={msg.get('tool_call_id', '?')}]\n{content}"
        return f"[{role}]\n{content}"
    role = getattr(msg, "role", "?")
    parts = [f"[{role}]"]
    if msg.content:
        parts.append(msg.content)
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        for tc in msg.tool_calls:
            parts.append(f"  -> {tc.function.name}({tc.function.arguments})")
    return "\n".join(parts)


def _log_api_call(messages, response):
    try:
        msg = response.choices[0].message
        with open(_get_log_path(), "a", encoding="utf-8") as f:
            f.write(f"{'=' * 60}\n")
            f.write(f"{datetime.now().isoformat()}\n\n")
            f.write("--- PROMPT ---\n")
            for m in messages:
                f.write(_fmt_message(m) + "\n\n")
            f.write("--- OUTPUT ---\n")
            if msg.content:
                f.write(msg.content + "\n")
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    f.write(f"tool_call: {tc.function.name}({tc.function.arguments})\n")
            if hasattr(msg, "parsed") and msg.parsed:
                f.write(msg.parsed.model_dump_json(indent=2, ensure_ascii=False) + "\n")
            f.write("\n")
    except Exception:
        pass


# ── Logging client wrapper ─────────────────────────────────────────────

class _Completions:
    def __init__(self, real):
        self._real = real

    def create(self, **kwargs):
        resp = self._real.chat.completions.create(**kwargs)
        _log_api_call(kwargs.get("messages", []), resp)
        return resp


class _BetaCompletions:
    def __init__(self, real):
        self._real = real

    def parse(self, **kwargs):
        resp = self._real.beta.chat.completions.parse(**kwargs)
        _log_api_call(kwargs.get("messages", []), resp)
        return resp


class _Chat:
    def __init__(self, real):
        self.completions = _Completions(real)


class _BetaChat:
    def __init__(self, real):
        self.completions = _BetaCompletions(real)


class _Beta:
    def __init__(self, real):
        self.chat = _BetaChat(real)


class _LoggingClient:
    def __init__(self, real):
        self._real = real
        self.chat = _Chat(real)
        self.beta = _Beta(real)

    def __getattr__(self, name):
        return getattr(self._real, name)


client = _LoggingClient(_raw_client)


# ── SQL helpers ────────────────────────────────────────────────────────

def validate_sql(sql: str) -> bool:
    normalized = sql.strip().upper()
    if not normalized.startswith("SELECT"):
        return False
    forbidden = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE"]
    return not any(kw in normalized for kw in forbidden)


def execute_query(sql: str) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(sql).fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        return [{"error": str(e)}]
    finally:
        conn.close()
