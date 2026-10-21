import csv, collections, zipfile, io

os_by_cty=collections.Counter(); tot_by_cty=collections.Counter()
with open('/Users/nealcaren/Downloads/results_pct_20221108.txt',encoding='utf-8',errors='replace') as f:
    for row in csv.DictReader(f,delimiter='\t'):
        if row['Contest Name'].strip()!='US SENATE': continue
        c=row['County'].strip()
        if 'ABSENT' in row['Precinct'].upper(): continue
        os_by_cty[c]+=int(row['One Stop'] or 0)
        tot_by_cty[c]+=int(row['Total Votes'] or 0)

abs_cty=collections.Counter()
z=zipfile.ZipFile('absentee_20221108.zip')
with z.open(z.namelist()[0]) as fh:
    for row in csv.DictReader(io.TextIOWrapper(fh,encoding='utf-8',errors='replace')):
        if row['ballot_req_type']=='MAIL': continue
        if row['ballot_rtn_status'] not in ('ACCEPTED','ACCEPTED - CURED'): continue
        abs_cty[row['county_desc'].strip()]+=1

print(f"statewide: results OneStop={sum(os_by_cty.values()):,}  absentee accepted in-person={sum(abs_cty.values()):,}")
diffs=[]
for c in sorted(os_by_cty):
    a=os_by_cty[c]; b=abs_cty.get(c,0)
    diffs.append((abs(a-b), c, a, b, 100*(b-a)/a if a else 0))
print(f"counties compared: {len(diffs)}")
print(f"median abs % diff: {sorted(d[4] if d[4]>0 else -d[4] for d in diffs)[len(diffs)//2]:.3f}%")
print("\nlargest discrepancies:")
for d in sorted(diffs,reverse=True)[:6]:
    print(f"  {d[1]:15} results={d[2]:>8,} absentee={d[3]:>8,} diff={d[4]:+.2f}%")
print("\nclosest 4:")
for d in sorted(diffs)[:4]:
    print(f"  {d[1]:15} results={d[2]:>8,} absentee={d[3]:>8,} diff={d[4]:+.2f}%")
