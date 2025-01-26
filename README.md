# Anonymizacja Danych

>[!NOTE]
>Wersja Pythona zalecana do uruchomienia skryptów powinna wynosić 3.11 lub wyższa.

## Konfiguracja środowiska

W celu uruchomienia skryptów należy zainstalować wymagane biblioteki. W tym celu należy wykonać poniższe polecenie:

```bash
pip install -r requirements.txt
```

lub w przypadku korzystania z `uv`:

```bash
uv sync
```

## Uruchomienie skryptu wydajnościowego

W celu uruchomienia skryptu wydajnościowego należy wykonać poniższe polecenie:

```bash
python prfrmnce.py
```

## Dostępne flagi dla skryptu wydajnościowego
```bash
usage: prfrmnce.py [-h] [--method {deterministic,shuffle,bitwise}] [--sizes SIZES [SIZES ...]]

Test anonymization performance

options:
  -h, --help            show this help message and exit
  --method {deterministic,shuffle,bitwise}, -m {deterministic,shuffle,bitwise}
                        Anonymization method to test
  --sizes SIZES [SIZES ...], -s SIZES [SIZES ...]
                        Dataset sizes to test
```
