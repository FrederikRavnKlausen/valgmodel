#!/usr/bin/env python3
"""
Script til at summere stemmer på hvert parti ved hvert afstemningssted.
"""

import csv
import sys
from collections import defaultdict


def sum_votes_by_party(csv_file):
    """
    Læser valgdata fra CSV fil og summerer stemmer på hvert parti ved hvert afstemningssted.

    Args:
        csv_file: Sti til CSV fil med valgdata

    Returns:
        Dictionary med summerede stemmer grupperet efter afstemningsområde og parti
    """
    # Dictionary til at holde summerede stemmer
    # Nøgle: (Afstemningsområde, Bogstavbetegnelse, Listenavn)
    # Værdi: Total antal stemmer
    votes_sum = defaultdict(int)

    # Læs CSV filen
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        row_count = 0

        for row in reader:
            row_count += 1
            afstemningsomraade = row['Afstemningsområde']
            bogstav = row['Bogstavbetegnelse']
            parti = row['Listenavn']
            stemmer = int(row['Stemmetal'])

            # Tilføj stemmerne til totalen for dette parti ved dette afstemningssted
            key = (afstemningsomraade, bogstav, parti)
            votes_sum[key] += stemmer

    print(f"Læste {row_count} rækker fra {csv_file}")

    return votes_sum


def format_results(votes_sum):
    """
    Formaterer resultatet til visning og gemning.

    Args:
        votes_sum: Dictionary med summerede stemmer

    Returns:
        Liste af tupler sorteret efter afstemningsområde og parti
    """
    # Konverter til liste og sorter
    results = []
    for (afstemningsomraade, bogstav, parti), stemmer in votes_sum.items():
        results.append((afstemningsomraade, bogstav, parti, stemmer))

    # Sorter efter afstemningsområde og derefter bogstav
    results.sort(key=lambda x: (x[0], x[1]))

    return results


def save_to_csv(results, output_file):
    """
    Gemmer resultatet til en CSV fil.

    Args:
        results: Liste af tupler med resultater
        output_file: Sti til output fil
    """
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Afstemningsområde', 'Parti (Bogstav)', 'Parti (Navn)', 'Total Stemmer'])

        for row in results:
            writer.writerow(row)


def calculate_total_by_party(results):
    """
    Beregner total stemmer per parti på tværs af alle afstemningssteder.

    Args:
        results: Liste af tupler med resultater

    Returns:
        Liste af tupler med totaler per parti, sorteret efter antal stemmer
    """
    party_totals = defaultdict(int)

    for afstemningsomraade, bogstav, parti, stemmer in results:
        key = (bogstav, parti)
        party_totals[key] += stemmer

    # Konverter til liste og sorter efter antal stemmer (faldende)
    totals = [(bogstav, parti, stemmer) for (bogstav, parti), stemmer in party_totals.items()]
    totals.sort(key=lambda x: x[2], reverse=True)

    return totals


def main():
    # Standard CSV fil hvis ikke andet specificeret
    csv_file = 'Kommunalvalg_2021_København_17-11-2025 20.11.26.csv'

    # Tillad at specificere en anden fil som argument
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]

    print(f"Analyserer valgdata fra: {csv_file}\n")
    print("=" * 80)

    # Summer stemmerne
    votes_sum = sum_votes_by_party(csv_file)

    # Formater resultatet
    results = format_results(votes_sum)

    # Vis resultatet
    print(f"\nSummerede stemmer på hvert parti ved hvert afstemningssted:")
    print("=" * 80)
    print(f"{'Afstemningsområde':<30} {'Bogstav':<8} {'Parti':<35} {'Stemmer':>10}")
    print("-" * 80)
    for afstemningsomraade, bogstav, parti, stemmer in results:
        print(f"{afstemningsomraade:<30} {bogstav:<8} {parti:<35} {stemmer:>10}")

    # Gem resultatet til en ny CSV fil
    output_file = csv_file.replace('.csv', '_summeret_efter_parti.csv')
    save_to_csv(results, output_file)
    print(f"\n\nResultatet er gemt i: {output_file}")

    # Vis også totaler per parti på tværs af alle afstemningssteder
    print("\n" + "=" * 80)
    print("Total stemmer per parti (på tværs af alle afstemningssteder):")
    print("=" * 80)
    totals = calculate_total_by_party(results)
    print(f"{'Bogstav':<8} {'Parti':<35} {'Total Stemmer':>15}")
    print("-" * 80)
    for bogstav, parti, stemmer in totals:
        print(f"{bogstav:<8} {parti:<35} {stemmer:>15}")


if __name__ == '__main__':
    main()
