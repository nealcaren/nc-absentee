import pickle, statistics
rows=pickle.load(open('work/panel.pkl','rb'))

for r in rows:
    for y in ('22','24'):
        pd=r[f'T{y}d']-r[f'd{y}']; pr=r[f'T{y}r']-r[f'r{y}']
        r[f'post{y}']=pd+pr
        r[f's{y}']=pr/(pd+pr) if (pd+pr)>0 else None
    r['bank']=r['d26']+r['r26']
    r['tot22']=r['T22d']+r['T22r']; r['tot24']=r['T24d']+r['T24r']

ok=[r for r in rows if r['s22'] is not None and r['s24'] is not None]
print("precincts with both years' post-6 shares:",len(ok))
print("banked early D+R in these:",f"{sum(r['bank'] for r in ok):,}")

ss=[r['s22'] for r in ok]
print(f"\nDistribution of precinct post-day-6 R share (2022):")
print(f"   p10 {statistics.quantiles(ss,n=10)[0]:.2f}  median {statistics.median(ss):.2f}  p90 {statistics.quantiles(ss,n=10)[8]:.2f}")
print(f"   sd {statistics.pstdev(ss):.3f}")

def project(base, share_key, N):
    tot_base=sum(r[base] for r in ok)
    g=N/tot_base
    d=r_=0.0; neg=0
    for p in ok:
        final=p[base]*g
        rem=final-p['bank']
        if rem<0: rem=0; neg+=1
        s=p[share_key] if share_key!='avg' else (p['s22']+p['s24'])/2
        d+=p['d26']+(1-s)*rem
        r_+=p['r26']+s*rem
    return d,r_,neg

print(f"\n{'scenario':38}{'D':>11}{'R':>11}{'D-R':>9}{'neg':>6}")
for N in (2_600_000,2_900_000,3_200_000):
    for base,lbl in [('tot22','base 2022'),('tot24','base 2024')]:
        for sk in ('s22','s24','avg'):
            d,r_,neg=project(base,sk,N)
            print(f"N={N/1e6:.1f}M {lbl} s={sk:4}          {d:>11,.0f}{r_:>11,.0f}{100*(d-r_)/(d+r_):>+9.1f}{neg:>6}")
