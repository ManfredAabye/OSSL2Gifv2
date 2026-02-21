from translations import translations

counts = {lang: len(trans) for lang, trans in translations.items()}
print('Anzahl Einträge pro Sprache:')
for lang, count in counts.items():
    print(f'{lang}: {count}')

all_same = len(set(counts.values())) == 1
print(f'\nAlle haben die gleiche Anzahl: {all_same}')
if all_same:
    print(f'Alle Sprachen: {counts["de"]} Einträge ✓')
