"""
Komplet eksempel på live valgnat workflow.

Dette script viser hvordan du:
1. Loader valgmodellen
2. Får live data (simuleret)
3. Prediктerer resultatet
4. Fordeler mandater
5. Genererer JSON til HTML visning
"""

from valgmodel import Valgmodel
from generate_live_data import generer_live_data, gem_live_data_json, NYE_PARTIER
import time


def simuler_valgnat():
    """
    Simulerer en valgnat hvor flere og flere valgsteder optælles.
    """
    print("="*70)
    print("LIVE VALGNAT SIMULATION")
    print("="*70)
    print("\nInitialiserer valgmodel med data fra 2021...")

    # 1. Initialiser model
    model = Valgmodel(
        "Kommunalvalg_2021_København_17-11-2025 20.11.26.csv",
        nye_partier=NYE_PARTIER
    )

    # 2. Hent alle valgsteder
    alle_valgsteder = list(model.forrige_valg_data['Valgsted'].unique())
    total_valgsteder = len(alle_valgsteder)

    print(f"Total antal valgsteder: {total_valgsteder}")
    print("\nSimulerer valgnat...\n")

    # 3. Simuler progressiv optælling
    milestones = [
        (0.10, "Første resultater"),
        (0.25, "En fjerdedel optalt"),
        (0.50, "Halvdelen optalt"),
        (0.75, "Tre fjerdedele optalt"),
        (1.00, "Alle valgsteder optalt")
    ]

    for pct, beskrivelse in milestones:
        antal = int(total_valgsteder * pct)
        if antal == 0:
            antal = 1

        optalte = alle_valgsteder[:antal]

        print(f"\n{'='*70}")
        print(f"🕐 {beskrivelse} ({antal} af {total_valgsteder} valgsteder, {pct*100:.0f}%)")
        print(f"{'='*70}")

        # Generer live data
        data = generer_live_data(
            model,
            optalte,
            "Kommunalvalg_2021_København_17-11-2025 20.11.26.csv",
            55
        )

        # Gem til JSON (HTML'en læser denne fil)
        gem_live_data_json(data, "live_data.json")

        # Vis top 5
        print("\nTop 5 partier:")
        for i, parti in enumerate(data['partier'][:5], 1):
            print(f"  {i}. {parti['bogstav']}: {parti['mandater']:2d} mandater "
                  f"({parti['procent']:5.2f}% af stemmerne)")

        # Vis forbund
        print("\nMandater per forbund:")
        for forbund in data['forbund']:
            if forbund['mandater'] > 0:
                print(f"  {forbund['navn']}: {forbund['mandater']} mandater")

        # Pause mellem opdateringer (i virkeligheden ville du vente på rigtige data)
        if pct < 1.0:
            print("\nVenter 2 sekunder før næste opdatering...")
            time.sleep(2)

    print("\n" + "="*70)
    print("VALGET ER AFSLUTTET!")
    print("="*70)
    print("\nÅbn live_mandatfordeling.html i din browser for at se visualiseringen.")
    print("Eller kør: python serve_live.py")


def vis_workflow():
    """Viser workflow beskrivelse."""
    print("\n" + "="*70)
    print("WORKFLOW PÅ VALGNATTEN")
    print("="*70)
    print("""
1. FORBEREDELSE (inden valget):
   - Initialiser Valgmodel med data fra forrige valg
   - Start HTTP server: python serve_live.py
   - Åbn live_mandatfordeling.html i browser

2. PÅ VALGNATTEN (når data kommer ind):
   # Hent liste over optalte valgsteder
   optalte_valgsteder = ["1. 1. Østerbro", "2. 1. Nørrebro", ...]

   # Generer live data
   data = generer_live_data(
       model,
       optalte_valgsteder,
       "live_data.csv",  # Sti til live CSV data
       55
   )

   # Gem som JSON
   gem_live_data_json(data, "live_data.json")

   # HTML siden opdaterer automatisk hvert 5. sekund!

3. AUTOMATISERING (valgtysk):
   - Sæt dette script op til at køre automatisk når ny data kommer
   - Eller kør i en loop der checker for nye valgsteder
   - HTML siden vil opdatere automatisk

4. EFTER VALGET:
   - Den endelige mandatfordeling er klar
   - Du kan gemme HTML siden som PDF til dokumentation
    """)


if __name__ == "__main__":
    vis_workflow()
    print("\n\nVil du køre en simulation? (Dette tager ca. 10 sekunder)")
    print("Tryk Enter for at fortsætte eller Ctrl+C for at stoppe...")
    try:
        input()
        simuler_valgnat()
    except KeyboardInterrupt:
        print("\n\nSimulation afbrudt.")
