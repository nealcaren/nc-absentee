import csv, collections, zipfile, io
os_votes=collections.defaultdict(lambda: collections.Counter())
with open('/Users/nealcaren/Downloads/results_pct_20221108.txt',encoding='utf-8',errors='replace') as f:
    for row in csv.DictReader(f,delimiter='\t'):
        if row['Contest Name'].strip()!='US SENATE': continue
        if 'ABSENT' in row['Precinct'].upper(): continue
        os_votes[row['County'].strip()][row['Choice'].strip()]+=int(row['One Stop'] or 0)
B='BLACK or AFRICAN AMERICAN'
race=collections.defaultdict(lambda: collections.Counter())
z=zipfile.ZipFile('absentee_20221108.zip')
with z.open(z.namelist()[0]) as fh:
    for row in csv.DictReader(io.TextIOWrapper(fh,encoding='utf-8',errors='replace')):
        if row['ballot_req_type']=='MAIL': continue
        if row['ballot_rtn_status'] not in ('ACCEPTED','ACCEPTED - CURED'): continue
        race[row['county_desc'].strip()][row['race']]+=1

data=[]
for c in sorted(os_votes):
    tot=sum(os_votes[c].values()); r=race[c]; rt=sum(r.values())
    if tot<1000 or rt<500: continue
    data.append(dict(n=tot,xB=r[B]/rt,T=os_votes[c]['Ted Budd']/(os_votes[c]['Ted Budd']+os_votes[c]['Cheri Beasley'])))

def sse(a,b,w):
    return sum(wi*(d['T']-a-b*d['xB'])**2 for d,wi in zip(data,w))

best=None
for wlbl,w in [('unweighted',[1.0]*len(data)),('weighted',[d['n'] for d in data])]:
    best=None
    for ai in range(0,101):
        a=ai/100
        for bi in range(0,101):
            b=bi/100
            if a+b>1: continue
            s=sse(a,b,w)
            if best is None or s<best[0]: best=(s,a,b)
    s,a,b=best
    print(f"{wlbl:11} constrained: non-Black={a:.2f}  Black={a+b:.2f}   (Black REP share {a+b:.2f})")
    wB=sum(d['n']*d['xB'] for d in data)/sum(d['n'] for d in data)
    print(f"            implied statewide REP={wB*(a+b)+(1-wB)*a:.3f}  actual=0.473")
