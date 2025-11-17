"""
Simpel workflow til valgnatten.

Dette script viser hvordan du bruger systemet på valgnatten:
1. Load valgmodel med forrige valgs data
2. Peg på live CSV fil (opdateres løbende)
3. Generer JSON automatisk
4. HTML opdaterer automatisk
"""

from valgmodel import Valgmodel
from generate_live_data import generer_live_data, gem_live_data_json
import time
import os


def watch_and_update(
    model: Valgmodel,
    live_csv_path: str,
    output_json: str = "live_data.json",
    interval: int = 5
):
    """
    Overvåger live CSV fil og opdaterer JSON automatisk.

    Args:
        model: Valgmodel instans
        live_csv_path: Sti til live CSV fil (opdateres af valgsystem)
        output_json: Output JSON fil som HTML'en læser
        interval: Sekunder mellem opdateringer
    """
    print("="*70)
    print("VALGNAT LIVE OPDATERING")
    print("="*70)
    print(f"\nOvervåger: {live_csv_path}")
    print(f"Output: {output_json}")
    print(f"Opdatering hver {interval} sekund")
    print("\nTryk Ctrl+C for at stoppe\n")

    last_mtime = 0

    try:
        while True:
            # Check om CSV'en er opdateret
            if os.path.exists(live_csv_path):
                current_mtime = os.path.getmtime(live_csv_path)

                if current_mtime != last_mtime:
                    last_mtime = current_mtime

                    print(f"[{time.strftime('%H:%M:%S')}] Ny data detekteret - opdaterer...")

                    try:
                        # Generer ny JSON
                        data = generer_live_data(model, live_csv_path, 55)
                        gem_live_data_json(data, output_json)

                        # Vis status
                        pct = data['metadata']['procent_optalt']
                        antal = data['metadata']['antal_optalte_valgsteder']
                        print(f"  ✓ Opdateret: {antal} valgsteder optalt ({pct:.1f}%)")

                        # Vis top 3
                        print("  Top 3 partier:")
                        for parti in data['partier'][:3]:
                            print(f"    {parti['bogstav']}: {parti['mandater']} mandater")

                    except Exception as e:
                        print(f"  ✗ Fejl: {e}")
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] Ingen nye data...", end='\r')

            else:
                print(f"[{time.strftime('%H:%M:%S')}] Venter på CSV fil...", end='\r')

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n\nAfslutter overvågning...")


def simpel_workflow():
    """
    Viser det simpleste workflow.
    """
    print("="*70)
    print("SIMPEL VALGNAT WORKFLOW")
    print("="*70)
    print("""
TRIN 1: Forberedelse (inden valget)
------------------------------------
# Initialiser model med data fra forrige valg
model = Valgmodel("forrige_valg_2021.csv")

TRIN 2: På valgnatten (automatisk loop)
----------------------------------------
# Dit valgsystem gemmer løbende data til live_data.csv
# (CSV'en indeholder kun de valgsteder der er optalt indtil videre)

# Kør dette script i et loop:
while True:
    data = generer_live_data(model, "live_data.csv", 55)
    gem_live_data_json(data, "live_data.json")
    time.sleep(5)  # Opdater hver 5. sekund

TRIN 3: Visning
---------------
# Åbn live_mandatfordeling.html i browser
# Den opdaterer automatisk hvert 5. sekund

# Eller kør server:
python serve_live.py


KOMPLET EKSEMPEL:
-----------------
    """)

    print("""
from valgmodel import Valgmodel
from generate_live_data import generer_live_data, gem_live_data_json

# 1. Initialiser model
model = Valgmodel("Kommunalvalg_2021_København.csv")

# 2. På valgnatten - gentag løbende
data = generer_live_data(model, "live_data.csv", 55)
gem_live_data_json(data, "live_data.json")

# 3. HTML'en opdaterer automatisk!
    """)


if __name__ == "__main__":
    simpel_workflow()

    print("\n\nVil du overvåge en live CSV fil nu?")
    print("Dette kræver at du har en live_data.csv fil.")
    print("\nTryk Enter for at fortsætte eller Ctrl+C for at stoppe...")

    try:
        input()

        # Brug 2021 data som eksempel
        model = Valgmodel("Kommunalvalg_2021_København_17-11-2025 20.11.26.csv")

        # Overvåg filen
        watch_and_update(
            model,
            "Kommunalvalg_2021_København_17-11-2025 20.11.26.csv",
            "live_data.json",
            5
        )

    except KeyboardInterrupt:
        print("\n\nAfsluttet.")
