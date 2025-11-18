"""
Test integration mellem valgmodel og mandatfordeling.
"""

from valgmodel import Valgmodel
from mandatfordeling import Mandatfordeling, KØBENHAVN_VALGFORBUND

# Partier der skal behandles som nye
NYE_PARTIER = ["M", "N", "Æ", "Q"]


def test_fuld_integration():
    """Test komplet flow fra stemmer til mandater."""
    print("="*70)
    print("INTEGRATION TEST: Valgmodel + Mandatfordeling")
    print("="*70)

    # 1. Load valgmodel
    model = Valgmodel(
        "Kommunalvalg_2021_København_17-11-2025 20.11.26.csv",
        nye_partier=NYE_PARTIER
    )

    # 2. Få stemmer fra 2021 (i virkeligheden ville dette være prediкtion)
    print("\nBruger 2021-resultatet som eksempel...")
    procent_resultat = model.forrige_valg_samlet

    # Konverter procenter til stemmer (antag 300,000 total stemmer)
    total_stemmer = 307046  # Faktisk antal fra 2021
    stemmer = {
        parti: int(pct / 100 * total_stemmer)
        for parti, pct in procent_resultat.items()
    }

    print(f"\nTotal stemmer: {total_stemmer:,}")

    # 3. Fordel mandater
    mf = Mandatfordeling(KØBENHAVN_VALGFORBUND)
    parti_mandater, forbund_mandater = mf.fordel_mandater(stemmer, 55)

    # 4. Vis resultat
    mf.print_resultat(stemmer, parti_mandater, forbund_mandater, 55)


if __name__ == "__main__":
    test_fuld_integration()
