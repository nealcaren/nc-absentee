import pickle, collections
d=pickle.load(open('work/agg.pkl','rb'))

for yr in (2022,2024,2026):
    s=d[yr]['site']
    win=[k for k,v in s.items() if v['win']>0]
    print(f"{yr}: distinct sites total={len(s)}  active-in-window={len(win)}  window votes={d[yr]['n_win']:,}")
    # counties with any site
    print("    counties with >=1 site:", len({k[0] for k in s}))

print()
# per-county comparison of window-active sites
def winsites(yr):
    return {k for k,v in d[yr]['site'].items() if v['win']>0}
a,b,c=winsites(2022),winsites(2024),winsites(2026)
print("2026 vs 2024: shared",len(c&b),"| only 2026",len(c-b),"| dropped",len(b-c))
print("2026 vs 2022: shared",len(c&a),"| only 2026",len(c-a),"| dropped",len(a-c))

counties=sorted({k[0] for k in a|b|c})
rows=[]
for cty in counties:
    na=sum(1 for k in a if k[0]==cty); nb=sum(1 for k in b if k[0]==cty); nc_=sum(1 for k in c if k[0]==cty)
    rows.append((cty,na,nb,nc_,nc_-nb,nc_-na))
rows.sort(key=lambda r:r[4])
print(f"\n{'county':22}{'2022':>6}{'2024':>6}{'2026':>6}{'v24':>6}{'v22':>6}")
for r in rows:
    flag=' <<<' if r[4]<=-2 else ''
    print(f"{r[0]:22}{r[1]:>6}{r[2]:>6}{r[3]:>6}{r[4]:>6}{r[5]:>6}{flag}")
