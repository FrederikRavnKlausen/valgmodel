"""
Mandatfordeling ved D'Hondt-metoden med valgforbund.

D'Hondt-metoden:
1. Divider hvert partis/forbunds stemmer med 1, 2, 3, 4, ...
2. De højeste kvotienter får mandater

Med valgforbund:
1. Fordel først mandater mellem valgforbund (D'Hondt)
2. Fordel derefter mandater internt i hvert forbund (D'Hondt)
"""

from typing import Dict, List, Tuple
from collections import defaultdict


class Mandatfordeling:
    """
    Håndterer mandatfordeling ved D'Hondt-metoden med valgforbund.
    """

    def __init__(self, valgforbund: Dict[str, List[str]]):
        """
        Initialiserer mandatfordelingsalgoritmen.

        Args:
            valgforbund: Dictionary hvor key er forbundsnavn og value er liste af partibogstaver
                        Eksempel: {"Forbund1": ["A", "B"], "Forbund2": ["C", "D"]}
        """
        self.valgforbund = valgforbund

        # Lav reverse mapping: parti -> forbund
        self.parti_til_forbund = {}
        for forbund_navn, partier in valgforbund.items():
            for parti in partier:
                self.parti_til_forbund[parti] = forbund_navn

    def dhondt(
        self,
        stemmer: Dict[str, int],
        antal_mandater: int
    ) -> Dict[str, int]:
        """
        Fordeler mandater ved D'Hondt-metoden.

        Args:
            stemmer: Dictionary med parti/forbund -> antal stemmer
            antal_mandater: Antal mandater at fordele

        Returns:
            Dictionary med parti/forbund -> antal mandater
        """
        if antal_mandater == 0:
            return {parti: 0 for parti in stemmer.keys()}

        mandater = {parti: 0 for parti in stemmer.keys()}

        # Fordel mandater én ad gangen
        for _ in range(antal_mandater):
            # Beregn kvotient for hvert parti: stemmer / (mandater + 1)
            kvotienter = {
                parti: stemmer[parti] / (mandater[parti] + 1)
                for parti in stemmer.keys()
                if stemmer[parti] > 0
            }

            if not kvotienter:
                break

            # Find parti med højeste kvotient
            vinder = max(kvotienter.keys(), key=lambda p: kvotienter[p])
            mandater[vinder] += 1

        return mandater

    def fordel_mandater(
        self,
        stemmer: Dict[str, int],
        total_mandater: int
    ) -> Tuple[Dict[str, int], Dict[str, int]]:
        """
        Fordeler mandater med valgforbund.

        Proces:
        1. Summer stemmer for hvert forbund
        2. Fordel mandater mellem forbund (D'Hondt)
        3. Fordel mandater internt i hvert forbund (D'Hondt)

        Args:
            stemmer: Dictionary med partibogstav -> antal stemmer
            total_mandater: Total antal mandater at fordele

        Returns:
            Tuple med:
            - Dictionary med partibogstav -> antal mandater
            - Dictionary med forbundsnavn -> antal mandater
        """
        # 1. Summer stemmer per forbund
        forbund_stemmer = defaultdict(int)
        for parti, antal in stemmer.items():
            if parti in self.parti_til_forbund:
                forbund = self.parti_til_forbund[parti]
                forbund_stemmer[forbund] += antal

        # 2. Fordel mandater mellem forbund
        forbund_mandater = self.dhondt(dict(forbund_stemmer), total_mandater)

        # 3. Fordel mandater internt i hvert forbund
        parti_mandater = {}

        for forbund_navn, forbund_partier in self.valgforbund.items():
            # Hent stemmer for partier i dette forbund
            forbund_parti_stemmer = {
                parti: stemmer.get(parti, 0)
                for parti in forbund_partier
            }

            # Fjern partier uden stemmer
            forbund_parti_stemmer = {
                p: s for p, s in forbund_parti_stemmer.items() if s > 0
            }

            # Fordel forbundets mandater mellem dets partier
            antal_mandater_til_forbund = forbund_mandater.get(forbund_navn, 0)

            if antal_mandater_til_forbund > 0 and forbund_parti_stemmer:
                parti_fordeling = self.dhondt(
                    forbund_parti_stemmer,
                    antal_mandater_til_forbund
                )
                parti_mandater.update(parti_fordeling)
            else:
                # Forbundet fik ingen mandater
                for parti in forbund_partier:
                    parti_mandater[parti] = 0

        # Tilføj partier der ikke er i noget forbund
        for parti in stemmer.keys():
            if parti not in parti_mandater:
                parti_mandater[parti] = 0

        return parti_mandater, dict(forbund_mandater)

    def print_resultat(
        self,
        stemmer: Dict[str, int],
        parti_mandater: Dict[str, int],
        forbund_mandater: Dict[str, int],
        total_mandater: int
    ):
        """
        Printer mandatfordelingsresultatet på en overskuelig måde.

        Args:
            stemmer: Dictionary med partibogstav -> antal stemmer
            parti_mandater: Dictionary med partibogstav -> antal mandater
            forbund_mandater: Dictionary med forbundsnavn -> antal mandater
            total_mandater: Total antal mandater
        """
        total_stemmer = sum(stemmer.values())

        print("\n" + "="*70)
        print(f"MANDATFORDELING - {total_mandater} mandater")
        print("="*70)

        # Vis per forbund
        for forbund_navn, forbund_partier in self.valgforbund.items():
            forbund_stemmer_total = sum(stemmer.get(p, 0) for p in forbund_partier)
            forbund_mandater_total = forbund_mandater.get(forbund_navn, 0)

            if forbund_stemmer_total == 0:
                continue

            forbund_pct = forbund_stemmer_total / total_stemmer * 100

            print(f"\n{forbund_navn}: {forbund_mandater_total} mandater "
                  f"({forbund_stemmer_total:,} stemmer, {forbund_pct:.2f}%)")
            print("-"*70)

            # Sorter partier i forbundet efter mandater
            forbund_partier_sorted = sorted(
                forbund_partier,
                key=lambda p: (parti_mandater.get(p, 0), stemmer.get(p, 0)),
                reverse=True
            )

            for parti in forbund_partier_sorted:
                parti_stemmer = stemmer.get(parti, 0)
                if parti_stemmer == 0:
                    continue

                parti_pct = parti_stemmer / total_stemmer * 100
                mandater = parti_mandater.get(parti, 0)

                print(f"  {parti}: {mandater:2d} mandater "
                      f"({parti_stemmer:7,} stemmer, {parti_pct:5.2f}%)")

        # Opsummering
        print("\n" + "="*70)
        print("OPSUMMERING")
        print("="*70)

        total_tildelt = sum(parti_mandater.values())
        print(f"Total mandater tildelt: {total_tildelt} af {total_mandater}")

        # Vis top 5 partier
        print("\nTop 5 partier efter mandater:")
        top_partier = sorted(
            parti_mandater.items(),
            key=lambda x: (x[1], stemmer.get(x[0], 0)),
            reverse=True
        )[:5]

        for parti, mandater in top_partier:
            if mandater > 0:
                pct = stemmer.get(parti, 0) / total_stemmer * 100
                print(f"  {parti}: {mandater} mandater ({pct:.2f}% af stemmerne)")


# Standard valgforbund for København
KØBENHAVN_VALGFORBUND = {
    "Rød blok 1 (A, B, M)": ["A", "B", "M"],
    "Blå blok (C, D, I, K, O, V, Æ)": ["C", "D", "I", "K", "O", "V", "Æ"],
    "Liste-alliancen (E, J, P, Q, R, T, Z)": ["E", "J", "P", "Q", "R", "T", "Z"],
    "Rød blok 2 (F, N, Ø, Å)": ["F", "N", "Ø", "Å"],
}


def test_mandatfordeling():
    """Test mandatfordeling med eksempeldata."""
    print("="*70)
    print("TEST: Mandatfordeling med D'Hondt")
    print("="*70)

    # Simpelt eksempel
    print("\nEksempel 1: Simpel fordeling (3 forbund, 10 mandater)")
    print("-"*70)

    simple_forbund = {
        "Forbund A": ["A", "B"],
        "Forbund B": ["C", "D"],
        "Forbund C": ["E"],
    }

    simple_stemmer = {
        "A": 10000,
        "B": 5000,
        "C": 8000,
        "D": 3000,
        "E": 4000,
    }

    mf = Mandatfordeling(simple_forbund)
    parti_m, forbund_m = mf.fordel_mandater(simple_stemmer, 10)
    mf.print_resultat(simple_stemmer, parti_m, forbund_m, 10)


if __name__ == "__main__":
    test_mandatfordeling()

    print("\n\n")
    print("="*70)
    print("For at bruge med rigtige valgdata:")
    print("="*70)
    print("""
from mandatfordeling import Mandatfordeling, KØBENHAVN_VALGFORBUND

# Brug prediкtionen fra valgmodellen
stemmer = {...}  # Dictionary med partibogstav -> stemmer

# Opret mandatfordeling med københavnske valgforbund
mf = Mandatfordeling(KØBENHAVN_VALGFORBUND)

# Fordel 55 mandater
parti_mandater, forbund_mandater = mf.fordel_mandater(stemmer, 55)

# Vis resultat
mf.print_resultat(stemmer, parti_mandater, forbund_mandater, 55)
    """)
