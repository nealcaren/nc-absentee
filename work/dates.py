import zipfile, io, csv, collections

def rows(path):
    z = zipfile.ZipFile(path); name = z.namelist()[0]
    with z.open(name) as fh:
        for row in csv.DictReader(io.TextIOWrapper(fh, encoding='utf-8', errors='replace')):
            yield row

for yr, path in [(2022,'absentee_20221108.zip'),(2024,'absentee_20241105.zip'),(2026,'absentee_20261103.zip')]:
    req=collections.Counter(); send=collections.Counter(); rtn=collections.Counter(); mism=0; n=0
    for row in rows(path):
        if row['ballot_req_type']=='MAIL': continue
        n+=1
        req[row['ballot_req_dt']]+=1; send[row['ballot_send_dt']]+=1; rtn[row['ballot_rtn_dt']]+=1
        if row['ballot_req_dt']!=row['ballot_send_dt'] or row['ballot_send_dt']!=row['ballot_rtn_dt']: mism+=1
    print(f"===== {yr} in-person n={n:,}  rows where req!=send!=rtn: {mism:,}")
    for label,c in [('req',req),('send',send),('rtn',rtn)]:
        ds=sorted(d for d in c if d.strip())
        print(f"  {label}: {ds[0]} .. {ds[-1]} | top:", c.most_common(4))
