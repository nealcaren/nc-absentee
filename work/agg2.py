import zipfile, io, csv, collections, pickle, datetime
FILES = [(2022,'absentee_20221108.zip','10/20/2022','10/25/2022'),
         (2024,'absentee_20241105.zip','10/17/2024','10/22/2024'),
         (2026,'absentee_20261103.zip','10/15/2026','10/20/2026')]
def rows(path):
    z=zipfile.ZipFile(path); n=z.namelist()[0]
    with z.open(n) as fh:
        for r in csv.DictReader(io.TextIOWrapper(fh,encoding='utf-8',errors='replace')): yield r
def ab(a):
    try: a=int(a)
    except: return 'UNK'
    return '<25' if a<25 else '25-34' if a<35 else '35-44' if a<45 else '45-54' if a<55 else '55-64' if a<65 else '65-74' if a<75 else '75+'

out={}
for yr,path,ws,we in FILES:
    wsd=datetime.datetime.strptime(ws,'%m/%d/%Y').date(); wed=datetime.datetime.strptime(we,'%m/%d/%Y').date()
    site=collections.defaultdict(lambda:{'win':0,'race':collections.Counter(),'party':collections.Counter()})
    cty=collections.defaultdict(lambda:{'win':0,'race':collections.Counter(),'party':collections.Counter(),'age':collections.Counter()})
    for r in rows(path):
        if r['ballot_req_type']=='MAIL': continue
        try: dd=datetime.datetime.strptime(r['ballot_send_dt'],'%m/%d/%Y').date()
        except: continue
        if not (wsd<=dd<=wed): continue
        c=r['county_desc'].strip(); sn=r['site_name'].strip()
        S=site[(c,sn)]; S['win']+=1; S['race'][r['race']]+=1; S['party'][r['voter_party_code']]+=1
        C=cty[c]; C['win']+=1; C['race'][r['race']]+=1; C['party'][r['voter_party_code']]+=1; C['age'][ab(r['age'])]+=1
    out[yr]={'site':{k:{'win':v['win'],'race':dict(v['race']),'party':dict(v['party'])} for k,v in site.items()},
             'county':{k:{'win':v['win'],'race':dict(v['race']),'party':dict(v['party']),'age':dict(v['age'])} for k,v in cty.items()}}
    print(yr,'done',len(site),'sites',sum(v['win'] for v in site.values()),'votes',flush=True)
pickle.dump(out,open('work/agg2.pkl','wb'))
