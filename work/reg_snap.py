import zipfile, io, csv, collections, pickle, sys
path, out = sys.argv[1], sys.argv[2]
z=zipfile.ZipFile(path)
reg_prec=collections.defaultdict(lambda: collections.Counter())
reg_cty=collections.defaultdict(lambda: collections.Counter())
reg_party=collections.defaultdict(lambda: collections.Counter())
reg_age=collections.defaultdict(lambda: collections.Counter())
n=0
with z.open(z.namelist()[0]) as fh:
    r=csv.reader(io.TextIOWrapper(fh,encoding='utf-16',errors='replace'),delimiter='\t')
    hdr=[h.strip() for h in next(r)]
    ix={k:i for i,k in enumerate(hdr)}
    ci,pi,ri,si,pa=ix['county_desc'],ix['precinct_desc'],ix['race_code'],ix['voter_status_desc'],ix['party_cd']
    ai=ix.get('age_at_year_end', ix.get('age'))
    for row in r:
        n+=1
        if len(row)<len(hdr): continue
        if row[si].strip()!='ACTIVE': continue
        c=row[ci].strip(); p=row[pi].strip(); rc=row[ri].strip()
        reg_prec[(c,p)][rc]+=1; reg_cty[c][rc]+=1; reg_party[c][row[pa].strip()]+=1
        try: a=int(row[ai])
        except: a=0
        reg_age[c]['<25' if a<25 else '25-34' if a<35 else '35-44' if a<45 else '45-54' if a<55 else '55-64' if a<65 else '65-74' if a<75 else '75+']+=1
        if n%2000000==0: print(n,flush=True)
print("rows",n,"active",sum(sum(v.values()) for v in reg_prec.values()),flush=True)
pickle.dump({'prec':{k:dict(v) for k,v in reg_prec.items()},'cty':{k:dict(v) for k,v in reg_cty.items()},
             'party':{k:dict(v) for k,v in reg_party.items()},'age':{k:dict(v) for k,v in reg_age.items()}},open(out,'wb'))
