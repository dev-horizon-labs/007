# dev_horizon labs: Text-to-SQL

Warsztat hands-on — zbuduj asystenta, który odpowiada na pytania po polsku, odpytując bazę wypożyczalni samochodów.

## Jak zacząć

Środowisko jest gotowe — Python, baza danych i klucz API są skonfigurowane.

Sprawdź połączenie z modelem:

```bash
python cp0.py
```

Jeśli działa — przejdź do CP1.

## Checkpointy

Każdy plik to jeden checkpoint. Pracujesz w nim — czytasz kod, odkomentowujesz, uruchamiasz.

### CP1: Function Calling (`cp1good.py`)

Model odpytuje bazę danych narzędziem zamiast zgadywać z danych w prompcie.

1. **Antywzorzec** — uruchom `python cp1bad.py`. Wszystkie dane lecą do promptu.
2. **Przeczytaj** — `cp1good.py` sekcja 1 to mini przykład Function Calling (narzędzie bez parametrów).
3. **Odkomentuj** — sekcja 2 w `cp1good.py`: odkomentuj oznaczone bloki i uruchom.
4. **Bonus** — sekcja BONUS na końcu pliku: eksperymenty dla chętnych.

### CP2: Structured Output (`cp2good.py`)

Model zwraca ustrukturyzowany raport (Pydantic) zamiast tekstu do parsowania.

1. **Antywzorce** — uruchom `python cp2bad1.py` i `python cp2bad2.py` kilka razy. Czy `json.loads()` zawsze działa?
2. **Przeczytaj** — `cp2good.py` sekcja 1 to mini przykład Structured Output (model z jednym polem `title`).
3. **Odkomentuj** — sekcja 2 w `cp2good.py`: odkomentuj modele Pydantic i funkcję `full_report()`.
4. **Bonus** — sekcja BONUS na końcu pliku: eksperymenty dla chętnych.

### CP3: Pipeline (`cp3good.py`)

Łączysz CP1 i CP2 w pipeline — model odpytuje bazę, formatuje raport, zapisuje do pliku markdown.

1. **Sprawdź importy** — `cp3good.py` importuje rozwiązania z CP1 i CP2 (muszą być odkomentowane!).
2. **Uruchom** — pipeline przetworzy 5 pytań i zapisze zbiorczy raport do `raporty/`.
3. **Bonus** — sekcja BONUS na końcu pliku: eksperymenty dla chętnych.

## Struktura repo

```
├── cp0.py              ← Ping pong — test połączenia z modelem
├── cp1bad.py           ← Antywzorzec CP1: prompt stuffing
├── cp1good.py          ← Checkpoint 1: Function Calling
├── cp2bad1.py          ← Antywzorzec CP2: luźna instrukcja JSON
├── cp2bad2.py          ← Antywzorzec CP2: sprzeczne instrukcje
├── cp2good.py          ← Checkpoint 2: Structured Output
├── cp3good.py          ← Checkpoint 3: Pipeline (FC + SO → raport .md)
├── lib/
│   ├── common.py       ← Modele (MODELS), schema DDL
│   └── db.py           ← Połączenie z bazą, walidacja SQL (nie zmieniaj)
├── data/
│   ├── wypozyczalnia.db ← Baza SQLite (80 samochodów, 120 klientów, 300 wypożyczeń)
│   └── create_db.py    ← Skrypt seedujący bazę (nie musisz uruchamiać)
├── raporty/            ← Tu trafiają wygenerowane raporty (po uruchomieniu CP3)
├── *.logs.txt          ← Logi API — po uruchomieniu cpX.py pojawi się cpX.logs.txt
└── requirements.txt    ← Zależności (openai, pydantic) — instalowane automatycznie
```

## Przydatne pytania do testowania

- "Ile samochodów jest dostępnych w Płocku?"
- "Który klient wypożyczył najwięcej samochodów?"
- "Jaka jest średnia stawka dzienna w kategorii SUV?"
- "Pokaż aktywne wypożyczenia z opóźnionym zwrotem"
- "Ile zarobiła wypożyczalnia w 2025 roku?"
- "Który oddział ma najwięcej samochodów w serwisie?"

## Debugowanie

Otwórz dowolny `cpX.py`, ustaw breakpoint (klik na marginesie) i naciśnij **F5** → "Python: File". Przejdziesz kod krok po kroku.

## Potrzebujesz pomocy?

- Podnieś rękę — prowadzący chętnie pomoże
- Ważniejsze jest zrozumienie niż ukończenie
