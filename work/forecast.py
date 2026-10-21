import pickle, collections
A=pickle.load(open('work/abs_full.pkl','rb'))
H=pickle.load(open('work/history2.pkl','rb'))
reg={y:pickle.load(open(f'work/reg{y}.pkl','rb')) for y in (2022,2024,2026)}

def e6(y,p): return sum(v.get(p,0) for v in A[y]['party'].values())
def regp(y,p): return sum(v.get(p,0) for v in reg[y]['party'].values())

print("First-6-day early votes by party")
for y in (2022,2024,2026):
    print(f"  {y}: ", {p: f"{e6(y,p):,}" for p in ['DEM','REP','UNA']})

print("\nShare of each party's TOTAL vote cast in the first 6 days")
for y in (2022,2024):
    print(f"  {y}: ", {p: f"{100*e6(y,p)/H[y]['tot'][p]:.1f}%" for p in ['DEM','REP','UNA']})

print("\nNaive backtest: day-6 early composition vs final result")
fin={2022:-4.07,2024:-3.83}
for y in (2022,2024):
    d=e6(y,'DEM'); r=e6(y,'REP')
    print(f"  {y}: day-6 early D-R = {100*(d-r)/(d+r):+.1f}   final two-party D-R = {fin[y]:+.1f}   miss = {fin[y]-100*(d-r)/(d+r):+.1f}")

print("\nPROJECTION for 2026 (total = early6 / historical day-6 share)")
for base in (2022,2024):
    tot={}
    for p in ['DEM','REP','UNA']:
        tot[p]=e6(2026,p)*H[base]['tot'][p]/e6(base,p)
    s=sum(tot.values())
    print(f"  calibrated on {base}: DEM {tot['DEM']:>9,.0f} ({100*tot['DEM']/s:.1f}%)  "
          f"REP {tot['REP']:>9,.0f} ({100*tot['REP']/s:.1f}%)  UNA {tot['UNA']:>9,.0f} ({100*tot['UNA']/s:.1f}%)  "
          f"total {s/1e6:.2f}M   D-R {100*(tot['DEM']-tot['REP'])/s:+.1f}")

print("\nWhat each party still needs on Election Day (per 1,000 early votes already banked)")
for p in ['DEM','REP']:
    print(f"  {p}: {e6(2026,p)/1000:.1f}k banked; 2022 ED/early ratio = {H[2022]['ed'][p]/H[2022]['early'][p]:.3f}; "
          f"2024 = {H[2024]['ed'][p]/H[2024]['early'][p]:.3f}")
