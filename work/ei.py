import csv, collections, zipfile, io

# --- results: US Senate One Stop votes by county and choice
os_votes=collections.defaultdict(lambda: collections.Counter())
with open('/Users/nealcaren/Downloads/results_pct_20221108.txt',encoding='utf-8',errors='replace') as f:
    for row in csv.DictReader(f,delimiter='\t'):
        if row['Contest Name'].strip()!='US SENATE': continue
        if 'ABSENT' in row['Precinct'].upper(): continue
        c=row['County'].strip(); ch=row['Choice'].strip()
        os_votes[c][ch]+=int(row['One Stop'] or 0)

choices=collections.Counter()
for c,v in os_votes.items():
    for ch,n in v.items(): choices[ch]+=n
print("top Senate choices (One Stop):")
for ch,n in choices.most_common(6): print(f"   {ch:25} {n:>8,}")

# --- absentee: race of One Stop voters by county
B='BLACK or AFRICAN AMERICAN'; W='WHITE'
race=collections.defaultdict(lambda: collections.Counter())
z=zipfile.ZipFile('absentee_20221108.zip')
with z.open(z.namelist()[0]) as fh:
    for row in csv.DictReader(io.TextIOWrapper(fh,encoding='utf-8',errors='replace')):
        if row['ballot_req_type']=='MAIL': continue
        if row['ballot_rtn_status'] not in ('ACCEPTED','ACCEPTED - CURED'): continue
        race[row['county_desc'].strip()][row['race']]+=1

REP=[ch for ch in choices if 'BUDD' in ch.upper()]
DEM=[ch for ch in choices if 'BEASLEY' in ch.upper()]
print("REP choice:",REP," DEM choice:",DEM)

data=[]
for c in sorted(os_votes):
    tot=sum(os_votes[c].values())
    if tot<1000: continue
    r=race[c]; rt=sum(r.values())
    if rt<500: continue
    rep=sum(os_votes[c][ch] for ch in REP)
    dem=sum(os_votes[c][ch] for ch in DEM)
    data.append(dict(c=c,n=tot,
        xB=r[B]/rt, xW=r[W]/rt, xO=1-r[B]/rt-r[W]/rt,
        T=rep/(rep+dem)))
print(f"\ncounties used: {len(data)}")

def ols(X,y):
    k=len(X[0]); A=[[0.0]*(k+1) for _ in range(k)]
    for xi,yi in zip(X,y):
        for i in range(k):
            for j in range(k): A[i][j]+=xi[i]*xi[j]
            A[i][k]+=xi[i]*yi
    for i in range(k):
        p=max(range(i,k),key=lambda r:abs(A[r][i])); A[i],A[p]=A[p],A[i]
        d=A[i][i]
        for j in range(i,k+1): A[i][j]/=d
        for r in range(k):
            if r!=i and A[r][i]:
                f=A[r][i]
                for j in range(i,k+1): A[r][j]-=f*A[i][j]
    return [A[i][k] for i in range(k)]

X=[[1.0,d['xB'],d['xW']] for d in data]; y=[d['T'] for d in data]
a,bB,bW=ols(X,y)
print(f"\nGoodman ecological regression (dependent = REP share of One Stop Senate vote)")
print(f"  intercept (other race): {a:+.3f}")
print(f"  Black  = a+bB = {a+bB:+.3f}")
print(f"  White  = a+bW = {a+bW:+.3f}")
print(f"  coef Black {bB:+.3f} (se n/a), White {bW:+.3f}")
pred=[a+bB*d['xB']+bW*d['xW'] for d in data]
ybar=sum(y)/len(y); ss=sum((v-ybar)**2 for v in y); sr=sum((v-p)**2 for v,p in zip(y,pred))
print(f"  R2 = {1-sr/ss:.3f}")

# reproduce overall
wB=sum(d['n']*d['xB'] for d in data)/sum(d['n'] for d in data)
wW=sum(d['n']*d['xW'] for d in data)/sum(d['n'] for d in data)
wO=1-wB-wW
implied=wB*(a+bB)+wW*(a+bW)+wO*a
actual=sum(d['n']*d['T'] for d in data)/sum(d['n'] for d in data)
print(f"\n  implied statewide REP share = {implied:.3f}   actual = {actual:.3f}")
