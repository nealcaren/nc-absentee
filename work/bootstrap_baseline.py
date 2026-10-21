#!/usr/bin/env python3
"""One-time: turn the 2022 and 2024 absentee archives into a small baseline file.

The full archives are ~300MB; the site only needs daily counts by party, which
is a few kilobytes. Run this locally once, commit data/baseline.json, and the
daily CI job never has to touch the old files again.
"""
import zipfile, io, csv, collections, datetime, json, sys

FILES = {
    2022: ('absentee_20221108.zip', datetime.date(2022, 11, 8)),
    2024: ('absentee_20241105.zip', datetime.date(2024, 11, 5)),
}
ACC = {'ACCEPTED', 'ACCEPTED - CURED', 'ACCEPTED - EXCEPTION'}
PARTS = ['DEM', 'REP', 'UNA', 'LIB']


def collect(path, election):
    days = collections.defaultdict(lambda: collections.Counter())
    z = zipfile.ZipFile(path)
    with z.open(z.namelist()[0]) as fh:
        for row in csv.DictReader(io.TextIOWrapper(fh, encoding='utf-8', errors='replace')):
            if row['ballot_req_type'] == 'MAIL':
                continue
            if row['ballot_rtn_status'] not in ACC:
                continue
            try:
                d = datetime.datetime.strptime(row['ballot_send_dt'].strip(), '%m/%d/%Y').date()
            except ValueError:
                continue
            t = (election - d).days
            if not 3 <= t <= 19:
                continue
            k = 20 - t
            days[k]['total'] += 1
            p = row['voter_party_code']
            days[k][p if p in PARTS else 'OTH'] += 1
    return {str(k): {p: int(days[k][p]) for p in PARTS + ['OTH', 'total']} for k in range(1, 18)}


out = {'election': {str(y): str(e) for y, (_, e) in FILES.items()}, 'days': {}}
for y, (path, election) in FILES.items():
    out['days'][str(y)] = collect(path, election)
    tot = sum(v['total'] for v in out['days'][str(y)].values())
    print(f"{y}: {tot:,} in-person early votes over {len(out['days'][str(y)])} days", flush=True)

with open('data/baseline.json', 'w') as f:
    json.dump(out, f, separators=(',', ':'))
print("wrote data/baseline.json")
