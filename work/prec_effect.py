import pickle, collections, statistics, math
reg={y:pickle.load(open(f'work/reg{y}.pkl','rb')) for y in (2022,2024,2026)}
A=pickle.load(open('work/abs_full.pkl','rb'))
S=pickle.load(open('work/agg2.pkl','rb'))
sites26=collections.defaultdict(set)
for (c,sn) in S[2026]['site']: sites26[c].add(sn)
sites22=collections.defaultdict(set)
for (c,sn) in S[2022]['site']: sites22[c].add(sn)

rows=[]
for (c,p),v in A[2022]['ps'].items():
    n22=sum(v.values())
    if n22<100: continue
    modal=max(v.items(),key=lambda x:x[1])[0]
    if modal not in sites26.get(c,set()):
        treat=1
    else: treat=0
    # 2026 modal site
    v26=A[2026]['ps'].get((c,p))
    if not v26: continue
    modal26=max(v26.items(),key=lambda x:x[1])[0]
    switched=1 if modal26!=modal else 0
    den_all=sum(reg[2022]['prec'].get((c,p),{}).values())
    den26=sum(reg[2026]['prec'].get((c,p),{}).values())
    if den_all<100 or den26<100: continue
    t22=100*n22/den_all; t26=100*sum(v26.values())/den26
    rows.append(dict(c=c,p=p,modal=modal,treat=treat,switched=switched,t22=t22,t26=t26,tot22=n22))

print(f"precincts analyzed: {len(rows)}")
print(f"  lost their 2022 modal site: {sum(r['treat'] for r in rows)} ({100*sum(r['treat'] for r in rows)/len(rows):.1f}%)")
print(f"  switched modal site: {sum(r['switched'] for r in rows)} ({100*sum(r['switched'] for r in rows)/len(rows):.1f}%)")

print("\nPrecinct early turnout rate (all voters), 2022 -> 2026")
for lbl,sel in [('lost site',lambda r:r['treat']==1),('retained site',lambda r:r['treat']==0)]:
    g=[r for r in rows if sel(r)]
    print(f"  {lbl:14} n={len(g):4}  median 2022={statistics.median([r['t22'] for r in g]):5.2f}%  "
          f"2026={statistics.median([r['t26'] for r in g]):5.2f}%  change={statistics.median([r['t26']-r['t22'] for r in g]):+5.2f}pp")

print("\nPrecinct early turnout rate change, by quartile of 2022 turnout")
g=sorted(rows,key=lambda r:r['t22']); q=len(g)//4
for i in range(4):
    s=g[i*q:(i+1)*q] if i<3 else g[3*q:]
    tr=[x for x in s if x['treat']==1]; un=[x for x in s if x['treat']==0]
    print(f"  Q{i+1} (2022 ~{s[0]['t22']:.1f}%): lost n={len(tr):3} chg={statistics.median([x['t26']-x['t22'] for x in tr]):+5.2f}  "
          f"retained n={len(un):3} chg={statistics.median([x['t26']-x['t22'] for x in un]):+5.2f}")
