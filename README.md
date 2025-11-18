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

### ⚠️ VIGTIGT at forstå

Modellen sammenligner **nuværende valgdata** med **forrige valgdata** for at beregne swing.

**På valgnatten** vil du have:
- **Forrige valg**: Komplet data fra 2021 (alle valgsteder)
- **Nuværende valg**: Delvis live data fra det nye valg (kun optalte valgsteder)

Modellen beregner swing for hvert parti og prediктerer det endelige resultat.

**VIGTIGT**: Hvis du bruger samme data til både "nuværende" og "forrige" (som i grundeksemplet), vil swing altid være 1.0, og prediктionen vil være identisk med forrige valgs resultat. Dette er ikke en fejl - det er sådan modellen fungerer! På valgnatten vil data være forskellige.

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

### Grundlæggende test

```bash
python valgmodel.py
```

Dette viser modellens grundstruktur (men giver samme resultat som 2021 fordi vi bruger samme data).

### Realistisk test med faktiske ændringer

```bash
python test_realistic.py
```

Dette simulerer et rigtigt valg hvor:
- Enhedslisten (Ø) går 5pp frem
- Socialdemokratiet (A) går 3pp tilbage
- Konservative (C) går 2pp tilbage

Og viser hvordan modellen prediктerer korrekt baseret på delvist optalte valgsteder.

## Mandatfordeling

Systemet inkluderer også D'Hondt-metoden til mandatfordeling med valgforbund.

### Brug

```python
from valgmodel import Valgmodel
from mandatfordeling import Mandatfordeling, KØBENHAVN_VALGFORBUND
from generate_live_data import generer_live_data, gem_live_data_json

# 1. Få prediktion fra valgmodellen
model = Valgmodel("forrige_valg.csv")
# live_data.csv indeholder kun optalte valgsteder

# 2. Generer komplet data (prediktion + mandatfordeling)
data = generer_live_data(model, "live_data.csv", 55)

# 3. Gem som JSON til HTML visning
gem_live_data_json(data, "live_data.json")
```

### Valgforbund

Mandatfordelingen bruger følgende valgforbund for København:

- **Rød blok 1**: A, B, M (Socialdemokratiet, Radikale, Danmark for Alle)
- **Blå blok**: C, D, I, K, O, V, Æ (Konservative, Nye Borgerlige, Liberal Alliance, Kristendemokraterne, Dansk Folkeparti, Venstre)
- **Liste-alliancen**: E, J, P, Q, R, T, Z
- **Rød blok 2**: F, N, Ø, Å (SF, Kommunisterne, Enhedslisten, Alternativet)

### Test mandatfordeling

```bash
python mandatfordeling.py
python integration_test.py
```

## Live HTML Visning

Systemet inkluderer en live HTML interface til at vise mandatfordelingen visuelt.

### Kom i gang

```bash
# 1. Generer live data
python generate_live_data.py

# 2. Start web server
python serve_live.py

# 3. Åbn http://localhost:8000/live_mandatfordeling.html i din browser
```

HTML'en opdaterer automatisk hvert 5. sekund når `live_data.json` ændres.

### På valgnatten

```python
from valgmodel import Valgmodel
from generate_live_data import generer_live_data, gem_live_data_json
import time

# Initialiser model
model = Valgmodel("Kommunalvalg_2021_København.csv")

# Loop der kører hele valgnatten
while True:
    # Din live CSV opdateres af valgsystemet
    # Den indeholder kun valgsteder der er optalt
    data = generer_live_data(model, "live_data.csv", 55)
    gem_live_data_json(data, "live_data.json")

    # HTML opdaterer automatisk!
    time.sleep(5)
```

Se `valgnat_workflow.py` for komplet eksempel.

## Filstruktur

- `valgmodel.py` - Hoved valgmodel (swing-baseret prediktion)
- `mandatfordeling.py` - D'Hondt mandatfordeling med valgforbund
- `generate_live_data.py` - Genererer JSON data fra CSV
- `live_mandatfordeling.html` - Live HTML visning
- `serve_live.py` - Simpel web server
- `valgnat_workflow.py` - Komplet workflow eksempel
- `test_realistic.py` - Test med simulerede ændringer
- `requirements.txt` - Python dependencies

## Licens

MIT
