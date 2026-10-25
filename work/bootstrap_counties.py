#!/usr/bin/env python3
"""One-time: 2022 county inputs for the unaffiliated-geography section.

Writes data/county_baseline.json with, for each county,
  days:   in-person early voters by day (1-17) and party
  result: One Stop votes for US Senate, Republican and Democratic
The archives stay out of the repo; this file is ~100KB.

    python3 work/bootstrap_counties.py [path/to/results_pct_20221108.zip]
"""
import zipfile, io, csv, collections, datetime, json, sys, os

ABSENTEE = 'absentee_20221108.zip'
RESULTS = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser('~/Downloads/results_pct_20221108.zip')
ELECTION = datetime.date(2022, 11, 8)
ACC = {'ACCEPTED', 'ACCEPTED - CURED', 'ACCEPTED - EXCEPTION'}
GROUPS = ['DEM', 'REP', 'UNA']

days = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
z = zipfile.ZipFile(ABSENTEE)
with z.open(z.namelist()[0]) as fh:
    for row in csv.DictReader(io.TextIOWrapper(fh, encoding='utf-8', errors='replace')):
        if row['ballot_req_type'] == 'MAIL' or row['ballot_rtn_status'] not in ACC:
            continue
        try:
            d = datetime.datetime.strptime(row['ballot_send_dt'].strip(), '%m/%d/%Y').date()
        except ValueError:
            continue
        t = (ELECTION - d).days
        if not 3 <= t <= 19:
            continue
        p = row['voter_party_code']
        days[row['county_desc'].strip()][20 - t][p if p in GROUPS else 'OTH'] += 1

result = collections.defaultdict(collections.Counter)
z = zipfile.ZipFile(RESULTS)
with z.open(z.namelist()[0]) as fh:
    for row in csv.DictReader(io.TextIOWrapper(fh, encoding='utf-8', errors='replace'), delimiter='\t'):
        if row['Contest Name'].strip() != 'US SENATE':
            continue
        side = {'REP': 'R', 'DEM': 'D'}.get(row['Choice Party'].strip())
        if side:
            result[row['County'].strip()][side] += int(row['One Stop'] or 0)

out = {'year': 2022, 'contest': 'US SENATE', 'counties': {
    c: {'days': {str(k): dict(days[c][k]) for k in sorted(days[c])}, 'result': dict(result[c])}
    for c in sorted(days) if c in result}}
with open('data/county_baseline.json', 'w') as f:
    json.dump(out, f, separators=(',', ':'))
print(f"wrote data/county_baseline.json: {len(out['counties'])} counties")
