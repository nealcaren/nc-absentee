import pickle, collections, datetime, csv
D=pickle.load(open('work/daily.pkl','rb'))
ED={y:datetime.date.fromisoformat(D[y]['election']) for y in D}
LAST=6
PARTS=['DEM','REP','UNA','LIB','OTH']

def dayk(y,p=None):
    ed=ED[y]; s=collections.Counter()
    for dt,n in D[y]['total'].items():
        k=(dt-(ed-datetime.timedelta(days=19))).days+1
        if not (1<=k<=17): continue
        if p is None: s[k]+=n
        elif p=='OTH':
            known=sum(D[y]['party'].get(f"{(ed-dt).days}|{q}",0) for q in ('DEM','REP','UNA','LIB'))
            s[k]+=n-known
        else: s[k]+=D[y]['party'].get(f"{(ed-dt).days}|{p}",0)
    return s

T={y:dayk(y) for y in (2022,2024,2026)}
P={p:{y:dayk(y,p) for y in (2022,2024,2026)} for p in PARTS}

# party-specific scale through day 6
S={p:(sum(P[p][2026][k] for k in range(1,7))/sum(P[p][2022][k] for k in range(1,7)))
   for p in PARTS}
S['ALL']=sum(T[2026][k] for k in range(1,7))/sum(T[2022][k] for k in range(1,7))
S['OTH']=S['ALL']  # tiny residual, own scale is noise

def pathA(p):
    return {k:P[p][2022].get(k,0)*S[p] for k in range(1,18)}
def pathB(p):
    return {k:(P[p][2026].get(k,0) if k<=LAST else P[p][2022].get(k,0)) for k in range(1,18)}

A={k:sum(pathA(p)[k] for p in PARTS) for k in range(1,18)}
B={k:sum(pathB(p)[k] for p in PARTS) for k in range(1,18)}

print("party scales through day 6 (2026 / 2022):")
for p in PARTS+['ALL']: print(f"   {p:4} {S[p]:.3f}x")

print(f"\n{'day':>4}{'date':>8}{'dow':>5}{'2022':>9}{'2026':>9}{'A':>9}{'B':>9}{'2024':>9}")
for k in range(1,18):
    dt=ED[2026]-datetime.timedelta(days=20-k)
    o=T[2026].get(k,0) if k<=LAST else None
    print(f"{k:>4}{dt.strftime('%b %d'):>8}{dt.strftime('%a'):>5}{T[2022].get(k,0):>9,}"
          f"{(f'{o:,}' if o else '—'):>9}{A[k]:>9,.0f}{B[k]:>9,.0f}{T[2024].get(k,0):>9,}")

print(f"\nTotals: A {sum(A.values()):,.0f}   B {sum(B.values()):,.0f}   2022 actual {sum(T[2022].values()):,}")

print(f"\n{'party':>5}{'banked':>10}{'scale':>8}{'A total':>11}{'B total':>11}{'A share':>9}{'B share':>9}")
for p in PARTS:
    bank=sum(P[p][2026][k] for k in range(1,7))
    a=sum(pathA(p).values()); b=sum(pathB(p).values())
    print(f"{p:>5}{bank:>10,}{S[p]:>8.2f}{a:>11,.0f}{b:>11,.0f}{'':>9}{'':>9}")
for nm,X in (('A',A),('B',B)):
    d=sum(pathA('DEM').values()) if nm=='A' else sum(pathB('DEM').values())
    r=sum(pathA('REP').values()) if nm=='A' else sum(pathB('REP').values())
    print(f"   path {nm}: early D {d:,.0f} R {r:,.0f} D lead {d-r:+,.0f} D share {100*d/(d+r):.1f}%")

with open('analysis/daily_forecast.csv','w',newline='') as f:
    w=csv.writer(f)
    hdr=['day','date','dow','observed_total','path_a_total','path_b_total','y2022','y2024']
    for p in ('DEM','REP','UNA'):
        hdr += [f'obs_{p.lower()}' if False else f'observed_{p.lower()}',f'path_a_{p.lower()}',f'path_b_{p.lower()}']
    w.writerow(hdr)
    for k in range(1,18):
        dt=ED[2026]-datetime.timedelta(days=20-k)
        row=[k,dt.isoformat(),dt.strftime('%a'),
             (T[2026].get(k,0) if k<=LAST else ''),round(A[k]),round(B[k]),T[2022].get(k,0),T[2024].get(k,0)]
        for p in ('DEM','REP','UNA'):
            row += [(P[p][2026].get(k,0) if k<=LAST else ''),round(pathA(p)[k]),round(pathB(p)[k])]
        w.writerow(row)
print("\nwrote analysis/daily_forecast.csv")
