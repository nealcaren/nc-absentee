#!/usr/bin/env python3
"""Download the newest 2026 absentee file and record daily in-person early votes.

Writes data/observed.json. Safe to run repeatedly; each run replaces the file
with the full history contained in the current archive, so a missed day heals
itself on the next run.

    python3 work/ingest.py                 # download from NCSBE
    python3 work/ingest.py --zip local.zip # use a local copy
"""
import zipfile, io, csv, collections, datetime, json, sys, os, urllib.request

URL = 'https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2026_11_03/absentee_20261103.zip'
ELECTION = datetime.date(2026, 11, 3)
ACC = {'ACCEPTED', 'ACCEPTED - CURED', 'ACCEPTED - EXCEPTION'}
PARTS = ['DEM', 'REP', 'UNA', 'LIB']
CACHE = 'data/2026_absentee.zip'


def fetch():
    if '--zip' in sys.argv:
        return sys.argv[sys.argv.index('--zip') + 1]
    os.makedirs('data', exist_ok=True)
    req = urllib.request.Request(URL, headers={'User-Agent': 'nc-absentee-tracker/1.0'})
    with urllib.request.urlopen(req, timeout=300) as r, open(CACHE, 'wb') as f:
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)
    print(f"downloaded {os.path.getsize(CACHE):,} bytes")
    return CACHE


def main():
    path = fetch()
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
            t = (ELECTION - d).days
            if not 3 <= t <= 19:
                continue
            k = 20 - t
            days[k]['total'] += 1
            p = row['voter_party_code']
            days[k][p if p in PARTS else 'OTH'] += 1

    out = {
        'election': str(ELECTION),
        'through': str(max(ELECTION - datetime.timedelta(days=20 - k) for k in days)),
        'last_day': max(days),
        'days': {str(k): {p: int(days[k][p]) for p in PARTS + ['OTH', 'total']} for k in sorted(days)},
    }
    with open('data/observed.json', 'w') as f:
        json.dump(out, f, indent=1)
    print(f"day {out['last_day']} of 17, {sum(v['total'] for v in out['days'].values()):,} banked, through {out['through']}")
    print("wrote data/observed.json")


if __name__ == '__main__':
    main()
