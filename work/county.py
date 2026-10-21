import pickle, statistics
d=pickle.load(open('work/agg.pkl','rb'))

def n(yr,cty): return d[yr]['county'].get(cty,0)
def s(yr,cty): return sum(1 for k,v in d[yr]['site'].items() if k[0]==cty and v['win']>0)

counties=sorted({c for yr in (2022,2024,2026) for c in d[yr]['county']})
rows=[]
for c in counties:
    a,b,cc=n(2022,c),n(2024,c),n(2026,c)
    sa,sb,sc=s(2022,c),s(2024,c),s(2026,c)
    if a<500: continue
    rows.append((c,a,cc,100*(cc-a)/a if a else 0,sa,sc,sc-sa, cc/sc if sc else 0, a/sa if sa else 0))

rows.sort(key=lambda r:r[3])
print(f"{'county':20}{'22votes':>9}{'26votes':>9}{'%chg':>8}{'s22':>5}{'s26':>5}{'dsite':>6}{'v/site26':>10}{'v/site22':>10}")
for r in rows[:15]:
    print(f"{r[0]:20}{r[1]:>9,}{r[2]:>9,}{r[3]:>+8.0f}{r[4]:>5}{r[5]:>5}{r[6]:>+6}{r[7]:>10,.0f}{r[8]:>10,.0f}")
print("   ...")
for r in rows[-10:]:
    print(f"{r[0]:20}{r[1]:>9,}{r[2]:>9,}{r[3]:>+8.0f}{r[4]:>5}{r[5]:>5}{r[6]:>+6}{r[7]:>10,.0f}{r[8]:>10,.0f}")

# correlation between site change and turnout change
import math
ds=[r[6] for r in rows]; pc=[r[3] for r in rows]
ma,mb=statistics.mean(ds),statistics.mean(pc)
cov=sum((x-ma)*(y-mb) for x,y in zip(ds,pc))
r=cov/math.sqrt(sum((x-ma)**2 for x in ds)*sum((y-mb)**2 for y in pc))
print(f"\ncounties analyzed: {len(rows)}")
print(f"corr(site change 22->26, % turnout change 22->26) = {r:+.3f}")

# split by site change
down=[x for x in rows if x[6]<0]; same=[x for x in rows if x[6]==0]; up=[x for x in rows if x[6]>0]
for lbl,g in [('lost sites',down),('unchanged',same),('gained sites',up)]:
    print(f"  {lbl:14} n={len(g):3}  median % turnout chg = {statistics.median([x[3] for x in g]):+.1f}")

tot22=sum(n(2022,c) for c in counties); tot26=sum(n(2026,c) for c in counties)
print(f"\nstatewide window votes 2022={tot22:,} 2026={tot26:,} ({100*(tot26-tot22)/tot22:+.1f}%)")
print(f"statewide sites 2022={sum(s(2022,c) for c in counties)} 2026={sum(s(2026,c) for c in counties)}")
