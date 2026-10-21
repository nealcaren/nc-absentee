import pickle, collections, statistics, math
reg={y:pickle.load(open(f'work/reg{y}.pkl','rb')) for y in (2022,2024,2026)}
A=pickle.load(open('work/abs_full.pkl','rb'))
S=pickle.load(open('work/agg2.pkl','rb'))
sites26=collections.defaultdict(set)
for (c,sn) in S[2026]['site']: sites26[c].add(sn)

rows=[]
for (c,p),v in A[2022]['ps'].items():
    n22=sum(v.values())
    if n22<100: continue
    modal=max(v.items(),key=lambda x:x[1])[0]
    v26=A[2026]['ps'].get((c,p))
    if not v26: continue
    r22=reg[2022]['prec'].get((c,p),{}); r26=reg[2026]['prec'].get((c,p),{})
    d22=sum(r22.values()); d26=sum(r26.values())
    if d22<100 or d26<100: continue
    rows.append(dict(c=c,p=p,treat=1 if modal not in sites26.get(c,set()) else 0,
        t22=100*n22/d22, t26=100*sum(v26.values())/d26,
        bsh22=r22.get('B',0)/d22, bsh26=r26.get('B',0)/d26,
        bn22=A[2022]['prec'].get((c,p),{}).get('B',0), bn26=v26.get('B',0),
        bd22=r22.get('B',0), bd26=r26.get('B',0)))
print("precincts:",len(rows))

# 1. TARGETING: did Black precincts lose sites more?
print("\n1. Share of precincts losing their 2022 site, by 2022 Black share of registered voters")
s=sorted(rows,key=lambda r:r['bsh22']); q=len(s)//4
for i in range(4):
    g=s[i*q:(i+1)*q] if i<3 else s[3*q:]
    print(f"   Q{i+1} Black share {100*g[0]['bsh22']:5.1f}-{100*g[-1]['bsh22']:5.1f}%  n={len(g):3}  "
          f"lost site: {100*sum(x['treat'] for x in g)/len(g):.1f}%")

# 2. Black turnout change by treatment
print("\n2. Black early turnout rate (precincts with >=100 Black registrants)")
bk=[r for r in rows if r['bd22']>=100 and r['bd26']>=100]
for lbl,sel in [('lost site',lambda r:r['treat']==1),('retained',lambda r:r['treat']==0)]:
    g=[r for r in bk if sel(r)]
    c22=statistics.median([100*r['bn22']/r['bd22'] for r in g])
    c26=statistics.median([100*r['bn26']/r['bd26'] for r in g])
    print(f"   {lbl:10} n={len(g):4}  median 2022={c22:5.2f}%  2026={c26:5.2f}%  change={c26-c22:+5.2f}pp")

# 3. FE regression: within-county
def within(rows,key):
    by=collections.defaultdict(list)
    for r in rows: by[r['c']].append(r)
    out=[]
    for c,g in by.items():
        m=statistics.mean(r[key] for r in g)
        for r in g: out.append(r[key]-m)
    return out
d=[dict(r,dy=r['t26']-r['t22']) for r in rows]
y=within(d,'dy'); x1=within(d,'treat'); x2=within(d,'t22')
def ols(X,y):
    k=len(X[0]); A=[[0.0]*(k+1) for _ in range(k)]
    for xi,yi in zip(X,y):
        for i in range(k):
            for j in range(k): A[i][j]+=xi[i]*xi[j]
            A[i][k]+=xi[i]*yi
    for i in range(k):
        p=max(range(i,k),key=lambda r:abs(A[r][i])); A[i],A[p]=A[p],A[i]
        dd=A[i][i]
        for j in range(i,k+1): A[i][j]/=dd
        for r_ in range(k):
            if r_!=i and A[r_][i]:
                f=A[r_][i]
                for j in range(i,k+1): A[r_][j]-=f*A[i][j]
    return [A[i][k] for i in range(k)]
b=ols([[1.0,x1[i],x2[i]] for i in range(len(d))],y)
print(f"\n3. Within-county FE regression of turnout change on site loss")
print(f"   site lost coefficient = {b[1]:+.3f} pp  (baseline turnout control)")
