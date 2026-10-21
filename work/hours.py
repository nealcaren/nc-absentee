import pickle, csv, collections, math, sys
sys.path.insert(0,'work')
from parse_sites import parse

YRS={2022:'ev22.txt',2024:'ev24.txt',2026:'ev26.txt'}
hours=collections.defaultdict(dict); sites=collections.defaultdict(dict)
for y,f in YRS.items():
    for s in parse('/Users/nealcaren/Downloads/'+f):
        hours[s['county']][y]=hours[s['county']].get(y,0)+s['hours']
        sites[s['county']][y]=sites[s['county']].get(y,0)+1

reg={y:pickle.load(open(f'work/reg{y}.pkl','rb')) for y in (2022,2024,2026)}
A=pickle.load(open('work/abs_full.pkl','rb'))

def early_by_race(y):
    out=collections.defaultdict(collections.Counter)
    for (c,p),v in A[y]['prec'].items():
        for k,n in v.items(): out[c][k]+=n
    return out
E={y:early_by_race(y) for y in (2022,2024,2026)}

def total(d): return sum(d.values())

rows=[]
for c in sorted(hours):
    r22=total(reg[2022]['cty'].get(c,{})); r26=total(reg[2026]['cty'].get(c,{}))
    if not r22 or not r26: continue
    h22,h26=hours[c].get(2022,0),hours[c].get(2026,0)
    rec=dict(county=c,sites22=sites[c].get(2022,0),sites26=sites[c].get(2026,0),
             hours22=h22,hours26=h26,
             hours_per_1k_22=1000*h22/r22, hours_per_1k_26=1000*h26/r26,
             pct_hours=100*(h26-h22)/h22 if h22 else None)
    for race in ('W','B'):
        rec[f'rate_{race}22']=100*E[2022][c].get(race,0)/reg[2022]['cty'][c].get(race,1)
        rec[f'rate_{race}26']=100*E[2026][c].get(race,0)/reg[2026]['cty'][c].get(race,1)
        rec[f'd_{race}']=rec[f'rate_{race}26']-rec[f'rate_{race}22']
    rec['d_hours_p1k']=rec['hours_per_1k_26']-rec['hours_per_1k_22']
    rows.append(rec)

with open('analysis/county_site_hours.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader()
    for r in rows: w.writerow({k:(round(v,3) if isinstance(v,float) else v) for k,v in r.items()})
print("wrote analysis/county_site_hours.csv",len(rows),"counties")

def corr(xs,ys):
    n=len(xs); mx=sum(xs)/n; my=sum(ys)/n
    sx=math.sqrt(sum((x-mx)**2 for x in xs)); sy=math.sqrt(sum((y-my)**2 for y in ys))
    return sum((x-mx)*(y-my) for x,y in zip(xs,ys))/(sx*sy)
def slope(xs,ys):
    n=len(xs); mx=sum(xs)/n; my=sum(ys)/n
    return sum((x-mx)*(y-my) for x,y in zip(xs,ys))/sum((x-mx)**2 for x in xs)

print(f"\nStatewide site-hours: 2022 {sum(hours[c].get(2022,0) for c in hours):,.0f}  "
      f"2024 {sum(hours[c].get(2024,0) for c in hours):,.0f}  "
      f"2026 {sum(hours[c].get(2026,0) for c in hours):,.0f}")
print(f"Statewide sites:      2022 {sum(sites[c].get(2022,0) for c in sites):,}      "
      f"2024 {sum(sites[c].get(2024,0) for c in sites):,}      "
      f"2026 {sum(sites[c].get(2026,0) for c in sites):,}")

for lbl,key in [('White turnout rate','d_W'),('Black turnout rate','d_B')]:
    xs=[r['d_hours_p1k'] for r in rows]; ys=[r[key] for r in rows]
    print(f"\n{lbl} change vs site-hours change (per 1k registrants), n={len(rows)}")
    print(f"   correlation {corr(xs,ys):+.3f}   slope {slope(xs,ys):+.4f} pp per hour-per-1000")
    # terciles of hours change
    srt=sorted(rows,key=lambda r:r['d_hours_p1k'])
    t=len(srt)//3
    for name,grp in [('cut most',srt[:t]),('middle',srt[t:2*t]),('cut least/added',srt[2*t:])]:
        print(f"   {name:16} n={len(grp):3}  dHours {sum(g['d_hours_p1k'] for g in grp)/len(grp):+6.1f}  "
              f"dWhite {sum(g['d_W'] for g in grp)/len(grp):+5.2f}  dBlack {sum(g['d_B'] for g in grp)/len(grp):+5.2f}")
