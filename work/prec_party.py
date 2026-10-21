import zipfile, io, csv, collections, pickle, datetime
FILES=[(2022,'absentee_20221108.zip','10/20/2022','10/25/2022','work/cw2022.pkl'),
       (2024,'absentee_20241105.zip','10/17/2024','10/22/2024','work/cw2024.pkl'),
       (2026,'absentee_20261103.zip','10/15/2026','10/20/2026','work/cw2026.pkl')]
out={}
for yr,path,ws,we,cwf in FILES:
    cw=pickle.load(open(cwf,'rb'))
    wsd=datetime.datetime.strptime(ws,'%m/%d/%Y').date(); wed=datetime.datetime.strptime(we,'%m/%d/%Y').date()
    d=collections.defaultdict(lambda: collections.Counter()); unm=0
    z=zipfile.ZipFile(path)
    with z.open(z.namelist()[0]) as fh:
        for row in csv.DictReader(io.TextIOWrapper(fh,encoding='utf-8',errors='replace')):
            if row['ballot_req_type']=='MAIL': continue
            if row['ballot_rtn_status'] not in ('ACCEPTED','ACCEPTED - CURED','ACCEPTED - EXCEPTION'): continue
            try: dt=datetime.datetime.strptime(row['ballot_send_dt'],'%m/%d/%Y').date()
            except: continue
            if not (wsd<=dt<=wed): continue
            c=row['county_desc'].strip(); p=row['precinct_desc'].strip()
            ab=cw.get(c,{}).get(p)
            if ab is None: unm+=1; continue
            d[(c,ab)][row['voter_party_code']]+=1
    print(f"{yr}: {len(d)} precincts, {sum(sum(v.values()) for v in d.values()):,} votes, {unm:,} unmapped",flush=True)
    out[yr]={k:dict(v) for k,v in d.items()}
pickle.dump(out,open('work/prec_party.pkl','wb'))
