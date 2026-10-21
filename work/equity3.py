import pickle, collections, statistics
reg={y:pickle.load(open(f'work/reg{y}.pkl','rb')) for y in (2022,2024,2026)}
A=pickle.load(open('work/abs_full.pkl','rb'))
S=pickle.load(open('work/agg2.pkl','rb'))
sites26=collections.defaultdict(set)
for (c,sn) in S[2026]['site']: sites26[c].add(sn)

rows=[]
for (c,p),v in A[2022]['ps'].items():
    if sum(v.values())<100: continue
    modal=max(v.items(),key=lambda x:x[1])[0]
    if (c,p) not in A[2026]['ps']: continue
    r22=reg[2022]['prec'].get((c,p),{}); r26=reg[2026]['prec'].get((c,p),{})
    if sum(r22.values())<100 or sum(r26.values())<100: continue
    a22=A[2022]['prec'].get((c,p),{}); a26=A[2026]['prec'].get((c,p),{})
    rows.append(dict(c=c,p=p,treat=1 if modal not in sites26.get(c,set()) else 0,
        bsh22=r22.get('B',0)/sum(r22.values()),
        bn22=a22.get('B',0),bn26=a26.get('B',0),
        bd22=r22.get('B',0),bd26=r26.get('B',0),
        wn22=a22.get('W',0),wn26=a26.get('W',0),wd22=r22.get('W',0),wd26=r26.get('W',0)))

print("POOLED early turnout rate by race and site status")
for race,(n22k,n26k,d22k,d26k) in {'Black':('bn22','bn26','bd22','bd26'),'White':('wn22','wn26','wd22','wd26')}.items():
    print(f"  {race}:")
    for lbl,sel in [('lost site',lambda r:r['treat']==1),('retained',lambda r:r['treat']==0)]:
        g=[r for r in rows if sel(r)]
        a=100*sum(r[n22k] for r in g)/sum(r[d22k] for r in g)
        b=100*sum(r[n26k] for r in g)/sum(r[d26k] for r in g)
        print(f"     {lbl:10} n={len(g):4}  2022={a:5.2f}%  2026={b:5.2f}%  change={b-a:+5.2f}pp")

print("\nWITHIN-COUNTY targeting (counties that lost >=1 site)")
by=collections.defaultdict(list)
for r in rows: by[r['c']].append(r)
hi_lost=hi_tot=lo_lost=lo_tot=0
for c,g in by.items():
    if len(g)<8: continue
    m=statistics.median(x['bsh22'] for x in g)
    for r in g:
        if r['bsh22']>m: hi_tot+=1; hi_lost+=r['treat']
        elif r['bsh22']<m: lo_tot+=1; lo_lost+=r['treat']
print(f"  above county median Black share: {100*hi_lost/hi_tot:.1f}% lost site (n={hi_tot})")
print(f"  below county median Black share: {100*lo_lost/lo_tot:.1f}% lost site (n={lo_tot})")
