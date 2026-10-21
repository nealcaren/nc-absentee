import zipfile, io, csv, collections, pickle, datetime
FILES=[(2022,'absentee_20221108.zip','10/20/2022','10/25/2022'),
       (2024,'absentee_20241105.zip','10/17/2024','10/22/2024'),
       (2026,'absentee_20261103.zip','10/15/2026','10/20/2026')]
RACE={'WHITE':'W','BLACK or AFRICAN AMERICAN':'B','ASIAN':'A','INDIAN AMERICAN or ALASKA NATIVE':'I',
      'TWO or MORE RACES':'M','NATIVE HAWAIIAN or PACIFIC ISLANDER':'P','OTHER':'O'}
def ag(a):
    try: a=int(a)
    except: return 'UNK'
    return '<25' if a<25 else '25-34' if a<35 else '35-44' if a<45 else '45-54' if a<55 else '55-64' if a<65 else '65-74' if a<75 else '75+'
out={}
for yr,path,ws,we in FILES:
    wsd=datetime.datetime.strptime(ws,'%m/%d/%Y').date(); wed=datetime.datetime.strptime(we,'%m/%d/%Y').date()
    prec=collections.defaultdict(lambda: collections.Counter())
    party=collections.defaultdict(lambda: collections.Counter())
    age=collections.defaultdict(lambda: collections.Counter())
    ps=collections.defaultdict(lambda: collections.Counter())   # (county,precinct) -> site
    z=zipfile.ZipFile(path); n=0
    with z.open(z.namelist()[0]) as fh:
        for row in csv.DictReader(io.TextIOWrapper(fh,encoding='utf-8',errors='replace')):
            if row['ballot_req_type']=='MAIL': continue
            if row['ballot_rtn_status'] not in ('ACCEPTED','ACCEPTED - CURED','ACCEPTED - EXCEPTION'): continue
            try: d=datetime.datetime.strptime(row['ballot_send_dt'],'%m/%d/%Y').date()
            except: continue
            if not (wsd<=d<=wed): continue
            n+=1
            c=row['county_desc'].strip(); p=row['precinct_desc'].strip()
            rc=RACE.get(row['race'],'U')
            prec[(c,p)][rc]+=1
            party[c][row['voter_party_code']]+=1
            age[c][ag(row['age'])]+=1
            ps[(c,p)][row['site_name'].strip()]+=1
    print(yr,f"{n:,}",flush=True)
    out[yr]={'prec':{k:dict(v) for k,v in prec.items()},
             'party':{k:dict(v) for k,v in party.items()},
             'age':{k:dict(v) for k,v in age.items()},
             'ps':{k:dict(v) for k,v in ps.items()}}
pickle.dump(out,open('work/abs_full.pkl','wb'))
