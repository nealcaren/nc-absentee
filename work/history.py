import zipfile, io, csv, collections, pickle
out={}
for yr,path in [(2022,'hs2022.zip'),(2024,'hs2024.zip')]:
    tot=collections.Counter(); bymethod=collections.defaultdict(lambda: collections.Counter())
    z=zipfile.ZipFile('/Users/nealcaren/Downloads/'+path)
    n=0
    with z.open(z.namelist()[0]) as fh:
        r=csv.DictReader(io.TextIOWrapper(fh,encoding='utf-8',errors='replace'),delimiter='\t')
        for row in r:
            v=int(row['total_voters'] or 0); p=row['party_cd'].strip(); m=row['voting_method'].strip()
            tot[p]+=v; bymethod[m][p]+=v; n+=v
    print(f"=== {yr}: total voters {n:,}")
    for p in ['DEM','REP','UNA','LIB','GRE']:
        print(f"   {p}: {tot[p]:>9,}  ({100*tot[p]/n:5.2f}%)")
    print("   by method:")
    for m in ['O','V','M','U','C','T','P']:
        s=sum(bymethod[m].values())
        if s: print(f"     {m}: {s:>9,}")
    out[yr]={'tot':dict(tot),'method':{k:dict(v) for k,v in bymethod.items()}}
pickle.dump(out,open('work/history.pkl','wb'))
