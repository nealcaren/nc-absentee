import pickle, collections
d=pickle.load(open('work/agg2.pkl','rb'))
print("party codes present:")
for yr in (2022,2024,2026):
    c=collections.Counter()
    for x in d[yr]['county'].values():
        for k,v in x['party'].items(): c[k]+=v
    print(f"  {yr}:",dict(c))

print("\nCounties that lost the most sites vs 2022:")
for cty in ['JOHNSTON','LENOIR','SAMPSON','PENDER','VANCE','WILSON','CUMBERLAND']:
    a=d[2022]['county'].get(cty,{}).get('win',0); b=d[2026]['county'].get(cty,{}).get('win',0)
    sa=sum(1 for k in d[2022]['site'] if k[0]==cty); sb=sum(1 for k in d[2026]['site'] if k[0]==cty)
    print(f"  {cty:12} sites {sa}->{sb}  votes {a:,}->{b:,} ({100*(b-a)/a:+.0f}%)" if a else cty)

print("\nLargest counties:")
for cty in ['WAKE','MECKLENBURG','GUILFORD','FORSYTH','DURHAM','BUNCOMBE','CUMBERLAND','NEW HANOVER']:
    a=d[2022]['county'].get(cty,{}).get('win',0); b=d[2026]['county'].get(cty,{}).get('win',0)
    sa=sum(1 for k in d[2022]['site'] if k[0]==cty); sb=sum(1 for k in d[2026]['site'] if k[0]==cty)
    print(f"  {cty:12} sites 22:{sa:3} 24:{sum(1 for k in d[2024]['site'] if k[0]==cty):3} 26:{sb:3}   "
          f"votes {a:,}->{b:,} ({100*(b-a)/a:+.0f}%)")

print("\nDemocratic/Republican share of window votes:")
for yr in (2022,2024,2026):
    p=collections.Counter()
    for x in d[yr]['county'].values():
        for k,v in x['party'].items(): p[k]+=v
    t=sum(p.values())
    print(f"  {yr}: DEM {100*p['DEM']/t:5.2f}%  REP {100*p['REP']/t:5.2f}%  UNA {100*p['UNA']/t:5.2f}%")
