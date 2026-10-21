import pickle, collections, difflib
d=pickle.load(open('work/agg.pkl','rb'))
def ws(yr): return {k for k,v in d[yr]['site'].items() if v['win']>0}
a,b,c=ws(2022),ws(2024),ws(2026)

for cty in ['GUILFORD','MECKLENBURG','WAKE','JOHNSTON','LENOIR','SAMPSON']:
    print(f"===== {cty}")
    for yr,S in [(2022,a),(2024,b),(2026,c)]:
        print(f"  {yr}:", sorted(k[1] for k in S if k[0]==cty))

print("\n===== fuzzy match attempt: 2024 sites with no exact 2026 match")
for cty,sn in sorted(b-c):
    cand=difflib.get_close_matches(sn,[k[1] for k in c if k[0]==cty],n=1,cutoff=0.6)
    print(f"  {cty:15} DROPPED: {sn[:45]:45} close2026: {cand}")
