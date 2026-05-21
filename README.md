# dev_horizon labs: Text-to-SQL

Warsztat hands-on — zbuduj asystenta, który odpowiada na pytania po polsku, odpytując bazę wypożyczalni samochodów.

## Jak zacząć

Środowisko jest gotowe — Python, baza danych i klucz API są skonfigurowane.

Zacznij od terminala:

```bash
python cp1bad.py
```

## Checkpointy

Każdy plik to jeden checkpoint. Pracujesz w nim — czytasz kod, odkomentowujesz, uruchamiasz.

### CP1: Function Calling (`cp1.py`)

Model odpytuje bazę danych narzędziem zamiast zgadywać z danych w prompcie.

1. **Antywzorzec** — uruchom `python cp1bad.py`. Wszystkie dane lecą do promptu.
2. **Przeczytaj** — `cp1.py` sekcja 1 to mini przykład Function Calling (narzędzie bez parametrów).
3. **Odkomentuj** — sekcja 2 w `cp1.py`: odkomentuj oznaczone bloki i uruchom.
4. **Bonus** — sekcja BONUS na końcu pliku: eksperymenty dla chętnych.

### CP2: Structured Output (`cp2.py`)

Model zwraca ustrukturyzowany raport (Pydantic) zamiast tekstu do parsowania.

1. **Antywzorce** — uruchom `python cp2bad1.py` i `python cp2bad2.py` kilka razy. Czy `json.loads()` zawsze działa?
2. **Przeczytaj** — `cp2.py` sekcja 1 to mini przykład Structured Output (model z jednym polem `title`).
3. **Odkomentuj** — sekcja 2 w `cp2.py`: odkomentuj modele Pydantic i funkcję `full_report()`.
4. **Bonus** — sekcja BONUS na końcu pliku: eksperymenty dla chętnych.

### CP3: Pipeline (`cp3.py`)

Łączysz CP1 i CP2 w pipeline — model odpytuje bazę, formatuje raport, zapisuje do pliku markdown.

1. **Sprawdź importy** — `cp3.py` importuje rozwiązania z CP1 i CP2 (muszą być odkomentowane!).
2. **Odkomentuj `pipeline()`** — odkomentuj funkcję i blok `__main__`.
3. **Uruchom** — pipeline przetworzy 3 pytania i zapisze raporty do katalogu `raporty/`.
4. **Bonus** — sekcja BONUS na końcu pliku: eksperymenty dla chętnych.

## Struktura repo

```
├── cp1bad.py           ← Antywzorzec CP1: prompt stuffing
├── cp1.py              ← Checkpoint 1: Function Calling
├── cp2bad1.py          ← Antywzorzec CP2: luźna instrukcja JSON
├── cp2bad2.py          ← Antywzorzec CP2: sprzeczne instrukcje
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
- Ważniejsze jest zrozumienie niż ukończenie
