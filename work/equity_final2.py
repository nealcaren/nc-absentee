import pickle, collections, statistics
reg={y:pickle.load(open(f'work/reg{y}.pkl','rb')) for y in (2022,2024,2026)}
A=pickle.load(open('work/abs_full.pkl','rb'))
S=pickle.load(open('work/agg2.pkl','rb'))
sites26=collections.defaultdict(set)
for (c,sn) in S[2026]['site']: sites26[c].add(sn)
lost_counties={c for c in {k[0] for k in S[2022]['site']} if len([1 for k in S[2026]['site'] if k[0]==c])<len([1 for k in S[2022]['site'] if k[0]==c])}

rows=[]
for (c,p),v in A[2022]['ps'].items():
    if sum(v.values())<100: continue
    modal=max(v.items(),key=lambda x:x[1])[0]
    v26=A[2026]['ps'].get((c,p))
    if not v26: continue
    r22=reg[2022]['prec'].get((c,p),{}); r26=reg[2026]['prec'].get((c,p),{})
    if sum(r22.values())<100 or sum(r26.values())<100: continue
    rows.append(dict(c=c,p=p,treat=1 if modal not in sites26.get(c,set()) else 0,
        bsh22=r22.get('B',0)/sum(r22.values()),
        bn22=A[2022]['prec'].get((c,p),{}).get('B',0), bn26=v26.get('B',0),
        bd22=r22.get('B',0), bd26=r26.get('B',0)))

print("2. POOLED Black early turnout rate by treatment")
for lbl,sel in [('lost site',lambda r:r['treat']==1),('retained',lambda r:r['treat']==0)]:
    g=[r for r in rows if sel(r)]
    n22=sum(r['bn22'] for r in g); d22=sum(r['bd22'] for r in g)
    n26=sum(r['bn26'] for r in g); d26=sum(r['bd26'] for r in g)
    print(f"   {lbl:10} n={len(g):4}  2022={100*n22/d22:5.2f}%  2026={100*n26/d26:5.2f}%  change={100*n26/d26-100*n22/d22:+5.2f}pp")

print("\n1b. Targeting, WITHIN counties that lost at least one site")
sub=[r for r in rows if r['c'] in lost_counties]
print(f"   ({len(sub)} precincts in {len(lost_counties)} counties)")
s=sorted(sub,key=lambda r:r['bsh22']); q=max(1,len(s)//4)
for i in range(4):
    g=s[i*q:(i+1)*q] if i<3 else s[3*q:]
    print(f"   Q{i+1} Black share {100*g[0]['bsh22']:5.1f}-{100*g[-1]['bsh22']:5.1f}%  n={len(g):3}  lost: {100*sum(x['treat'] for x in g)/len(g):.1f}%")

# within-county demeaned targeting
by=collections.defaultdict(list)
for r in sub: by[r['c']].append(r)
hi=lo=0
for c,g in by.items():
    if len(g)<5: continue
    for r in g:
        m=statistics.mean(x['bsh22'] for x in g)
        if r['bsh22']>m and r['treat']: hi+=1
        elif r['bsh22']>m: pass
        if r['bsh22']<=m and r['treat']: lo+=1
print(f"\n   above-county-median Black share: lost site {hi}   at/below: {lo}")
