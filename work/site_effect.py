import pickle, collections, statistics, math
reg={y:pickle.load(open(f'work/reg{y}.pkl','rb')) for y in (2022,2024,2026)}
A=pickle.load(open('work/abs_full.pkl','rb'))
S=pickle.load(open('work/agg2.pkl','rb'))   # site lists

def ns(y,c): return sum(1 for k in S[y]['site'] if k[0]==c)
def rr(y,c,rc):
    num=A[y]['prec']
    n=sum(v.get(rc,0) for (cc,p),v in num.items() if cc==c)
    den=sum(v.get(rc,0) for (cc,p),v in reg[y]['prec'].items() if cc==c)
    return (100*n/den if den else 0), n, den

rows=[]
for c in sorted(reg[2022]['cty']):
    if c not in reg[2026]['cty']: continue
    b22,_,db22=rr(2022,c,'B'); b26,_,db26=rr(2026,c,'B')
    w22,_,dw22=rr(2022,c,'W'); w26,_,dw26=rr(2026,c,'W')
    if db22<1000 or db26<1000: continue
    rows.append(dict(c=c,ds=ns(2026,c)-ns(2022,c),b22=b22,b26=b26,db=b26-b22,w22=w22,w26=w26,dw=w26-w22))
print("counties:",len(rows))

print("\nBlack early-turnout rate (%), by site change 2022->2026")
for lbl,sel in [('lost sites',lambda r:r['ds']<0),('unchanged',lambda r:r['ds']==0),('gained',lambda r:r['ds']>0)]:
    g=[r for r in rows if sel(r)]
    print(f"  {lbl:11} n={len(g):3}  2022={statistics.median([r['b22'] for r in g]):5.2f}  "
          f"2026={statistics.median([r['b26'] for r in g]):5.2f}  change={statistics.median([r['db'] for r in g]):+5.2f}pp")
print("\nWhite early-turnout rate (%), by site change")
for lbl,sel in [('lost sites',lambda r:r['ds']<0),('unchanged',lambda r:r['ds']==0),('gained',lambda r:r['ds']>0)]:
    g=[r for r in rows if sel(r)]
    print(f"  {lbl:11} n={len(g):3}  2022={statistics.median([r['w22'] for r in g]):5.2f}  "
          f"2026={statistics.median([r['w26'] for r in g]):5.2f}  change={statistics.median([r['dw'] for r in g]):+5.2f}pp")

def corr(x,y):
    mx,my=statistics.mean(x),statistics.mean(y)
    d=math.sqrt(sum((a-mx)**2 for a in x)*sum((b-my)**2 for b in y))
    return sum((a-mx)*(b-my) for a,b in zip(x,y))/d if d else 0
print(f"\ncorr(site change, Black turnout change) = {corr([r['ds'] for r in rows],[r['db'] for r in rows]):+.3f}")
print(f"corr(site change, White turnout change) = {corr([r['ds'] for r in rows],[r['dw'] for r in rows]):+.3f}")
