"""
Valgmodel til live prediktion på valgnatten.

Modellen fungerer ved at:
1. Summere optalte stemmer på de valgsteder der er optalt (nuværende valg)
2. Summere samme valgsteder fra forrige valg
3. Beregne swing for hvert parti som forholdet mellem nuværende og forrige procent
4. Applicere dette swing på det samlede resultat fra forrige valg
5. Normalisere resultatet
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple


class Valgmodel:
    """
    Live valgmodel der prediктerer det endelige resultat baseret på
    delvist optalte valgsteder.
    """

    def __init__(self, forrige_valg_csv: str):
        """
        Initialiserer modellen med data fra forrige valg.

        Args:
            forrige_valg_csv: Sti til CSV-fil med data fra forrige valg
        """
        self.forrige_valg_data = self._load_data(forrige_valg_csv)
        self.forrige_valg_samlet = self._beregn_samlet_resultat(self.forrige_valg_data)

    def _load_data(self, csv_fil: str) -> pd.DataFrame:
        """
        Indlæser valgdata fra CSV.

        Args:
            csv_fil: Sti til CSV-fil

        Returns:
            DataFrame med valgdata
        """
        df = pd.read_csv(
            csv_fil,
            sep=';',
            encoding='utf-8-sig'  # Håndterer BOM i filen
        )

        # Aggreger stemmer per valgsted og parti
        result = df.groupby(['Afstemningsområde', 'Bogstavbetegnelse', 'Listenavn'])['Stemmetal'].sum().reset_index()
        result.columns = ['Valgsted', 'Parti_bogstav', 'Parti_navn', 'Stemmer']

        return result

    def _beregn_samlet_resultat(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Beregner det samlede resultat (procenter) for alle partier.

        Args:
            data: DataFrame med valgdata

        Returns:
            Dictionary med parti_bogstav -> procent
        """
        total_stemmer = data.groupby('Parti_bogstav')['Stemmer'].sum()
        total = total_stemmer.sum()
        procent = (total_stemmer / total * 100).to_dict()

        return procent

    def _beregn_resultat_for_valgsteder(
        self,
        data: pd.DataFrame,
        valgsteder: List[str]
    ) -> Dict[str, float]:
        """
        Beregner resultat (procenter) for specifikke valgsteder.

        Args:
            data: DataFrame med valgdata
            valgsteder: Liste af valgsteder at inkludere

        Returns:
            Dictionary med parti_bogstav -> procent
        """
        filtreret_data = data[data['Valgsted'].isin(valgsteder)]

        if len(filtreret_data) == 0:
            raise ValueError(f"Ingen data fundet for valgstederne: {valgsteder}")

        total_stemmer = filtreret_data.groupby('Parti_bogstav')['Stemmer'].sum()
        total = total_stemmer.sum()
        procent = (total_stemmer / total * 100).to_dict()

        return procent

    def prediкer(
        self,
        nuværende_valg_data: pd.DataFrame,
        optalte_valgsteder: List[str]
    ) -> Dict[str, float]:
        """
        Prediкerer det endelige resultat baseret på delvist optalte valgsteder.

        Metode:
        1. Beregn p_i: procenter for optalte valgsteder (nuværende valg)
        2. Beregn q_i: procenter for samme valgsteder (forrige valg)
        3. Beregn swing: s_i = p_i / q_i
        4. Prediкer: r_i * s_i hvor r_i er samlet resultat fra forrige valg
        5. Normaliser så sum = 100%

        Args:
            nuværende_valg_data: DataFrame med data fra nuværende valg
            optalte_valgsteder: Liste af valgsteder der er optalt

        Returns:
            Dictionary med parti_bogstav -> prediкeret procent
        """
        # p_i: procenter for optalte valgsteder (nuværende valg)
        p = self._beregn_resultat_for_valgsteder(nuværende_valg_data, optalte_valgsteder)

        # q_i: procenter for samme valgsteder (forrige valg)
        q = self._beregn_resultat_for_valgsteder(self.forrige_valg_data, optalte_valgsteder)

        # r_i: samlet resultat fra forrige valg
        r = self.forrige_valg_samlet

        # Beregn prediкtion: r_i * (p_i / q_i)
        prediкtion = {}
        for parti in r.keys():
            if parti in q and q[parti] > 0:
                # Hvis partiet findes i både p og q
                if parti in p:
                    swing = p[parti] / q[parti]
                else:
                    # Partiet havde stemmer i forrige valg på disse valgsteder,
                    # men ikke i nuværende -> swing = 0
                    swing = 0
                prediкtion[parti] = r[parti] * swing
            else:
                # Partiet havde ingen stemmer på disse valgsteder i forrige valg
                if parti in p:
                    # Men har stemmer nu - brug p[parti] som estimat
                    prediкtion[parti] = p[parti]
                else:
                    # Partiet findes hverken i p eller q for disse valgsteder
                    # Brug r[parti] som fallback
                    prediкtion[parti] = r[parti]

        # Håndter nye partier der ikke var med sidste gang
        for parti in p.keys():
            if parti not in prediкtion:
                prediкtion[parti] = p[parti]

        # Normaliser så sum = 100%
        total = sum(prediкtion.values())
        if total > 0:
            prediкtion = {k: (v / total * 100) for k, v in prediкtion.items()}

        return prediкtion

    def prediкer_fra_csv(
        self,
        nuværende_valg_csv: str,
        optalte_valgsteder: List[str]
    ) -> Dict[str, float]:
        """
        Wrapper funкtion der indlæser nuværende valgdata fra CSV.

        Args:
            nuværende_valg_csv: Sti til CSV med nuværende valgdata
            optalte_valgsteder: Liste af valgsteder der er optalt

        Returns:
            Dictionary med parti_bogstav -> prediкeret procent
        """
        nuværende_data = self._load_data(nuværende_valg_csv)
        return self.prediкer(nuværende_data, optalte_valgsteder)

    def print_resultat(self, resultat: Dict[str, float], titel: str = "Resultat"):
        """
        Printer resultat i en pæn formatering.

        Args:
            resultat: Dictionary med parti -> procent
            titel: Titel til output
        """
        print(f"\n{titel}")
        print("=" * 60)

        # Sorter efter procent (højest først)
        sorteret = sorted(resultat.items(), key=lambda x: x[1], reverse=True)

        for parti, procent in sorteret:
            print(f"{parti:3s}: {procent:6.2f}%")

        print("=" * 60)
        print(f"Total: {sum(resultat.values()):.2f}%\n")


if __name__ == "__main__":
    print("="*70)
    print("VALGMODEL - Grundlæggende eksempel")
    print("="*70)
    print("""
VIGTIG BEMÆRKNING:
Dette eksempel bruger 2021-data både som "nuværende" og "forrige" valg.
Det betyder at swing = 1.0 for alle partier, og prediктionen bliver
identisk med 2021-resultatet.

På den rigtige valgnat vil "nuværende" data være forskellig fra "forrige",
og modellen vil give meningsfulde prediктioner.

Se test_realistic.py for eksempler med reelle forskelle!
    """)

    # Initialiser modellen med data fra 2021
    model = Valgmodel("Kommunalvalg_2021_København_17-11-2025 20.11.26.csv")

    # Vis det faktiske resultat fra 2021
    model.print_resultat(model.forrige_valg_samlet, "Faktisk resultat 2021")

    # Test med nogle få valgsteder
    print("\nTester modellen med 4 valgsteder...")
    print("(Bruger samme 2021-data → swing = 1.0 → prediкtion = 2021-resultat)")

    eksempel_valgsteder = [
        "12. 3. Nord",
        "17. 4. Nord",
        "13. 3. Syd",
        "18. 4. Syd"
    ]

    # Brug samme data (derfor vil resultat være identisk)
    prediкtion = model.prediкer_fra_csv(
        "Kommunalvalg_2021_København_17-11-2025 20.11.26.csv",
        eksempel_valgsteder
    )

    model.print_resultat(prediкtion, "Prediкtion (4 valgsteder)")

    print("\nSom forventet: Prediкtion = 2021-resultat (fordi data er identiske)")
    print("\nFor at se modellen i aкtion med reelle forskelle, kør:")
    print("  python test_realistic.py")
