import pickle, statistics
rows=pickle.load(open('work/panel.pkl','rb'))
for r in rows:
    for y in ('22','24'):
        pd=r[f'T{y}d']-r[f'd{y}']; pr=r[f'T{y}r']-r[f'r{y}']
        r[f's{y}']=pr/(pd+pr) if (pd+pr)>0 else None
ok=[r for r in rows if r['s22'] is not None and r['s24'] is not None]

def run(target, source_share):
    """predict target year's D total using source year's precinct post-6 R shares"""
    predD=actD=predR=actR=0.0
    for p in ok:
        bank=p[f'd{target}']+p[f'r{target}']
        final=p[f'T{target}d']+p[f'T{target}r']
        rem=max(0.0,final-bank)
        s=p[source_share]
        predD+=p[f'd{target}']+(1-s)*rem
        predR+=p[f'r{target}']+s*rem
        actD+=p[f'T{target}d']; actR+=p[f'T{target}r']
    return predD,predR,actD,actR

print("BACKTEST: predict year Y using the OTHER year's precinct post-day-6 shares")
for tgt,src,lbl in [('24','s22','2024 using 2022 shares'),('22','s24','2022 using 2024 shares')]:
    pd,pr,ad,ar=run(tgt,src)
    print(f"  {lbl:28} predicted D-R {100*(pd-pr)/(pd+pr):+6.2f}   actual {100*(ad-ar)/(ad+ar):+6.2f}   "
          f"error {100*(pd-pr)/(pd+pr)-100*(ad-ar)/(ad+ar):+6.2f}")

print("\nSame, using the statewide constant R share instead of precinct shares:")
for tgt,src,lbl in [('24','s22','2024 using 2022 constant'),('22','s24','2022 using 2024 constant')]:
    P=sum(p[f'T{src}d']-p[f'd{src}'] for p in ok); Q=sum(p[f'T{src}r']-p[f'r{src}'] for p in ok)
    s=Q/(P+Q)
    pd=pr=ad=ar=0.0
    for p in ok:
        bank=p[f'd{target}']+p[f'r{target}']; final=p[f'T{target}d']+p[f'T{target}r']
        rem=max(0.0,final-bank)
        pd+=p[f'd{target}']+(1-s)*rem; pr+=p[f'r{target}']+s*rem
        ad+=p[f'T{target}d']; ar+=p[f'T{target}r']
    print(f"  {lbl:28} predicted D-R {100*(pd-pr)/(pd+pr):+6.2f}   actual {100*(ad-ar)/(ad+ar):+6.2f}   "
          f"error {100*(pd-pr)/(pd+pr)-100*(ad-ar)/(ad+ar):+6.2f}")
