import zipfile, io, csv, collections, datetime
FILES=[(2022,'absentee_20221108.zip',datetime.date(2022,10,20),datetime.date(2022,10,25)),
       (2024,'absentee_20241105.zip',datetime.date(2024,10,17),datetime.date(2024,10,22)),
       (2026,'absentee_20261103.zip',datetime.date(2026,10,15),datetime.date(2026,10,20))]
def rows(p):
    z=zipfile.ZipFile(p); n=z.namelist()[0]
    with z.open(n) as fh:
        for r in csv.DictReader(io.TextIOWrapper(fh,encoding='utf-8',errors='replace')): yield r
for yr,path,ws,we in FILES:
    seen=set(); dup=0; rows_=0; badstatus=collections.Counter()
    mail_acc=0; mail_acc_by=collections.Counter()
    for r in rows(path):
        if r['ballot_req_type']=='MAIL':
            if r['ballot_rtn_status'] in ('ACCEPTED','ACCEPTED - CURED','ACCEPTED - EXCEPTION'):
                try:
                    d=datetime.datetime.strptime(r['ballot_rtn_dt'],'%m/%d/%Y').date()
                except: continue
                if d<=we: mail_acc+=1; mail_acc_by[d]+=1
            continue
        try: d=datetime.datetime.strptime(r['ballot_send_dt'],'%m/%d/%Y').date()
        except: continue
        if not (ws<=d<=we): continue
        rows_+=1
        if r['ballot_rtn_status'] not in ('ACCEPTED','ACCEPTED - CURED','ACCEPTED - EXCEPTION'):
            badstatus[r['ballot_rtn_status']]+=1
        k=r['voter_reg_num']
        if k in seen: dup+=1
        else: seen.add(k)
    print(f"{yr}: window rows={rows_:,} distinct voters={len(seen):,} duplicates={dup:,} "
          f"({100*dup/rows_:.2f}%) | non-accepted={sum(badstatus.values()):,} {badstatus.most_common(4)}")
    print(f"      mail accepted by {we}: {mail_acc:,}")
