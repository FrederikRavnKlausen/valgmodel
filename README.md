# Valgmodel til Live Prediktion

En valgmodel til at forudsige det endelige valgresultat baseret på delvist optalte valgsteder på valgnatten.

## Hvordan virker modellen?

Modellen bruger en swing-baseret tilgang:

1. **Aggreger optalte stemmer**: Summer alle stemmer på de valgsteder der er optalt i det nuværende valg → giver procenter **p₁, ..., pₙ** for hvert parti

2. **Aggreger samme valgsteder fra forrige valg**: Summer stemmer på de samme valgsteder fra forrige valg → giver procenter **q₁, ..., qₙ**

3. **Beregn swing**: For hvert parti beregnes swing som **sᵢ = pᵢ / qᵢ**

4. **Applicer på samlet resultat**: Tag det samlede resultat fra forrige valg **r₁, ..., rₙ** og gang med swing → **rᵢ × sᵢ**

5. **Normaliser**: Normaliser resultatet så summen bliver 100%

### Matematisk notation

Hvis vi kalder:
- **p** = procenter på optalte valgsteder (nuværende valg)
- **q** = procenter på samme valgsteder (forrige valg)
- **r** = samlet resultat (forrige valg)

Så er prediктionen:

```
Prediкtion_i = (r_i × p_i / q_i) / Σ(r_j × p_j / q_j)
```

## Installation

```bash
pip install -r requirements.txt
```

## Brug

### Grundlæggende eksempel

```python
from valgmodel import Valgmodel

# Initialiser modellen med data fra forrige valg
model = Valgmodel("Kommunalvalg_2021_København_17-11-2025 20.11.26.csv")

# På valgnatten: specificer hvilke valgsteder der er optalt
optalte_valgsteder = [
    "1. 1. Østerbro",
    "1. 2. Østerbro",
    "2. 1. Nørrebro"
]

# Prediкer baseret på live data
prediкtion = model.prediкer_fra_csv(
    "live_data.csv",  # CSV med nuværende valgdata
    optalte_valgsteder
)

# Vis resultat
model.print_resultat(prediкtion, "Prediкeret resultat")
```

### Alternativ: Brug DataFrame direkte

```python
import pandas as pd
from valgmodel import Valgmodel

model = Valgmodel("Kommunalvalg_2021_København_17-11-2025 20.11.26.csv")

# Hvis du allerede har data i en DataFrame
nuværende_data = pd.DataFrame(...)  # Dit live data

optalte_valgsteder = ["1. 1. Østerbro", "2. 1. Nørrebro"]

prediкtion = model.prediкer(nuværende_data, optalte_valgsteder)
```

## CSV Format

CSV-filen skal have følgende kolonner (semikolon-separeret):

```
Afstemningsområde;Bogstavbetegnelse;Listenavn;Navn;Stemmetal
1. 1. Østerbro;A;Socialdemokratiet;Listestemmer;447
1. 1. Østerbro;A;Socialdemokratiet;Sophie Hæstorp Andersen;317
...
```

- **Afstemningsområde**: Navn på valgstedet
- **Bogstavbetegnelse**: Partibogstav (A, B, C, osv.)
- **Listenavn**: Partinavn
- **Navn**: Enten "Listestemmer" eller kandidatnavn
- **Stemmetal**: Antal stemmer

Modellen aggregerer automatisk alle stemmer (både listestemmer og personlige stemmer) per valgsted og parti.

## Eksempel på valgaften-workflow

```python
from valgmodel import Valgmodel

# 1. Initialiser modellen inden valget starter
model = Valgmodel("Kommunalvalg_2021_København_17-11-2025 20.11.26.csv")

# 2. Når de første valgsteder er optalt
optalte = ["1. 1. Østerbro"]
pred = model.prediкer_fra_csv("live_data.csv", optalte)
model.print_resultat(pred, f"Prediкtion ({len(optalte)} valgsteder)")

# 3. Opdater løbende når flere valgsteder kommer ind
optalte = ["1. 1. Østerbro", "1. 2. Østerbro", "2. 1. Nørrebro"]
pred = model.prediкer_fra_csv("live_data.csv", optalte)
model.print_resultat(pred, f"Prediкtion ({len(optalte)} valgsteder)")

# 4. Fortsæt indtil alle er optalt
```

## Begrænsninger og overvejelser

- **Repræsentativitet**: Modellen antager at de optalte valgsteder er repræsentative. Hvis f.eks. kun byvalgsteder er optalt, kan prediктionen være skæv.

- **Nye partier**: Partier der ikke stillede op ved forrige valg håndteres ved at bruge deres nuværende procent direkte.

- **Store swings**: Ved meget store lokale swings kan modellen give unøjagtige resultater.

- **Små valgsteder**: Med meget få optalte valgsteder er usikkerheden stor.

## Test

Kør eksemplet:

```bash
python valgmodel.py
```

Dette viser:
1. Det faktiske resultat fra 2021
2. En simuleret prediкtion baseret på nogle få valgsteder
3. Forskellen mellem prediкtion og faktisk resultat

## Licens

MIT
