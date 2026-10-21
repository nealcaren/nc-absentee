import csv, collections, zipfile, io
os_votes=collections.defaultdict(lambda: collections.Counter())
with open('/Users/nealcaren/Downloads/results_pct_20221108.txt',encoding='utf-8',errors='replace') as f:
    for row in csv.DictReader(f,delimiter='\t'):
        if row['Contest Name'].strip()!='US SENATE': continue
        if 'ABSENT' in row['Precinct'].upper(): continue
        os_votes[row['County'].strip()][row['Choice'].strip()]+=int(row['One Stop'] or 0)
B='BLACK or AFRICAN AMERICAN'; W='WHITE'
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
    rep=os_votes[c]['Ted Budd']; dem=os_votes[c]['Cheri Beasley']
    data.append(dict(c=c,n=tot,xB=r[B]/rt,xW=r[W]/rt,T=rep/(rep+dem)))

def ols(X,y,w=None):
    k=len(X[0]); A=[[0.0]*(k+1) for _ in range(k)]
    for xi,yi,wi in zip(X,y,w or [1.0]*len(y)):
        for i in range(k):
            for j in range(k): A[i][j]+=wi*xi[i]*xi[j]
            A[i][k]+=wi*xi[i]*yi
    for i in range(k):
        p=max(range(i,k),key=lambda r:abs(A[r][i])); A[i],A[p]=A[p],A[i]
        d=A[i][i]
        for j in range(i,k+1): A[i][j]/=d
        for r in range(k):
            if r!=i and A[r][i]:
                f=A[r][i]
                for j in range(i,k+1): A[r][j]-=f*A[i][j]
    return [A[i][k] for i in range(k)]

print("TWO-GROUP: Black vs everyone else (dependent = REP share of One Stop Senate vote)")
for lbl,w in [('unweighted',None),('weighted by county early votes',[d['n'] for d in data])]:
    X=[[1.0,d['xB']] for d in data]; y=[d['T'] for d in data]
    a,b=ols(X,y,w)
    print(f"  {lbl:32} non-Black={a:.3f}  Black={a+b:.3f}")

print("\nSENSITIVITY: exclude counties with >15% 'other/undesignated' race")
sub=[d for d in data if (1-d['xB']-d['xW'])<0.15]
X=[[1.0,d['xB']] for d in sub]; y=[d['T'] for d in sub]
a,b=ols(X,y)
print(f"  n={len(sub)}  non-Black={a:.3f}  Black={a+b:.3f}")

print("\nActual statewide One Stop Senate result: REP 47.3%, DEM 52.7%")
print(f"Black share of One Stop voters: {sum(d['n']*d['xB'] for d in data)/sum(d['n'] for d in data):.3f}")
