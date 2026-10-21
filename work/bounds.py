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

rows=[]
for c in sorted(os_votes):
    tot=sum(os_votes[c].values()); r=race[c]; rt=sum(r.values())
    if tot<1000 or rt<500: continue
    X=r[B]/rt
    T=os_votes[c]['Ted Budd']/(os_votes[c]['Ted Budd']+os_votes[c]['Cheri Beasley'])
    if X<=0 or X>=1: continue
    lo=max(0.0,(T-(1-X))/X); hi=min(1.0,T/X)
    rows.append((c,X,T,lo,hi,r[B]))

W=sum(x[5] for x in rows)
agg_lo=sum(x[3]*x[5] for x in rows)/W
agg_hi=sum(x[4]*x[5] for x in rows)/W
print(f"counties: {len(rows)}   Black One Stop voters: {W:,.0f}")
print(f"\nKing deterministic bounds on Black Republican share (weighted by Black voters):")
print(f"   [{agg_lo:.3f}, {agg_hi:.3f}]   width={agg_hi-agg_lo:.3f}")
print(f"\nunweighted mean of county bounds: [{sum(x[3] for x in rows)/len(rows):.3f}, {sum(x[4] for x in rows)/len(rows):.3f}]")
print(f"\ncounties where bounds are uninformative (width>0.8): {sum(1 for x in rows if x[4]-x[3]>0.8)}/{len(rows)}")
print(f"median county bound width: {sorted(x[4]-x[3] for x in rows)[len(rows)//2]:.3f}")

print("\nwidest and tightest county bounds:")
for x in sorted(rows,key=lambda x:-(x[4]-x[3]))[:3]:
    print(f"   {x[0]:15} X={x[1]:.3f} T={x[2]:.3f}  [{x[3]:.2f},{x[4]:.2f}]")
for x in sorted(rows,key=lambda x:(x[4]-x[3]))[:3]:
    print(f"   {x[0]:15} X={x[1]:.3f} T={x[2]:.3f}  [{x[3]:.2f},{x[4]:.2f}]")

print("\nSame bounds if we only use the 20 largest counties:")
big=sorted(rows,key=lambda x:-x[5])[:20]
W2=sum(x[5] for x in big)
print(f"   [{sum(x[3]*x[5] for x in big)/W2:.3f}, {sum(x[4]*x[5] for x in big)/W2:.3f}]")
