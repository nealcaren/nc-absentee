import zipfile, io, csv, collections, pickle
EARLY={'O','EV','EC','U','C'}   # 1stop / early vote / curbside variants
MAIL={'M','A'}
ED={'V'}
out={}
for yr,path in [(2022,'hs2022.zip'),(2024,'hs2024.zip')]:
    tot=collections.Counter(); early=collections.Counter(); ed=collections.Counter(); mail=collections.Counter()
    z=zipfile.ZipFile('/Users/nealcaren/Downloads/'+path)
    with z.open(z.namelist()[0]) as fh:
        for row in csv.DictReader(io.TextIOWrapper(fh,encoding='utf-8',errors='replace'),delimiter='\t'):
            v=int(row['total_voters'] or 0); p=row['party_cd'].strip(); m=row['voting_method'].strip()
            tot[p]+=v
            if m in EARLY: early[p]+=v
            elif m in MAIL: mail[p]+=v
            elif m in ED: ed[p]+=v
    print(f"=== {yr} total {sum(tot.values()):,}")
    print(f"{'party':6}{'total':>10}{'early':>10}{'mail':>10}{'ED':>10}{'early%':>8}")
    for p in ['DEM','REP','UNA']:
        print(f"{p:6}{tot[p]:>10,}{early[p]:>10,}{mail[p]:>10,}{ed[p]:>10,}{100*early[p]/tot[p]:>8.1f}")
    out[yr]={'tot':dict(tot),'early':dict(early),'ed':dict(ed),'mail':dict(mail)}
pickle.dump(out,open('work/history2.pkl','wb'))
