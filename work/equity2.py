import pickle, statistics, math
d=pickle.load(open('work/agg2.pkl','rb'))
B='BLACK or AFRICAN AMERICAN'; W='WHITE'

def corr(xs,ys):
    mx,my=statistics.mean(xs),statistics.mean(ys)
    den=math.sqrt(sum((x-mx)**2 for x in xs)*sum((y-my)**2 for y in ys))
    return sum((x-mx)*(y-my) for x,y in zip(xs,ys))/den if den else 0.0

def sitecount(yr,c): return sum(1 for k in d[yr]['site'] if k[0]==c)

rows=[]
for c in d[2022]['county']:
    if c not in d[2026]['county']: continue
    a,b=d[2022]['county'][c],d[2026]['county'][c]
    if a['win']<500: continue
    rows.append(dict(c=c,v22=a['win'],v26=b['win'],g=100*(b['win']-a['win'])/a['win'],
      bs22=100*a['race'].get(B,0)/a['win'], bs26=100*b['race'].get(B,0)/b['win'],
      ds=sitecount(2026,c)-sitecount(2022,c)))
print("counties:",len(rows))
print("\nBy site change, 2022->2026:")
for lbl,sel in [('lost sites',lambda r:r['ds']<0),('unchanged',lambda r:r['ds']==0),('gained',lambda r:r['ds']>0)]:
    g=[r for r in rows if sel(r)]
    print(f"  {lbl:11} n={len(g):3}  median turnout growth={statistics.median([r['g'] for r in g]):+6.1f}%"
          f"  median Black share 22={statistics.median([r['bs22'] for r in g]):5.1f}%"
          f"  26={statistics.median([r['bs26'] for r in g]):5.1f}%"
          f"  d={statistics.median([r['bs26']-r['bs22'] for r in g]):+5.2f}")

rs=sorted(rows,key=lambda r:r['bs22']); q=max(1,len(rs)//4)
print("\nBy 2022 Black share quartile:")
for i in range(4):
    g=rs[i*q:(i+1)*q] if i<3 else rs[3*q:]
    print(f"  Q{i+1} {g[0]['bs22']:5.1f}-{g[-1]['bs22']:5.1f}%  n={len(g):2}  "
          f"median growth={statistics.median([r['g'] for r in g]):+6.1f}%  "
          f"median dBlackShare={statistics.median([r['bs26']-r['bs22'] for r in g]):+5.2f}  "
          f"median dSites={statistics.median([r['ds'] for r in g]):+.0f}")

print(f"\ncorr(dSites, dBlackShare)      = {corr([r['ds'] for r in rows],[r['bs26']-r['bs22'] for r in rows]):+.3f}")
print(f"corr(dSites, turnout growth)   = {corr([r['ds'] for r in rows],[r['g'] for r in rows]):+.3f}")
print(f"corr(Black share 22, growth)   = {corr([r['bs22'] for r in rows],[r['g'] for r in rows]):+.3f}")

print("\nVotes per site, 6-day window:")
for yr in (2022,2024,2026):
    n=len(d[yr]['site']); v=sum(x['win'] for x in d[yr]['site'].values())
    print(f"  {yr}: {v:,} / {n} = {v/n:,.0f}")

print("\nBlack share of early voters by year (window):")
for yr in (2022,2024,2026):
    tot=sum(c['win'] for c in d[yr]['county'].values())
    blk=sum(c['race'].get(B,0) for c in d[yr]['county'].values())
    wht=sum(c['race'].get(W,0) for c in d[yr]['county'].values())
    print(f"  {yr}: Black {100*blk/tot:.2f}%  White {100*wht/tot:.2f}%  (n={tot:,})")
