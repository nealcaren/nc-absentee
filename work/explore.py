import zipfile, io, csv, collections, sys

def rows(path):
    z = zipfile.ZipFile(path)
    name = z.namelist()[0]
    with z.open(name) as fh:
        f = io.TextIOWrapper(fh, encoding='utf-8', errors='replace')
        r = csv.DictReader(f)
        for row in r:
            yield row

for yr, path in [(2022,'absentee_20221108.zip'),(2024,'absentee_20241105.zip'),(2026,'absentee_20261103.zip')]:
    n=0
    types=collections.Counter(); deliv=collections.Counter(); status=collections.Counter()
    dates=collections.Counter(); siteblank=collections.Counter()
    for row in rows(path):
        n+=1
        t=row['ballot_req_type']; types[t]+=1
        deliv[row['ballot_req_delivery_type']]+=1
        status[row['ballot_rtn_status']]+=1
        dates[row['ballot_req_dt']]+=1
        if not row['site_name'].strip() or row['site_name']==' ':
            siteblank[t]+=1
    print(f"===== {yr}  rows={n:,}")
    print(" req_type   ", types.most_common(10))
    print(" delivery   ", deliv.most_common(10))
    print(" status     ", status.most_common(10))
    print(" date range ", min(d for d in dates if d), "->", max(dates), len(dates),"distinct dates")
    print(" blank site by type", siteblank.most_common(6))
    sys.stdout.flush()
