import zipfile, io, csv, collections, datetime, pickle, json

FILES={2022:('absentee_20221108.zip',datetime.date(2022,11,8)),
       2024:('absentee_20241105.zip',datetime.date(2024,11,5)),
       2026:('absentee_20261103.zip',datetime.date(2026,11,3))}
ACC={'ACCEPTED','ACCEPTED - CURED','ACCEPTED - EXCEPTION'}

out={}
for yr,(path,ed) in FILES.items():
    party=collections.Counter(); race=collections.Counter(); cty=collections.Counter()
    total=collections.Counter()
    z=zipfile.ZipFile(path)
    with z.open(z.namelist()[0]) as fh:
        for row in csv.DictReader(io.TextIOWrapper(fh,encoding='utf-8',errors='replace')):
            if row['ballot_req_type']=='MAIL': continue
            if row['ballot_rtn_status'] not in ACC: continue
            ds=row['ballot_send_dt'].strip()
            try: d=datetime.datetime.strptime(ds,'%m/%d/%Y').date()
            except: continue
            t=(ed-d).days
            if t<3 or t>19: continue
            total[d]+=1
            party[(t,row['voter_party_code'])]+=1
            race[(t,row['race'])]+=1
            cty[(d,row['county_desc'].strip())]+=1
    out[yr]=dict(total=dict(total),party={f"{t}|{p}":v for (t,p),v in party.items()},
                 race={f"{t}|{r}":v for (t,r),v in race.items()},
                 cty={f"{d}|{c}":v for (d,c),v in cty.items()},
                 election=str(ed))
    ds=sorted(total)
    print(f"{yr}: {sum(total.values()):,} in-person early votes, {len(total)} days, {ds[0]} .. {ds[-1]}, t {min((ed-d).days for d in ds)}..{max((ed-d).days for d in ds)}",flush=True)
pickle.dump(out,open('work/daily.pkl','wb'))

# tidy CSV: year, date, dow, t, total, D, R, U, other
rows=[]
for yr,d in out.items():
    ed=datetime.date.fromisoformat(d['election'])
    for dt,n in sorted(d['total'].items()):
        ds=dt.isoformat()
        g=lambda p: d['party'].get(f"{(ed-dt).days}|{p}",0)
        rows.append(dict(year=yr,date=ds,dow=dt.strftime('%a'),t=(ed-dt).days,
                         total=n,dem=g('DEM'),rep=g('REP'),una=g('UNA'),lib=g('LIB'),other=n-g('DEM')-g('REP')-g('UNA')-g('LIB')))
with open('analysis/daily_early.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print("wrote analysis/daily_early.csv",len(rows),"rows")
