import zipfile, io, csv, collections
# history_stats precinct values
hs=collections.defaultdict(set)
z=zipfile.ZipFile('/Users/nealcaren/Downloads/hs2022.zip')
with z.open(z.namelist()[0]) as fh:
    for row in csv.DictReader(io.TextIOWrapper(fh,encoding='utf-8',errors='replace'),delimiter='\t'):
        hs[row['county_desc'].strip()].add(row['precinct_abbrv'].strip())
# results precinct values
res=collections.defaultdict(set)
with open('/Users/nealcaren/Downloads/results_pct_20221108.txt',encoding='utf-8',errors='replace') as f:
    for row in csv.DictReader(f,delimiter='\t'):
        res[row['County'].strip()].add(row['Precinct'].strip())
for c in ['WAKE','MECKLENBURG','BRUNSWICK','ALAMANCE','FORSYTH']:
    print(f"{c}:")
    print("   history:", sorted(hs[c])[:8])
    print("   results:", sorted(res[c])[:8])
    print("   exact overlap:", len(hs[c]&res[c]), "/", len(res[c]))
