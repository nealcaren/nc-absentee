import zipfile, io, csv, collections, pickle
EARLY={'O','EV','EC','U','C'}; MAIL={'M','A'}; ED={'V'}
out={}
for yr,path in [(2022,'hs2022.zip'),(2024,'hs2024.zip')]:
    d=collections.defaultdict(lambda: collections.Counter())
    z=zipfile.ZipFile('/Users/nealcaren/Downloads/'+path)
    with z.open(z.namelist()[0]) as fh:
        for row in csv.DictReader(io.TextIOWrapper(fh,encoding='utf-8',errors='replace'),delimiter='\t'):
            v=int(row['total_voters'] or 0)
            if not v: continue
            c=row['county_desc'].strip(); p=row['precinct_abbrv'].strip(); party=row['party_cd'].strip(); m=row['voting_method'].strip()
            k=f'{party}|{"E" if m in EARLY else "M" if m in MAIL else "V" if m in ED else "X"}'
            d[(c,p)][k]+=v
    print(yr,len(d),"precincts",sum(sum(v.values()) for v in d.values()),"voters",flush=True)
    out[yr]={k:dict(v) for k,v in d.items()}
pickle.dump(out,open('work/hist_prec.pkl','wb'))
