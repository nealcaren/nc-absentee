import zipfile, io, csv, collections, datetime

def rows(path):
    z = zipfile.ZipFile(path); name = z.namelist()[0]
    with z.open(name) as fh:
        for row in csv.DictReader(io.TextIOWrapper(fh, encoding='utf-8', errors='replace')):
            yield row

for yr, path in [(2022,'absentee_20221108.zip'),(2024,'absentee_20241105.zip'),(2026,'absentee_20261103.zip')]:
    c=collections.Counter()
    for row in rows(path):
        if row['ballot_req_type']=='MAIL': continue
        c[row['ballot_send_dt']]+=1
    ds=sorted(d for d in c if d.strip())
    print(f"===== {yr}")
    for d in ds[:12]:
        print("   ", d, f"{c[d]:>8,}")
    print("    ...")
    for d in ds[-3:]:
        print("   ", d, f"{c[d]:>8,}")
