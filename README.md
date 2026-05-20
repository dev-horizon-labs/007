# dev_horizon labs: Text-to-SQL

Warsztat hands-on — zbuduj asystenta, który odpowiada na pytania po polsku, odpytując bazę wypożyczalni samochodów.

## Jak zacząć

Środowisko jest gotowe — Python, baza danych i klucz API są skonfigurowane.

Zacznij od terminala:

```bash
python cp1.py
```

## Checkpointy

Każdy plik to jeden checkpoint. Pracujesz w nim — czytasz kod, uruchamiasz, implementujesz.

### CP1: Function Calling (`cp1.py`)

Model odpytuje bazę danych narzędziem zamiast zgadywać z danych w prompcie.

1. **Uruchom** — sekcja 1 wrzuca wszystkie dane do promptu. Sprawdź odpowiedzi.
2. **Przeczytaj** — sekcja 2 to mini przykład Function Calling (narzędzie bez parametrów).
3. **Napisz** — sekcja 3: zbuduj narzędzie `execute_sql(sql_query)` używając tego samego patternu.

### CP2: Structured Output (`cp2.py`)

Model zwraca ustrukturyzowany raport (Pydantic) zamiast tekstu do parsowania.

1. **Uruchom kilka razy** — sekcja 1 parsuje tekst modelu przez `json.loads()`. Czy zawsze działa?
2. **Przeczytaj** — sekcja 2 to mini przykład Structured Output (model z jednym polem `title`).
3. **Napisz** — sekcja 3: rozbuduj do pełnego `RentalReport` z tabelą danych.

### CP3: Pipeline (`cp3.py`)

Łączysz CP1 i CP2 w pipeline — model odpytuje bazę, formatuje raport, zapisuje do pliku markdown.

1. **Sprawdź importy** — `cp3.py` importuje Twoje rozwiązania z CP1 i CP2 (nie kopiujesz kodu!).
2. **Napisz `pipeline()`** — połącz Function Calling z Structured Output.
3. **Uruchom** — pipeline przetworzy 3 pytania i zapisze raporty do katalogu `raporty/`.

## Struktura repo

```
├── cp1.py              ← Checkpoint 1: Function Calling
├── cp2.py              ← Checkpoint 2: Structured Output
├── cp3.py              ← Checkpoint 3: Pipeline (FC + SO → raport .md)
├── lib/
│   └── db.py           ← Połączenie z bazą, walidacja SQL, schema (nie zmieniaj)
├── data/
│   ├── wypozyczalnia.db ← Baza SQLite (80 samochodów, 120 klientów, 300 wypożyczeń)
│   └── create_db.py    ← Skrypt seedujący bazę (nie musisz uruchamiać)
├── raporty/            ← Tu trafiają wygenerowane raporty (po uruchomieniu CP3)
├── .env                ← URL proxy API (nie zmieniaj)
└── requirements.txt
```

## Przydatne pytania do testowania

- "Ile samochodów jest dostępnych w Płocku?"
- "Który klient wypożyczył najwięcej samochodów?"
- "Jaka jest średnia stawka dzienna w kategorii SUV?"
- "Pokaż aktywne wypożyczenia z opóźnionym zwrotem"
- "Ile zarobiła wypożyczalnia w 2025 roku?"
- "Który oddział ma najwięcej samochodów w serwisie?"

## Potrzebujesz pomocy?

- Podnieś rękę — prowadzący chętnie pomoże
- Rozwiązania dostaniesz po warsztacie
- Ważniejsze jest zrozumienie niż ukończenie
