#!/usr/bin/env python3
"""Refresh 2026 daily early-vote counts and score them against the two projections.

    python3 work/update_daily.py            # use the local zip
    python3 work/update_daily.py --download  # fetch the newest file from NCSBE first
"""
import zipfile, io, csv, collections, datetime, pickle, subprocess, sys, os

ZIP='absentee_20261103.zip'
URL='https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2026_11_03/absentee_20261103.zip'
ACC={'ACCEPTED','ACCEPTED - CURED','ACCEPTED - EXCEPTION'}
ED=datetime.date(2026,11,3)

if '--download' in sys.argv:
    before=os.path.getsize(ZIP) if os.path.exists(ZIP) else 0
    subprocess.run(['curl','-sL','-o',ZIP,URL],check=True)
    after=os.path.getsize(ZIP)
    print(f"downloaded {ZIP}: {after:,} bytes ({'changed' if after!=before else 'unchanged'})")

def parse2026():
    party=collections.Counter(); total=collections.Counter()
    z=zipfile.ZipFile(ZIP)
    with z.open(z.namelist()[0]) as fh:
        for row in csv.DictReader(io.TextIOWrapper(fh,encoding='utf-8',errors='replace')):
            if row['ballot_req_type']=='MAIL': continue
            if row['ballot_rtn_status'] not in ACC: continue
            try: d=datetime.datetime.strptime(row['ballot_send_dt'].strip(),'%m/%d/%Y').date()
            except: continue
            t=(ED-d).days
            if t<3 or t>19: continue
            total[d]+=1; party[(t,row['voter_party_code'])]+=1
    return dict(total=dict(total),party={f"{t}|{p}":v for (t,p),v in party.items()},
                race={},cty={},election=str(ED))

D=pickle.load(open('work/daily.pkl','rb'))
fresh=parse2026()
D[2026]=fresh
pickle.dump(D,open('work/daily.pkl','wb'))

def dayk(y,p=None):
    ed=datetime.date.fromisoformat(D[y]['election']); s=collections.Counter()
    for dt,n in D[y]['total'].items():
        k=(dt-(ed-datetime.timedelta(days=19))).days+1
        if 1<=k<=17: s[k]+= n if p is None else D[y]['party'].get(f"{(ed-dt).days}|{p}",0)
    return s

T22,T26=dayk(2022),dayk(2026)
last=max([k for k in range(1,18) if T26.get(k)])
obs=sum(T26[k] for k in range(1,last+1)); base=sum(T22[k] for k in range(1,last+1))
scale=obs/base
A=sum(T22.values())*scale
B=obs+sum(T22[k] for k in range(last+1,18))

print(f"\n2026 data through {max(fresh['total'])}  (day {last} of 17)")
print(f"banked {obs:,} in-person early votes")
print(f"cumulative 2026 / 2022 scale: {scale:.2f}x  (was 1.46x at day 6)\n")
print(f"{'day':>4}{'date':>12}{'dow':>5}{'actual':>10}{'A prop':>10}{'B revert':>10}{'act/A':>8}{'act/B':>8}")
for k in range(1,last+1):
    dt=ED-datetime.timedelta(days=20-k)
    a=T22[k]*scale; b=T22[k]
    print(f"{k:>4}{dt.isoformat():>12}{dt.strftime('%a'):>5}{T26[k]:>10,}{a:>10,.0f}{b:>10,.0f}"
          f"{T26[k]/a if a else 0:>8.2f}{T26[k]/b if b else 0:>8.2f}")

print(f"\nprojected total in-person early:  A {A:,.0f}   B {B:,.0f}")
for p in ('DEM','REP','UNA'):
    o=sum(dayk(2026,p)[k] for k in range(1,last+1)); b2=sum(dayk(2022,p)[k] for k in range(1,last+1))
    s=o/b2 if b2 else 0
    print(f"   {p}: banked {o:>9,}  scale {s:>5.2f}x  path A total {sum(dayk(2022,p).values())*s:>10,.0f}  "
          f"path B total {o+sum(dayk(2022,p)[k] for k in range(last+1,18)):>10,.0f}")
print(f"\n{'day':>4}{'date':>8}  {'D act':>8}{'D A':>8}{'D B':>8}  {'R act':>8}{'R A':>8}{'R B':>8}")
for k in range(1,last+1):
    dt=ED-datetime.timedelta(days=20-k)
    da,ra=dayk(2026,'DEM')[k],dayk(2026,'REP')[k]
    a22,r22=dayk(2022,'DEM')[k],dayk(2022,'REP')[k]
    sd=sum(dayk(2026,'DEM')[i] for i in range(1,last+1))/sum(dayk(2022,'DEM')[i] for i in range(1,last+1))
    sr=sum(dayk(2026,'REP')[i] for i in range(1,last+1))/sum(dayk(2022,'REP')[i] for i in range(1,last+1))
    print(f"{k:>4}{dt.strftime('%b %d'):>8}  {da:>8,}{a22*sd:>8,.0f}{a22:>8,}  {ra:>8,}{r22*sr:>8,.0f}{r22:>8,}")

print("\nRead: act/A >> 1 means the surge is persisting (high path); act/B >> 1 means front-loaded only.")
print("      Watch the D and R rows separately: falling D with flat R means Democrats moved votes earlier.")
