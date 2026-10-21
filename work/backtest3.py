import pickle
rows=pickle.load(open('work/panel.pkl','rb'))
for r in rows:
    for y in ('22','24'):
        pd=r[f'T{y}d']-r[f'd{y}']; pr=r[f'T{y}r']-r[f'r{y}']
        r[f's{y}']=pr/(pd+pr) if (pd+pr)>0 else None
ok=[r for r in rows if r['s22'] is not None and r['s24'] is not None]

def ev(tgt,src_year,share_key):
    pd=pr=ad=ar=0.0
    for p in ok:
        bank=p[f'd{tgt}']+p[f'r{tgt}']; final=p[f'T{tgt}d']+p[f'T{tgt}r']
        rem=max(0.0,final-bank)
        s=p[share_key] if share_key!='const' else CONST
        pd+=p[f'd{tgt}']+(1-s)*rem; pr+=p[f'r{tgt}']+s*rem
        ad+=p[f'T{tgt}d']; ar+=p[f'T{tgt}r']
    return 100*(pd-pr)/(pd+pr),100*(ad-ar)/(ad+ar)

P=sum(p['T22d']-p['d22'] for p in ok); Q=sum(p['T22r']-p['r22'] for p in ok)
CONST=Q/(P+Q)
r1=ev('24','22','s22'); r2=ev('24','22','const')
print(f"2024 backtest  precinct shares: pred {r1[0]:+.2f} actual {r1[1]:+.2f} err {r1[0]-r1[1]:+.2f}")
print(f"2024 backtest  constant  s22 : pred {r2[0]:+.2f} actual {r2[1]:+.2f} err {r2[0]-r2[1]:+.2f}")
P=sum(p['T24d']-p['d24'] for p in ok); Q=sum(p['T24r']-p['r24'] for p in ok)
CONST=Q/(P+Q)
r3=ev('22','24','s24'); r4=ev('22','24','const')
print(f"2022 backtest  precinct shares: pred {r3[0]:+.2f} actual {r3[1]:+.2f} err {r3[0]-r3[1]:+.2f}")
print(f"2022 backtest  constant  s24 : pred {r4[0]:+.2f} actual {r4[1]:+.2f} err {r4[0]-r4[1]:+.2f}")
print(f"\nprecinct shares mean abs error {(abs(r1[0]-r1[1])+abs(r3[0]-r3[1]))/2:.2f} vs constant {(abs(r2[0]-r2[1])+abs(r4[0]-r4[1]))/2:.2f}")
