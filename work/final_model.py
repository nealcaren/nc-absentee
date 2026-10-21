import pickle, collections, statistics
E=pickle.load(open('work/prec_party.pkl','rb'))
H=pickle.load(open('work/hist_prec.pkl','rb'))
rows=pickle.load(open('work/panel.pkl','rb'))
for r in rows:
    for y in ('22','24'):
        pd=r[f'T{y}d']-r[f'd{y}']; pr=r[f'T{y}r']-r[f'r{y}']
        r[f's{y}']=pr/(pd+pr) if (pd+pr)>0 else None
    r['tot22']=r['T22d']+r['T22r']; r['tot24']=r['T24d']+r['T24r']
ok=[r for r in rows if r['s22'] is not None and r['s24'] is not None]

def cty_shares(yr):
    agg=collections.defaultdict(lambda:[0.0,0.0])
    for p in ok:
        agg[p['c'][0]][0]+=p[f'T{yr}d']-p[f'd{yr}']
        agg[p['c'][0]][1]+=p[f'T{yr}r']-p[f'r{yr}']
    return {k:v[1]/(v[0]+v[1]) for k,v in agg.items() if v[0]+v[1]>0}
S22,S24=cty_shares('22'),cty_shares('24')
SAVG={k:(S22[k]+S24.get(k,S22[k]))/2 for k in S22}

# base per-precinct final D+R from 2022, county fallback
base22={}
bycty=collections.defaultdict(list)
for p in ok:
    base22[p['c']]=p['tot22']; bycty[p['c'][0]].append(p['tot22'])
cty_med={k:statistics.median(v) for k,v in bycty.items()}

def final_share(c):
    return SAVG.get(c, SAVG.get(c, 0.51))

def project(N, sharemap, base_total=None):
    tot=sum(base22.values()) if base_total is None else base_total
    g=N/tot
    D=R=0.0; miss=0
    for c,v in E[2026].items():
        b=base22.get(c)
        if b is None:
            b=cty_med.get(c[0]); 
            if b is None: miss+=1; continue
        bank=v.get('DEM',0)+v.get('REP',0)
        if bank==0: continue
        final=b*g
        rem=max(0.0,final-bank)
        s=sharemap.get(c[0],0.51)
        D+=v.get('DEM',0)+(1-s)*rem
        R+=v.get('REP',0)+s*rem
    return D,R,miss

print(f"{'N':>7}{'base':>8}{'shares':>9}{'D':>11}{'R':>11}{'D-R reg':>9}")
res=[]
for N in (2_600_000,2_900_000,3_200_000):
    for sm,lbl in [(S22,'2022'),(S24,'2024'),(SAVG,'avg')]:
        D,R,miss=project(N,sm)
        m=100*(D-R)/(D+R)
        res.append(m)
        print(f"{N/1e6:>7.1f}{'2022':>8}{lbl:>9}{D:>11,.0f}{R:>11,.0f}{m:>+9.2f}")
print(f"\nrange of registration margin: {min(res):+.2f} to {max(res):+.2f}   center {statistics.median(res):+.2f}")
print(f"after registration->vote correction (R+1.7 to R+3.3):")
print(f"   {min(res)-3.3:+.2f} to {max(res)-1.7:+.2f}   center {statistics.median(res)-2.5:+.2f}")
