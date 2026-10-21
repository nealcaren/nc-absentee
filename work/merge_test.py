import csv, collections, zipfile, io, datetime, re

# precincts in results for US SENATE (exclude pseudo-precincts)
res=collections.defaultdict(set); rescount=collections.Counter()
with open('/Users/nealcaren/Downloads/results_pct_20221108.txt', encoding='utf-8', errors='replace') as f:
    r=csv.DictReader(f, delimiter='\t')
    for row in r:
        if row['Contest Name'].strip()!='US SENATE': continue
        cty=row['County'].strip(); p=row['Precinct'].strip()
        if 'ABSENT' in p.upper(): continue
        res[cty].add(p); rescount[cty]+=int(row['Total Votes'] or 0)

# precincts in absentee file
absn=collections.defaultdict(set)
z=zipfile.ZipFile('absentee_20221108.zip')
with z.open(z.namelist()[0]) as fh:
    for row in csv.DictReader(io.TextIOWrapper(fh,encoding='utf-8',errors='replace')):
        absn[row['county_desc'].strip()].add(row['precinct_desc'].strip())

def norm(s):
    return re.sub(r'[^A-Z0-9]','',s.upper())

tot_r=tot_a=tot_m=0; worst=[]
for cty in sorted(res):
    R=res[cty]; A=absn.get(cty,set())
    rn={norm(x) for x in R}; an={norm(x) for x in A}
    m=len(rn&an)
    tot_r+=len(rn); tot_a+=len(an); tot_m+=m
    worst.append((m/len(rn) if rn else 0, cty, len(rn), len(an), m))

print(f"statewide normalised precinct match: {tot_m}/{tot_r} results precincts ({100*tot_m/tot_r:.1f}%)")
print("\nbest counties:")
for w in sorted(worst,reverse=True)[:6]:
    print(f"  {w[1]:15} results={w[2]:4} absentee={w[3]:4} matched={w[4]:4} ({100*w[0]:.0f}%)")
print("\nworst counties:")
for w in sorted(worst)[:8]:
    print(f"  {w[1]:15} results={w[2]:4} absentee={w[3]:4} matched={w[4]:4} ({100*w[0]:.0f}%)")
