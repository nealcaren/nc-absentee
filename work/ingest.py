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
LAST_MODIFIED = None


def remote_modified():
    """Last-Modified of the archive, or None if the HEAD request fails."""
    try:
        req = urllib.request.Request(URL, method='HEAD', headers={'User-Agent': 'nc-absentee-tracker/1.0'})
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.headers.get('Last-Modified')
    except Exception as e:
        print(f"HEAD check failed ({e}); will download anyway")
        return None


def previous_stamp():
    try:
        return json.load(open('data/observed.json')).get('source_last_modified')
    except Exception:
        return None


def fetch():
    if '--zip' in sys.argv:
        return sys.argv[sys.argv.index('--zip') + 1]
    os.makedirs('data', exist_ok=True)

    # Polling every two hours: skip the 48MB download when the archive has not
    # been re-posted since the last run.
    global LAST_MODIFIED
    lm = remote_modified()
    LAST_MODIFIED = lm
    if lm and lm == previous_stamp() and '--force' not in sys.argv:
        print(f"no new file: S3 Last-Modified is still {lm}")
        sys.exit(0)

    req = urllib.request.Request(URL, headers={'User-Agent': 'nc-absentee-tracker/1.0'})
    with urllib.request.urlopen(req, timeout=300) as r, open(CACHE, 'wb') as f:
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)
    print(f"downloaded {os.path.getsize(CACHE):,} bytes (Last-Modified {lm})")
    return CACHE


def main():
    path = fetch()
    days = collections.defaultdict(lambda: collections.Counter())
    counties = collections.defaultdict(lambda: collections.Counter())
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
            counties[row['county_desc'].strip()][p if p in ('DEM', 'REP', 'UNA') else 'OTH'] += 1

    out = {
        'election': str(ELECTION),
        'source_last_modified': LAST_MODIFIED,
        'through': str(max(ELECTION - datetime.timedelta(days=20 - k) for k in days)),
        'last_day': max(days),
        'days': {str(k): {p: int(days[k][p]) for p in PARTS + ['OTH', 'total']} for k in sorted(days)},
        # cumulative in-person early voters by county and party, for the geography section
        'counties': {c: dict(counties[c]) for c in sorted(counties)},
    }
    with open('data/observed.json', 'w') as f:
        json.dump(out, f, indent=1)
    print(f"day {out['last_day']} of 17, {sum(v['total'] for v in out['days'].values()):,} banked, through {out['through']}")
    print("wrote data/observed.json")


if __name__ == '__main__':
    main()
