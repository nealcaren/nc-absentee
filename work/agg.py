import zipfile, io, csv, collections, pickle, datetime

FILES = [(2022,'absentee_20221108.zip','10/20/2022','10/25/2022'),
         (2024,'absentee_20241105.zip','10/17/2024','10/22/2024'),
         (2026,'absentee_20261103.zip','10/15/2026','10/20/2026')]

def rows(path):
    z = zipfile.ZipFile(path); name = z.namelist()[0]
    with z.open(name) as fh:
        for row in csv.DictReader(io.TextIOWrapper(fh, encoding='utf-8', errors='replace')):
            yield row

def agebucket(a):
    try: a=int(a)
    except: return 'UNK'
    if a<25: return '<25'
    if a<35: return '25-34'
    if a<45: return '35-44'
    if a<55: return '45-54'
    if a<65: return '55-64'
    if a<75: return '65-74'
    return '75+'

out={}
for yr, path, ws, we in FILES:
    ws_d=datetime.datetime.strptime(ws,'%m/%d/%Y').date()
    we_d=datetime.datetime.strptime(we,'%m/%d/%Y').date()
    site=collections.defaultdict(lambda: {'win':0,'tot':0,'first':None,'last':None,'race':collections.Counter(),'party':collections.Counter()})
    county=collections.Counter(); county_tot=collections.Counter()
    demo_win={k:collections.Counter() for k in ['race','ethnicity','party','gender','age']}
    demo_tot={k:collections.Counter() for k in ['race','ethnicity','party','gender','age']}
    mail_win=0; mail_tot=0; nc=0; nt=0
    for row in rows(path):
        if row['ballot_req_type']=='MAIL':
            d=row['ballot_req_dt']
            if row['ballot_rtn_status'] in ('ACCEPTED','ACCEPTED - CURED'):
                mail_tot+=1
                try:
                    if ws_d<=datetime.datetime.strptime(d,'%m/%d/%Y').date()<=we_d: mail_win+=1
                except: pass
            continue
        cty=row['county_desc'].strip(); sn=row['site_name'].strip()
        s=site[(cty,sn)]; s['tot']+=1; nt+=1
        county_tot[cty]+=1
        try:
            dd=datetime.datetime.strptime(row['ballot_send_dt'],'%m/%d/%Y').date()
        except: dd=None
        if s['first'] is None or (dd and dd<s['first']): s['first']=dd
        if s['last'] is None or (dd and dd>s['last']): s['last']=dd
        for k,val in [('race',row['race']),('ethnicity',row['ethnicity'].strip()),('party',row['voter_party_code']),('gender',row['gender']),('age',agebucket(row['age']))]:
            demo_tot[k][val]+=1
        if dd and ws_d<=dd<=we_d:
            s['win']+=1; nc+=1; county[cty]+=1
            for k,val in [('race',row['race']),('ethnicity',row['ethnicity'].strip()),('party',row['voter_party_code']),('gender',row['gender']),('age',agebucket(row['age']))]:
                demo_win[k][val]+=1
    out[yr]=dict(site={k:dict(v,race=dict(v['race']),party=dict(v['party'])) for k,v in site.items()},
                 county=dict(county),county_tot=dict(county_tot),
                 demo_win={k:dict(v) for k,v in demo_win.items()},
                 demo_tot={k:dict(v) for k,v in demo_tot.items()},
                 mail_win=mail_win,mail_tot=mail_tot,n_win=nc,n_tot=nt,ws=ws,we=we)
    print(yr,'in-person window',f"{nc:,}",'total',f"{nt:,}",'| sites all period',len(site),'| mail',f"{mail_tot:,}",flush=True)

pickle.dump(out, open('work/agg.pkl','wb'))
