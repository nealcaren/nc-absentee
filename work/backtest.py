import csv, collections, zipfile, io, datetime, pickle

def final_shares(path, contest, ecol):
    c=collections.Counter()
    with open(path,encoding='utf-8',errors='replace') as f:
        for row in csv.DictReader(f,delimiter='\t'):
            if row['Contest Name'].strip()!=contest: continue
            if 'ABSENT' in row['Precinct'].upper(): continue
            c[row['Choice'].strip()]+=int(row['Total Votes'] or 0)
    tot=sum(c.values())
    top=c.most_common(6)
    return c, tot, top

print("=== 2022 US SENATE (final) ===")
c,t,top=final_shares('/Users/nealcaren/Downloads/results_pct_20221108.txt','US SENATE',None)
for k,v in top: print(f"   {k:28}{v:>9,}  {100*v/t:5.2f}%")
budd=c['Ted Budd']; beas=c['Cheri Beasley']
print(f"   two-party: Budd {100*budd/(budd+beas):.2f}  Beasley {100*beas/(budd+beas):.2f}")
d22=100*(beas-budd)/(budd+beas)

print("\n=== 2024 US PRESIDENT (final) ===")
z=zipfile.ZipFile('/Users/nealcaren/Downloads/results_pct_20241105.zip')
name=z.namelist()[0]
c=collections.Counter()
with z.open(name) as fh:
    for row in csv.DictReader(io.TextIOWrapper(fh,encoding='utf-8',errors='replace'),delimiter='\t'):
        if row['Contest Name'].strip()!='US PRESIDENT': continue
        if 'ABSENT' in row['Precinct'].upper(): continue
        c[row['Choice'].strip()]+=int(row['Total Votes'] or 0)
tot=sum(c.values())
for k,v in c.most_common(4): print(f"   {k:28}{v:>9,}  {100*v/tot:5.2f}%")
trump=c.get('Donald J. Trump',0); harris=c.get('Kamala D. Harris',0)
print(f"   two-party: Trump {100*trump/(trump+harris):.2f}  Harris {100*harris/(trump+harris):.2f}")
d24=100*(harris-trump)/(trump+harris)

print(f"\nFinal two-party Democratic margin: 2022 {d22:+.2f}   2024 {d24:+.2f}")
pickle.dump({'d22':d22,'d24':d24,'tot22':budd+beas,'tot24':trump+harris},open('work/final_margins.pkl','wb'))
