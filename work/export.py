import pickle, collections, csv, statistics
E=pickle.load(open('work/prec_party.pkl','rb'))
rows=pickle.load(open('work/panel.pkl','rb'))
for r in rows:
    for y in ('22','24'):
        pd=r[f'T{y}d']-r[f'd{y}']; pr=r[f'T{y}r']-r[f'r{y}']
        r[f's{y}']=pr/(pd+pr) if (pd+pr)>0 else None
    r['tot22']=r['T22d']+r['T22r']; r['tot24']=r['T24d']+r['T24r']
    r['bank']=r['d26']+r['r26']
ok=[r for r in rows if r['s22'] is not None and r['s24'] is not None]

def cty_shares(yr):
    agg=collections.defaultdict(lambda:[0.0,0.0])
    for p in ok:
        agg[p['c'][0]][0]+=p[f'T{yr}d']-p[f'd{yr}']
        agg[p['c'][0]][1]+=p[f'T{yr}r']-p[f'r{yr}']
    return {k:v[1]/(v[0]+v[1]) for k,v in agg.items() if v[0]+v[1]>0}
S22,S24=cty_shares('22'),cty_shares('24')

# county-level projection at N=2.9M
N=2_900_000
tot22=sum(r['tot22'] for r in ok); g=N/tot22
cty=collections.defaultdict(lambda: dict(bank_d=0,bank_r=0,base=0))
for r in ok:
    c=r['c'][0]
    cty[c]['bank_d']+=r['d26']; cty[c]['bank_r']+=r['r26']; cty[c]['base']+=r['tot22']
out=[]
for c,v in cty.items():
    s=(S22.get(c,0.51)+S24.get(c,0.51))/2
    rem=max(0.0,v['base']*g-v['bank_d']-v['bank_r'])
    D=v['bank_d']+(1-s)*rem; R=v['bank_r']+s*rem
    out.append(dict(county=c,banked_dem=v['bank_d'],banked_rep=v['bank_r'],
        post6_rep_share=round(s,3),
        proj_dem=round(D),proj_rep=round(R),
        proj_dem_margin=round(100*(D-R)/(D+R),2)))
out.sort(key=lambda r:r['proj_dem_margin'])
with open('analysis/county_projection.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
print("wrote analysis/county_projection.csv",len(out),"counties")
print("most Republican-projected counties:",[(r['county'],r['proj_dem_margin']) for r in out[:5]])
print("most Democratic-projected:",[(r['county'],r['proj_dem_margin']) for r in out[-5:]])

# precinct file
with open('analysis/precinct_panel.csv','w',newline='') as f:
    w=csv.writer(f)
    w.writerow(['county','precinct','early_dem_2022','early_rep_2022','early_dem_2024','early_rep_2024',
                'early_dem_2026','early_rep_2026','total_dem_2022','total_rep_2022','total_dem_2024','total_rep_2024',
                'post6_rep_share_2022','post6_rep_share_2024'])
    for r in ok:
        w.writerow([r['c'][0],r['c'][1],r['d22'],r['r22'],r['d24'],r['r24'],r['d26'],r['r26'],
                    r['T22d'],r['T22r'],r['T24d'],r['T24r'],
                    round(r['s22'],4),round(r['s24'],4)])
print("wrote analysis/precinct_panel.csv",len(ok),"precincts")
