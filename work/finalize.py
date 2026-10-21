import pickle, collections, csv, statistics
reg={y:pickle.load(open(f'work/reg{y}.pkl','rb')) for y in (2022,2024,2026)}
A=pickle.load(open('work/abs_full.pkl','rb'))
S=pickle.load(open('work/agg2.pkl','rb'))
sites26=collections.defaultdict(set)
for (c,sn) in S[2026]['site']: sites26[c].add(sn)

rows=[]
for (c,p),v in A[2022]['ps'].items():
    if sum(v.values())<100: continue
    modal=max(v.items(),key=lambda x:x[1])[0]
    if (c,p) not in A[2026]['ps']: continue
    r22=reg[2022]['prec'].get((c,p),{}); r26=reg[2026]['prec'].get((c,p),{})
    if sum(r22.values())<100 or sum(r26.values())<100: continue
    a22=A[2022]['prec'].get((c,p),{}); a26=A[2026]['prec'].get((c,p),{})
    rows.append(dict(county=c,precinct=p,modal_site_2022=modal,
        lost_site=1 if modal not in sites26.get(c,set()) else 0,
        reg_2022=sum(r22.values()),reg_2026=sum(r26.values()),
        turnout_2022=round(100*sum(v.values())/sum(r22.values()),3),
        turnout_2026=round(100*sum(a26.values())/sum(r26.values()),3),
        black_share_reg_2022=round(100*r22.get('B',0)/sum(r22.values()),2)))
with open('analysis/precinct_site_loss.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print("wrote analysis/precinct_site_loss.csv",len(rows),"precincts")

# statewide rates for report
def rate(y,rc,table='prec'):
    num=sum(v.get(rc,0) for v in A[y]['prec'].values())
    den=sum(v.get(rc,0) for v in reg[y]['prec'].values())
    return 100*num/den
def prate(y,p):
    num=sum(v.get(p,0) for v in A[y]['party'].values())
    den=sum(v.get(p,0) for v in reg[y]['party'].values())
    return 100*num/den
print("\nrace rates:",{rc:[round(rate(y,rc),2) for y in (2022,2024,2026)] for rc in ['W','B']})
print("party rates:",{p:[round(prate(y,p),2) for y in (2022,2024,2026)] for p in ['DEM','REP','UNA']})
