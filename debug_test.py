"""
Debug script til at teste om modellen filtrerer valgsteder korrekt.
"""

from valgmodel import Valgmodel
import pandas as pd


def test_filtrering():
    """Test om modellen faktisk filtrerer på valgsteder."""
    print("="*70)
    print("DEBUG: Test af filtrering")
    print("="*70)

    model = Valgmodel("Kommunalvalg_2021_København_17-11-2025 20.11.26.csv")

    # Få alle valgsteder
    alle_valgsteder = sorted(model.forrige_valg_data['Valgsted'].unique())
    print(f"\nTotal antal valgsteder i data: {len(alle_valgsteder)}")

    # Test 1: Kun ét valgsted
    print("\n" + "-"*70)
    print("TEST 1: Kun ét valgsted")
    print("-"*70)

    et_valgsted = [alle_valgsteder[0]]
    print(f"Valgsted: {et_valgsted[0]}")

    # Beregn resultat for dette ene valgsted
    resultat_et = model._beregn_resultat_for_valgsteder(
        model.forrige_valg_data,
        et_valgsted
    )

    print("\nResultat for dette ene valgsted:")
    sorteret = sorted(resultat_et.items(), key=lambda x: x[1], reverse=True)[:5]
    for parti, pct in sorteret:
        print(f"  {parti}: {pct:.2f}%")

    # Test 2: Alle valgsteder
    print("\n" + "-"*70)
    print("TEST 2: Alle valgsteder")
    print("-"*70)

    resultat_alle = model._beregn_resultat_for_valgsteder(
        model.forrige_valg_data,
        alle_valgsteder
    )

    print("\nResultat for alle valgsteder:")
    sorteret = sorted(resultat_alle.items(), key=lambda x: x[1], reverse=True)[:5]
    for parti, pct in sorteret:
        print(f"  {parti}: {pct:.2f}%")

    # Sammenlign
    print("\n" + "-"*70)
    print("Sammenligning:")
    print("-"*70)
    print(f"Er resultaterne forskellige? {resultat_et != resultat_alle}")

    # Test 3: Tæl stemmer
    print("\n" + "-"*70)
    print("TEST 3: Stemmeantal")
    print("-"*70)

    stemmer_et = model.forrige_valg_data[
        model.forrige_valg_data['Valgsted'].isin(et_valgsted)
    ]['Stemmer'].sum()

    stemmer_alle = model.forrige_valg_data['Stemmer'].sum()

    print(f"Stemmer for ét valgsted: {stemmer_et:,}")
    print(f"Stemmer for alle valgsteder: {stemmer_alle:,}")
    print(f"Forholdet: {stemmer_et/stemmer_alle*100:.2f}%")


def test_prediktion_detail():
    """Test prediktion i detaljer."""
    print("\n" + "="*70)
    print("DEBUG: Detaljeret test af prediktion")
    print("="*70)

    model = Valgmodel("Kommunalvalg_2021_København_17-11-2025 20.11.26.csv")

    # Brug nogle få valgsteder
    valgsteder = [
        "12. 3. Nord",
        "17. 4. Nord"
    ]

    print(f"\nTest valgsteder: {valgsteder}")

    # Manuelt beregn p, q, r
    print("\n" + "-"*70)
    print("Beregning af p, q, r:")
    print("-"*70)

    # p: Resultat på disse valgsteder (nuværende - bruger samme data som test)
    p = model._beregn_resultat_for_valgsteder(
        model.forrige_valg_data,
        valgsteder
    )

    # q: Resultat på disse valgsteder (forrige)
    q = model._beregn_resultat_for_valgsteder(
        model.forrige_valg_data,
        valgsteder
    )

    # r: Samlet resultat (forrige)
    r = model.forrige_valg_samlet

    print("\nTop 3 partier:")
    print("\n  p (nuværende, disse valgsteder):")
    for parti, pct in sorted(p.items(), key=lambda x: x[1], reverse=True)[:3]:
        print(f"    {parti}: {pct:.2f}%")

    print("\n  q (forrige, disse valgsteder):")
    for parti, pct in sorted(q.items(), key=lambda x: x[1], reverse=True)[:3]:
        print(f"    {parti}: {pct:.2f}%")

    print("\n  r (forrige, alle valgsteder):")
    for parti, pct in sorted(r.items(), key=lambda x: x[1], reverse=True)[:3]:
        print(f"    {parti}: {pct:.2f}%")

    # Beregn swing
    print("\n" + "-"*70)
    print("Swing (p/q) for top 3:")
    print("-"*70)

    for parti in sorted(r.items(), key=lambda x: x[1], reverse=True)[:3]:
        parti_navn = parti[0]
        if parti_navn in q and q[parti_navn] > 0 and parti_navn in p:
            swing = p[parti_navn] / q[parti_navn]
            print(f"  {parti_navn}: {p[parti_navn]:.2f}% / {q[parti_navn]:.2f}% = {swing:.4f}")

    # Kør faktisk prediktion
    pred = model.prediкer(model.forrige_valg_data, valgsteder)

    print("\n" + "-"*70)
    print("Prediktion (top 3):")
    print("-"*70)
    for parti, pct in sorted(pred.items(), key=lambda x: x[1], reverse=True)[:3]:
        print(f"  {parti}: {pct:.2f}%")


def test_forskellige_valgsteder():
    """Test om forskellige valgsteder giver forskellige resultater."""
    print("\n" + "="*70)
    print("DEBUG: Test forskellige valgsteder")
    print("="*70)

    model = Valgmodel("Kommunalvalg_2021_København_17-11-2025 20.11.26.csv")

    # Find valgsteder fra forskellige områder
    alle = model.forrige_valg_data['Valgsted'].unique()

    # Få resultater for forskellige områder
    områder = {}
    for valgsted in alle:
        område = valgsted.split('.')[-1].strip() if '.' in valgsted else valgsted
        if område not in områder:
            områder[område] = []
        områder[område].append(valgsted)

    # Tag nogle forskellige områder
    test_områder = list(områder.items())[:5]

    for område_navn, valgsteder_liste in test_områder:
        if len(valgsteder_liste) == 0:
            continue

        valgsted = [valgsteder_liste[0]]

        resultat = model._beregn_resultat_for_valgsteder(
            model.forrige_valg_data,
            valgsted
        )

        print(f"\n{område_navn} ({valgsted[0]}):")
        top3 = sorted(resultat.items(), key=lambda x: x[1], reverse=True)[:3]
        for parti, pct in top3:
            print(f"  {parti}: {pct:.2f}%")


if __name__ == "__main__":
    test_filtrering()
    test_forskellige_valgsteder()
    test_prediktion_detail()
