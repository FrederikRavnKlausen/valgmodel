"""
Simulerer forskellige scenarier for at demonstrere hvordan modellen virker.

Dette script viser:
1. Prediкtion med forskellige antal optalte valgsteder
2. Hvordan modellen håndterer forskellige demografiske områder
3. Nøjagtigheden af prediктionen når flere valgsteder optælles
"""

from valgmodel import Valgmodel
import pandas as pd


def simuler_gradvis_optælling():
    """
    Simulerer en gradvis optælling af valgsteder gennem valgnatten.
    """
    print("\n" + "="*70)
    print("SIMULERING: Gradvis optælling af valgsteder")
    print("="*70)

    model = Valgmodel("Kommunalvalg_2021_København_17-11-2025 20.11.26.csv")

    # Hent alle unikke valgsteder
    alle_valgsteder = model.forrige_valg_data['Valgsted'].unique().tolist()

    print(f"\nTotal antal valgsteder: {len(alle_valgsteder)}")

    # Simuler optælling af 5%, 10%, 25%, 50%, 75%, 100%
    procenter = [5, 10, 25, 50, 75, 100]

    for pct in procenter:
        antal = max(1, int(len(alle_valgsteder) * pct / 100))
        valgsteder = alle_valgsteder[:antal]

        # I denne simulation bruger vi samme data (2021) for både "nuværende" og "forrige"
        # På valgnatten ville "nuværende" være live data
        pred = model.prediкer_fra_csv(
            "Kommunalvalg_2021_København_17-11-2025 20.11.26.csv",
            valgsteder
        )

        print(f"\n{pct}% optalt ({antal} valgsteder):")
        print("-" * 70)

        # Vis top 5 partier
        sorteret = sorted(pred.items(), key=lambda x: x[1], reverse=True)[:5]
        for parti, procent in sorteret:
            faktisk = model.forrige_valg_samlet[parti]
            diff = procent - faktisk
            print(f"{parti}: {procent:5.2f}% (faktisk: {faktisk:5.2f}%, diff: {diff:+5.2f})")


def analyser_geografisk_bias():
    """
    Viser hvordan modellen kan give bias hvis kun visse typer valgsteder er optalt.
    """
    print("\n" + "="*70)
    print("ANALYSE: Geografisk bias")
    print("="*70)

    model = Valgmodel("Kommunalvalg_2021_København_17-11-2025 20.11.26.csv")

    # Få valgsteder fra forskellige områder
    østerbro = [v for v in model.forrige_valg_data['Valgsted'].unique()
                if 'Østerbro' in v]
    nørrebro = [v for v in model.forrige_valg_data['Valgsted'].unique()
                if 'Nørrebro' in v]
    vesterbro = [v for v in model.forrige_valg_data['Valgsted'].unique()
                 if 'Vesterbro' in v]

    print(f"\nØsterbro: {len(østerbro)} valgsteder")
    print(f"Nørrebro: {len(nørrebro)} valgsteder")
    print(f"Vesterbro: {len(vesterbro)} valgsteder")

    områder = [
        ("Kun Østerbro", østerbro[:10]),
        ("Kun Nørrebro", nørrebro[:10]),
        ("Kun Vesterbro", vesterbro[:10]),
        ("Mix af alle", østerbro[:5] + nørrebro[:5] + vesterbro[:5])
    ]

    for navn, valgsteder in områder:
        if len(valgsteder) == 0:
            continue

        print(f"\n{navn} ({len(valgsteder)} valgsteder):")
        print("-" * 70)

        pred = model.prediкer_fra_csv(
            "Kommunalvalg_2021_København_17-11-2025 20.11.26.csv",
            valgsteder
        )

        # Vis top 5
        sorteret = sorted(pred.items(), key=lambda x: x[1], reverse=True)[:5]
        for i, (parti, procent) in enumerate(sorteret, 1):
            print(f"{i}. {parti}: {procent:5.2f}%")


def vis_alle_valgsteder():
    """
    Viser en liste over alle valgsteder i datasættet.
    """
    print("\n" + "="*70)
    print("ALLE VALGSTEDER I DATASÆTTET")
    print("="*70)

    model = Valgmodel("Kommunalvalg_2021_København_17-11-2025 20.11.26.csv")
    valgsteder = sorted(model.forrige_valg_data['Valgsted'].unique())

    print(f"\nTotal: {len(valgsteder)} valgsteder\n")

    # Gruppér efter område
    områder = {}
    for v in valgsteder:
        # Ekstrahér område (tekst efter første nummer)
        parts = v.split('.')
        if len(parts) >= 3:
            område = parts[2].strip()
            if område not in områder:
                områder[område] = []
            områder[område].append(v)

    for område, steder in sorted(områder.items()):
        print(f"\n{område} ({len(steder)} valgsteder):")
        for sted in steder[:5]:  # Vis de første 5
            print(f"  - {sted}")
        if len(steder) > 5:
            print(f"  ... og {len(steder)-5} flere")


def eksempel_live_brug():
    """
    Viser hvordan modellen kan bruges på valgnatten med løbende opdateringer.
    """
    print("\n" + "="*70)
    print("EKSEMPEL: Live brug på valgnatten")
    print("="*70)

    model = Valgmodel("Kommunalvalg_2021_København_17-11-2025 20.11.26.csv")

    print("""
Dette er et eksempel på hvordan du kan bruge modellen live på valgnatten:

1. Start med at initialisere modellen med data fra forrige valg:
   model = Valgmodel("forrige_valg.csv")

2. Når de første resultater kommer ind, opdater listen af optalte valgsteder:
   optalte_valgsteder = ["1. 1. Østerbro", "1. 2. Østerbro"]

3. Kør prediктionen:
   pred = model.prediкer_fra_csv("live_data.csv", optalte_valgsteder)
   model.print_resultat(pred)

4. Opdater optalte_valgsteder løbende og kør prediктionen igen.

VIGTIG NOTE:
- På valgnatten skal du have en CSV med live data fra det nuværende valg
- Denne CSV skal have samme format som data fra forrige valg
- Du skal holde styr på hvilke valgsteder der er helt optalt
- Vær opmærksom på at de første valgsteder måske ikke er repræsentative!
    """)

    # Simuler en simpel progression
    alle_valgsteder = model.forrige_valg_data['Valgsted'].unique().tolist()

    print("\nSimuleret progression gennem aftenen:")
    print("-" * 70)

    tidspunkter = [
        (20.00, 10, "Første resultater"),
        (21.00, 50, "Halvdelen optalt"),
        (22.00, 150, "Mange resultater inde"),
        (23.00, 250, "Næsten færdig")
    ]

    for tid, antal, beskrivelse in tidspunkter:
        valgsteder = alle_valgsteder[:antal]
        pred = model.prediкer_fra_csv(
            "Kommunalvalg_2021_København_17-11-2025 20.11.26.csv",
            valgsteder
        )

        print(f"\nKl. {tid:.2f} - {beskrivelse} ({antal} valgsteder, {antal/len(alle_valgsteder)*100:.1f}%)")
        sorteret = sorted(pred.items(), key=lambda x: x[1], reverse=True)[:3]
        for parti, procent in sorteret:
            print(f"  {parti}: {procent:5.2f}%")


if __name__ == "__main__":
    # Kør alle simuleringer
    vis_alle_valgsteder()
    simuler_gradvis_optælling()
    analyser_geografisk_bias()
    eksempel_live_brug()

    print("\n" + "="*70)
    print("Simulering afsluttet!")
    print("="*70)
