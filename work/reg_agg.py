import zipfile, io, csv, collections, pickle, sys
z=zipfile.ZipFile('/Users/nealcaren/Downloads/ncvoter_Statewide.zip')
reg_prec=collections.defaultdict(lambda: collections.Counter())   # (county,precinct) -> race
reg_cty=collections.defaultdict(lambda: collections.Counter())    # county -> race
reg_party=collections.defaultdict(lambda: collections.Counter())
reg_age=collections.defaultdict(lambda: collections.Counter())
n=0
with z.open(z.namelist()[0]) as fh:
    for row in csv.DictReader(io.TextIOWrapper(fh,encoding='utf-8',errors='replace'),delimiter='\t'):
        n+=1
        if row['voter_status_desc']!='ACTIVE': continue
        c=row['county_desc'].strip(); p=row['precinct_desc'].strip(); rc=row['race_code']
        reg_prec[(c,p)][rc]+=1
        reg_cty[c][rc]+=1
        reg_party[c][row['party_cd']]+=1
        try: a=int(row['age_at_year_end'])
        except: a=0
        reg_age[c]['<25' if a<25 else '25-34' if a<35 else '35-44' if a<45 else '45-54' if a<55 else '55-64' if a<65 else '65-74' if a<75 else '75+']+=1
        if n%1000000==0: print(n,flush=True)
print("total rows",n,flush=True)
pickle.dump({'prec':{k:dict(v) for k,v in reg_prec.items()},
             'cty':{k:dict(v) for k,v in reg_cty.items()},
             'party':{k:dict(v) for k,v in reg_party.items()},
             'age':{k:dict(v) for k,v in reg_age.items()}},open('work/reg2026.pkl','wb'))
print("active registered:",sum(sum(v.values()) for v in reg_prec.values()))
