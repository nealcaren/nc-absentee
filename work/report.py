import pickle, csv, statistics
d=pickle.load(open('work/agg2.pkl','rb'))
B='BLACK or AFRICAN AMERICAN'
def ns(yr,c): return sum(1 for k in d[yr]['site'] if k[0]==c)
rows=[]
for c in sorted(d[2022]['county']):
    a=d[2022]['county'][c]; b=d[2024]['county'].get(c,{'win':0,'race':{},'party':{}}); e=d[2026]['county'][c]
    rows.append(dict(county=c,
        sites_2022=ns(2022,c),sites_2024=ns(2024,c),sites_2026=ns(2026,c),
        votes_2022=a['win'],votes_2024=b['win'],votes_2026=e['win'],
        pct_chg_26v22=round(100*(e['win']-a['win'])/a['win'],1) if a['win'] else '',
        black_share_2022=round(100*a['race'].get(B,0)/a['win'],2) if a['win'] else '',
        black_share_2026=round(100*e['race'].get(B,0)/e['win'],2) if e['win'] else '',
        dem_share_2022=round(100*a['party'].get('DEM',0)/a['win'],2) if a['win'] else '',
        dem_share_2026=round(100*e['party'].get('DEM',0)/e['win'],2) if e['win'] else ''))
with open('analysis/county_sites_turnout.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print("wrote analysis/county_sites_turnout.csv",len(rows),"counties")

# statewide summary
tot={yr:sum(x['win'] for x in d[yr]['county'].values()) for yr in (2022,2024,2026)}
sites={yr:len(d[yr]['site']) for yr in (2022,2024,2026)}
blk={yr:sum(x['race'].get(B,0) for x in d[yr]['county'].values()) for yr in (2022,2024,2026)}
print("\nSTATEWIDE")
for yr in (2022,2024,2026):
    print(f"  {yr}: sites={sites[yr]} votes={tot[yr]:,} v/site={tot[yr]/sites[yr]:,.0f} black={100*blk[yr]/tot[yr]:.2f}%")
