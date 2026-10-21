import zipfile, io, csv, collections
z=zipfile.ZipFile('absentee_20221108.zip')
with z.open(z.namelist()[0]) as fh:
    r=csv.DictReader(io.TextIOWrapper(fh,encoding='utf-8',errors='replace'))
    byv=collections.defaultdict(list)
    for i,row in enumerate(r):
        if row['ballot_req_type']=='MAIL': continue
        byv[row['voter_reg_num']].append(row)
        if len(byv)>200000: break
dups=[v for v in byv.values() if len(v)>1]
print("voters seen:",len(byv),"with >1 row:",len(dups))
for v in dups[:3]:
    print("\n--- voter", v[0]['voter_reg_num'], v[0]['voter_last_name'])
    for row in v:
        print("   ", {k:row[k] for k in ('county_desc','precinct_desc','ballot_req_type','ballot_send_dt','ballot_rtn_status','site_name','sdr')})
# distribution of counts
c=collections.Counter(len(v) for v in byv.values())
print("\nrows-per-voter distribution:",c.most_common(8))
print("distinct election_dt:", set(row['election_dt'] for v in dups[:50] for row in v))
