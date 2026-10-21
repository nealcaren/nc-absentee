import pickle, statistics, math
d=pickle.load(open('work/agg.pkl','rb'))
def n(yr,c): return d[yr]['county'].get(c,0)
def s(yr,c): return sum(1 for k,v in d[yr]['site'].items() if k[0]==c and v['win']>0)

# need per-county race counts -> recompute from site-level race counters
def race_by_county(yr):
    out={}
    for (cty,sn),v in d[yr]['site'].items():
        if v['win']<=0: continue
        r=out.setdefault(cty,{'tot':0,'BLACK':0,'WHITE':0})
        r['tot']+=v['win']
        r['BLACK']+=v['race'].get('BLACK or AFRICAN AMERICAN',0)
        r['WHITE']+=v['race'].get('WHITE',0)
    return out
r22,r26=race_by_county(2022),race_by_county(2026)

rows=[]
for c in r22:
    if c not in r26: continue
    t22,t26=r22[c]['tot'],r26[c]['tot']
    if t22<500: continue
    rows.append(dict(c=c,v22=t22,v26=t26,
        g=100*(t26-t22)/t22,
        bs22=100*r22[c]['BLACK']/t22, bs26=100*r26[c]['BLACK']/t26,
        ds=s(2026,c)-s(2022,c)))

print("counties:",len(rows))
# turnout growth by site change
for lbl,sel in [('lost',lambda r:r['ds']<0),('same',lambda r:r['ds']==0),('gained',lambda r:r['ds']>0)]:
    g=[r for r in rows if sel(r)]
    print(f"  {lbl:7} n={len(g):3} median growth={statistics.median([r['g'] for r in g]):+6.1f}%  "
          f"median black share 2026={statistics.median([r['bs26'] for r in g]):5.1f}%  "
          f"median dBlackShare={statistics.median([r['bs26']-r['bs22'] for r in g]):+5.2f}")

# turnout growth by 2022 black share quartile
rs=sorted(rows,key=lambda r:r['bs22'])
q=len(rs)//4
print("\n  2022 black share quartile -> median turnout growth 22->26")
for i in range(4):
    g=rs[i*q:(i+1)*q] if i<3 else rs[3*q:]
    print(f"   Q{i+1} black share {g[0]['bs22']:.1f}-{g[-1]['bs22']:.1f}%  n={len(g):2}  median growth={statistics.median([r['g'] for r in g]):+6.1f}%  "
          f"median dBlackShare={statistics.median([r['bs26']-r['bs22'] for r in g]):+5.2f}")

def corr(xs,ys):
    mx,my=statistics.mean(xs),statistics.mean(ys)
    return sum((x-mx)*(y-my) for x,y in zip(xs,ys))/math.sqrt(sum((x-mx)**2 for x in xs)*sum((y-my)**2 for y in ys))
print(f"\ncorr(site change, black share change) = {corr([r['ds'] for r in rows],[r['bs26']-r['bs22'] for r in rows]):+.3f}")
print(f"corr(site change, turnout growth)     = {corr([r['ds'] for r in rows],[r['g'] for r in rows]):+.3f}")
print(f"corr(black share 22, turnout growth)  = {corr([r['bs22'] for r in rows],[r['g'] for r in rows]):+.3f}")

print("\nVotes per site (6-day window):")
for yr in (2022,2024,2026):
    ns=sum(1 for k,v in d[yr]['site'].items() if v['win']>0)
    print(f"  {yr}: {d[yr]['n_win']:,} votes / {ns} sites = {d[yr]['n_win']/ns:,.0f} per site")
