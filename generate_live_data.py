"""
Genererer JSON data til live HTML visning.
"""

import json
from valgmodel import Valgmodel
from mandatfordeling import Mandatfordeling, KØBENHAVN_VALGFORBUND


def generer_live_data(
    model: Valgmodel,
    nuværende_data_csv: str,
    total_mandater: int = 55
) -> dict:
    """
    Genererer komplet data til live visning.

    Automatisk detekterer hvilke valgsteder der er optalt i CSV'en.

    Args:
        model: Valgmodel instans
        nuværende_data_csv: Sti til CSV med nuværende valgdata (kun optalte valgsteder)
        total_mandater: Antal mandater at fordele

    Returns:
        Dictionary med komplet data til visning
    """
    # 1. Load nuværende data og find automatisk optalte valgsteder
    nuværende_data = model._load_data(nuværende_data_csv)
    optalte_valgsteder = list(nuværende_data['Valgsted'].unique())

    # 2. Få prediкtion
    prediкtion_procent = model.prediкer(nuværende_data, optalte_valgsteder)

    # 2. Konverter til stemmer (antag samme total som forrige valg)
    total_stemmer = sum(model.forrige_valg_data['Stemmer'])
    stemmer = {
        parti: int(pct / 100 * total_stemmer)
        for parti, pct in prediкtion_procent.items()
    }

    # 3. Fordel mandater
    mf = Mandatfordeling(KØBENHAVN_VALGFORBUND)
    parti_mandater, forbund_mandater = mf.fordel_mandater(stemmer, total_mandater)

    # 4. Byg output struktur
    output = {
        "metadata": {
            "total_mandater": total_mandater,
            "total_stemmer": total_stemmer,
            "antal_optalte_valgsteder": len(optalte_valgsteder),
            "procent_optalt": len(optalte_valgsteder) / len(model.forrige_valg_data['Valgsted'].unique()) * 100
        },
        "forbund": [],
        "partier": []
    }

    # Parti farver (standard danske partier)
    parti_farver = {
        "A": "#E3515D",  # Socialdemokratiet - rød
        "B": "#EB4295",  # Radikale - magenta
        "C": "#429969",  # Konservative - grøn
        "D": "#5BC0EB",  # Nye Borgerlige - lyseblå
        "F": "#9C1D5A",  # SF - lilla
        "I": "#3FB2BE",  # Liberal Alliance - cyan
        "O": "#3D6F8D",  # Dansk Folkeparti - blå
        "V": "#254D73",  # Venstre - mørkeblå
        "Ø": "#E6801A",  # Enhedslisten - orange/rød
        "Å": "#50A64E",  # Alternativet - grøn
        "K": "#F4CE50",  # Kristendemokraterne - gul
        "M": "#4BA146",  # Danmark for Alle - grøn
        "N": "#DC143C",  # Kommunisterne - rød
    }

    # Default farve for andre partier
    default_farve = "#999999"

    # Byg forbund data
    for forbund_navn, forbund_partier in KØBENHAVN_VALGFORBUND.items():
        forbund_stemmer = sum(stemmer.get(p, 0) for p in forbund_partier)
        forbund_pct = forbund_stemmer / total_stemmer * 100
        forbund_m = forbund_mandater.get(forbund_navn, 0)

        forbund_data = {
            "navn": forbund_navn,
            "mandater": forbund_m,
            "stemmer": forbund_stemmer,
            "procent": round(forbund_pct, 2),
            "partier": []
        }

        # Byg parti data i forbund
        for parti in forbund_partier:
            parti_stemmer = stemmer.get(parti, 0)
            if parti_stemmer == 0:
                continue

            parti_pct = parti_stemmer / total_stemmer * 100
            parti_m = parti_mandater.get(parti, 0)

            parti_data = {
                "bogstav": parti,
                "mandater": parti_m,
                "stemmer": parti_stemmer,
                "procent": round(parti_pct, 2),
                "farve": parti_farver.get(parti, default_farve)
            }

            forbund_data["partier"].append(parti_data)
            output["partier"].append(parti_data)

        # Sorter partier i forbund efter mandater
        forbund_data["partier"].sort(key=lambda x: x["mandater"], reverse=True)

        output["forbund"].append(forbund_data)

    # Sorter forbund efter mandater
    output["forbund"].sort(key=lambda x: x["mandater"], reverse=True)

    # Sorter alle partier efter mandater
    output["partier"].sort(key=lambda x: x["mandater"], reverse=True)

    return output


def gem_live_data_json(output: dict, filnavn: str = "live_data.json"):
    """Gemmer data som JSON fil."""
    with open(filnavn, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # Test eksempel
    model = Valgmodel("Kommunalvalg_2021_København_17-11-2025 20.11.26.csv")

    # Generer data
    # CSV'en indeholder automatisk hvilke valgsteder der er optalt
    data = generer_live_data(
        model,
        "Kommunalvalg_2021_København_17-11-2025 20.11.26.csv",
        55
    )

    # Gem som JSON
    gem_live_data_json(data)

    print("Live data genereret og gemt i live_data.json")
    print(f"\nMetadata:")
    print(f"  Total mandater: {data['metadata']['total_mandater']}")
    print(f"  Optalt: {data['metadata']['antal_optalte_valgsteder']} valgsteder ({data['metadata']['procent_optalt']:.1f}%)")
    print(f"\nTop 3 partier:")
    for parti in data['partier'][:3]:
        print(f"  {parti['bogstav']}: {parti['mandater']} mandater ({parti['procent']:.2f}%)")
