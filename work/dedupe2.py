import zipfile, io, csv, collections, datetime
FILES=[(2022,'absentee_20221108.zip',datetime.date(2022,10,20),datetime.date(2022,10,25)),
       (2024,'absentee_20241105.zip',datetime.date(2024,10,17),datetime.date(2024,10,22)),
       (2026,'absentee_20261103.zip',datetime.date(2026,10,15),datetime.date(2026,10,20))]
def rows(p):
    z=zipfile.ZipFile(p); n=z.namelist()[0]
    with z.open(n) as fh:
        for r in csv.DictReader(io.TextIOWrapper(fh,encoding='utf-8',errors='replace')): yield r
for yr,path,ws,we in FILES:
    seen=set(); dup=0; rows_=0
    for r in rows(path):
        if r['ballot_req_type']=='MAIL': continue
        try: d=datetime.datetime.strptime(r['ballot_send_dt'],'%m/%d/%Y').date()
        except: continue
        if not (ws<=d<=we): continue
        rows_+=1
        k=(r['county_desc'],r['voter_reg_num'])
        if k in seen: dup+=1
        else: seen.add(k)
    print(f"{yr}: rows={rows_:,} distinct voters={len(seen):,} dup rows={dup:,} ({100*dup/rows_:.2f}%)")
