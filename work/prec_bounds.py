import csv, collections, zipfile, io, re
def norm(s): return re.sub(r'[^A-Z0-9]','',s.upper())

# results: One Stop Senate votes by county+precinct
res=collections.defaultdict(lambda: collections.Counter())
with open('/Users/nealcaren/Downloads/results_pct_20221108.txt',encoding='utf-8',errors='replace') as f:
    for row in csv.DictReader(f,delimiter='\t'):
        if row['Contest Name'].strip()!='US SENATE': continue
        p=row['Precinct'].strip()
        if 'ABSENT' in p.upper() or p.upper().startswith('OS'): continue
        res[(row['County'].strip(),norm(p))][row['Choice'].strip()]+=int(row['One Stop'] or 0)

B='BLACK or AFRICAN AMERICAN'
absn=collections.defaultdict(lambda: collections.Counter())
z=zipfile.ZipFile('absentee_20221108.zip')
with z.open(z.namelist()[0]) as fh:
    for row in csv.DictReader(io.TextIOWrapper(fh,encoding='utf-8',errors='replace')):
        if row['ballot_req_type']=='MAIL': continue
        if row['ballot_rtn_status'] not in ('ACCEPTED','ACCEPTED - CURED'): continue
        absn[(row['county_desc'].strip(),norm(row['precinct_desc'].strip()))][row['race']]+=1

rows=[]
for k,v in res.items():
    rep=v.get('Ted Budd',0); dem=v.get('Cheri Beasley',0); tot=rep+dem
    a=absn.get(k)
    if not a or tot<50: continue
    rt=sum(a.values())
    if rt<30: continue
    X=a[B]/rt; T=rep/tot
    if X<=0 or X>=1: continue
    lo=max(0.0,(T-(1-X))/X); hi=min(1.0,T/X)
    rows.append((k[0],k[1],X,T,lo,hi,a[B]))
print(f"matched precincts usable: {len(rows)}  across {len({r[0] for r in rows})} counties")
W=sum(r[6] for r in rows)
print(f"Black One Stop voters in these precincts: {W:,.0f}")
print(f"weighted bounds: [{sum(r[4]*r[6] for r in rows)/W:.3f}, {sum(r[5]*r[6] for r in rows)/W:.3f}]")
w=sorted(r[5]-r[4] for r in rows)
print(f"median precinct bound width: {w[len(w)//2]:.3f}  (county-level was 1.000)")
print(f"precincts width<0.5: {sum(1 for x in w if x<0.5)}/{len(w)}")
