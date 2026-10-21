import zipfile, io, csv, collections, pickle, datetime, sys
FILES=[(2022,'absentee_20221108.zip','10/20/2022','10/25/2022'),
       (2024,'absentee_20241105.zip','10/17/2024','10/22/2024'),
       (2026,'absentee_20261103.zip','10/15/2026','10/20/2026')]
out={}
for yr,path,ws,we in FILES:
    wsd=datetime.datetime.strptime(ws,'%m/%d/%Y').date(); wed=datetime.datetime.strptime(we,'%m/%d/%Y').date()
    prec=collections.defaultdict(lambda: collections.Counter())
    cty=collections.defaultdict(lambda: collections.Counter())
    z=zipfile.ZipFile(path)
    n=0
    with z.open(z.namelist()[0]) as fh:
        for row in csv.DictReader(io.TextIOWrapper(fh,encoding='utf-8',errors='replace')):
            if row['ballot_req_type']=='MAIL': continue
            if row['ballot_rtn_status'] not in ('ACCEPTED','ACCEPTED - CURED','ACCEPTED - EXCEPTION'): continue
            try: d=datetime.datetime.strptime(row['ballot_send_dt'],'%m/%d/%Y').date()
            except: continue
            if not (wsd<=d<=wed): continue
            n+=1
            c=row['county_desc'].strip(); p=row['precinct_desc'].strip(); rc=row['race']
            key={'WHITE':'W','BLACK or AFRICAN AMERICAN':'B','ASIAN':'A','INDIAN AMERICAN or ALASKA NATIVE':'I',
                 'TWO or MORE RACES':'M','NATIVE HAWAIIAN or PACIFIC ISLANDER':'P','OTHER':'O'}.get(rc,'U')
            prec[(c,p)][key]+=1
            cty[c][key]+=1
    print(yr,"window early voters",f"{n:,}","precinct keys",len(prec),flush=True)
    out[yr]={'prec':{k:dict(v) for k,v in prec.items()},'cty':{k:dict(v) for k,v in cty.items()}}
pickle.dump(out,open('work/abs_prec.pkl','wb'))
