import pickle, statistics, collections
rows=pickle.load(open('work/panel.pkl','rb'))
for r in rows:
    for y in ('22','24'):
        pd=r[f'T{y}d']-r[f'd{y}']; pr=r[f'T{y}r']-r[f'r{y}']
        r[f's{y}']=pr/(pd+pr) if (pd+pr)>0 else None
        r[f'w{y}']=pd+pr
ok=[r for r in rows if r['s22'] is not None and r['s24'] is not None]

# county-level shares per year
def county_shares(src):
    agg=collections.defaultdict(lambda:[0.0,0.0])
    for p in ok:
        agg[p['c'][0]][0]+=p[f'T{src}d']-p[f'd{src}']
        agg[p['c'][0]][1]+=p[f'T{src}r']-p[f'r{src}']
    return {k: v[1]/(v[0]+v[1]) for k,v in agg.items()}

def ev(tgt,sharefn):
    pd=pr=ad=ar=0.0
    for p in ok:
        bank=p[f'd{tgt}']+p[f'r{tgt}']; final=p[f'T{tgt}d']+p[f'T{tgt}r']
        rem=max(0.0,final-bank); s=sharefn(p)
        pd+=p[f'd{tgt}']+(1-s)*rem; pr+=p[f'r{tgt}']+s*rem
        ad+=p[f'T{tgt}d']; ar+=p[f'T{tgt}r']
    return 100*(pd-pr)/(pd+pr),100*(ad-ar)/(ad+ar)

for tgt,src in [('24','22'),('22','24')]:
    cs=county_shares(src)
    glob=sum(p[f'T{src}r']-p[f'r{src}'] for p in ok)/sum(p[f'T{src}d']-p[f'd{src}']+p[f'T{src}r']-p[f'r{src}'] for p in ok)
    res={}
    res['state constant']=ev(tgt,lambda p,s=glob: s)
    res['county constant']=ev(tgt,lambda p,cs=cs: cs.get(p['c'][0],glob))
    res['precinct']=ev(tgt,lambda p,y=src: p[f's{y}'])
    # shrinkage toward state: weight k
    for k in (5,20,100,500):
        def shr(p,y=src,g=glob,k=k):
            w=p[f'w{y}']
            return (p[f's{y}']*w+g*k)/(w+k)
        res[f'shrink k={k}']=ev(tgt,lambda p,f=shr: f(p))
    print(f"\n=== predicting {tgt} with {src} data")
    for lbl,(pred,act) in res.items():
        print(f"   {lbl:18} pred {pred:+6.2f}  actual {act:+6.2f}  err {pred-act:+6.2f}")
