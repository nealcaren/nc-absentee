import pickle, collections
E=pickle.load(open('work/prec_party.pkl','rb'))
H=pickle.load(open('work/hist_prec.pkl','rb'))
def hist(c,yr,party):
    return sum(v for k,v in H[yr].get(c,{}).items() if k.startswith(party+'|'))
keys={y:set(E[y]) for y in (2022,2024,2026)}
for y in (2022,2024): keys[y]&=set(H[y])
common=keys[2022]&keys[2024]&keys[2026]
print("present in all 3 years + history:",len(common))
rows=[]
for c in common:
    d22,r22=E[2022][c].get('DEM',0),E[2022][c].get('REP',0)
    d24,r24=E[2024][c].get('DEM',0),E[2024][c].get('REP',0)
    d26,r26=E[2026][c].get('DEM',0),E[2026][c].get('REP',0)
    T22d,T22r=hist(c,2022,'DEM'),hist(c,2022,'REP')
    T24d,T24r=hist(c,2024,'DEM'),hist(c,2024,'REP')
    if min(d22+r22,d24+r24,d26+r26,T22d+T22r,T24d+T24r)==0: continue
    rows.append(dict(c=c,d22=d22,r22=r22,d24=d24,r24=r24,d26=d26,r26=r26,
        T22d=T22d,T22r=T22r,T24d=T24d,T24r=T24r))
print("usable precincts:",len(rows))
print("2022 early D+R in panel:",f"{sum(r['d22']+r['r22'] for r in rows):,}")
print("2024 early D+R in panel:",f"{sum(r['d24']+r['r24'] for r in rows):,}")
print("2026 early D+R in panel:",f"{sum(r['d26']+r['r26'] for r in rows):,}  (total 2026: 576,968)")
for y in ('22','24'):
    pd=sum(r[f'T{y}d']-r[f'd{y}'] for r in rows); pr=sum(r[f'T{y}r']-r[f'r{y}'] for r in rows)
    print(f"  20{y} post-day-6: D {pd:,} R {pr:,}  R share {100*pr/(pd+pr):.1f}%")
pickle.dump(rows,open('work/panel.pkl','wb'))
