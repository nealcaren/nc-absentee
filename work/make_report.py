import pickle, html
d=pickle.load(open('work/agg2.pkl','rb'))
years=[2022,2024,2026]
tot={y:sum(x['win'] for x in d[y]['county'].values()) for y in years}
sites={y:len(d[y]['site']) for y in years}
ps={y:tot[y]/sites[y] for y in years}

def bar(vals,labels,color,w=520,h=260,maxv=None,title='',fmt='{:.0f}'):
    maxv=maxv or max(vals)*1.15
    bw=w/len(vals)*0.55; step=w/len(vals)
    out=[f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px">']
    base=h-40
    for i,(v,l) in enumerate(zip(vals,labels)):
        bh=(v/maxv)*(base-30)
        x=i*step+(step-bw)/2; y=base-bh
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{color}" rx="3"/>')
        out.append(f'<text x="{x+bw/2:.1f}" y="{y-7:.1f}" text-anchor="middle" font-size="13" font-weight="600" fill="#222">{fmt.format(v)}</text>')
        out.append(f'<text x="{x+bw/2:.1f}" y="{base+18:.1f}" text-anchor="middle" font-size="12" fill="#555">{l}</text>')
    out.append(f'<line x1="0" y1="{base}" x2="{w}" y2="{base}" stroke="#ccc"/>')
    out.append('</svg>')
    return ''.join(out)

# scatter
pts=[]
for c in d[2022]['county']:
    if c not in d[2026]['county']: continue
    a=d[2022]['county'][c]['win']; b=d[2026]['county'][c]['win']
    if a<500: continue
    ds=sum(1 for k in d[2026]['site'] if k[0]==c)-sum(1 for k in d[2022]['site'] if k[0]==c)
    pts.append((ds,100*(b-a)/a,c))
W,H=560,320; PAD=45
minx,maxx=-4,4; miny,maxy=-30,90
def sx(x): return PAD+(x-minx)/(maxx-minx)*(W-PAD-15)
def sy(y): return H-PAD-(y-miny)/(maxy-miny)*(H-PAD-15)
sc=[f'<svg viewBox="0 0 {W} {H}" width="100%" style="max-width:{W}px">']
for gy in range(-30,91,30):
    sc.append(f'<line x1="{PAD}" y1="{sy(gy):.1f}" x2="{W-15}" y2="{sy(gy):.1f}" stroke="#eee"/><text x="{PAD-6}" y="{sy(gy)+4:.1f}" text-anchor="end" font-size="10" fill="#888">{gy}%</text>')
for gx in range(-4,5):
    sc.append(f'<text x="{sx(gx):.1f}" y="{H-PAD+16}" text-anchor="middle" font-size="10" fill="#888">{gx:+d}</text>')
sc.append(f'<line x1="{sx(0):.1f}" y1="{PAD-10}" x2="{sx(0):.1f}" y2="{H-PAD}" stroke="#bbb" stroke-dasharray="4"/>')
sc.append(f'<line x1="{PAD}" y1="{sy(0):.1f}" x2="{W-15}" y2="{sy(0):.1f}" stroke="#bbb" stroke-dasharray="4"/>')
for ds,g,c in pts:
    r=6 if g>60 else 4
    sc.append(f'<circle cx="{sx(ds):.1f}" cy="{sy(g):.1f}" r="{r}" fill="#2b6cb0" opacity="0.45"/>')
    if ds<-1 or g>65: sc.append(f'<text x="{sx(ds)+7:.1f}" y="{sy(g)+3:.1f}" font-size="9" fill="#444">{html.escape(c.title())}</text>')
sc.append(f'<text x="{W/2}" y="{H-6}" text-anchor="middle" font-size="11" fill="#555">Change in number of early-voting sites, 2022 \u2192 2026</text>')
sc.append(f'<text x="12" y="{H/2}" text-anchor="middle" font-size="11" fill="#555" transform="rotate(-90 12 {H/2})">% change in early votes, first 6 days</text>')
sc.append('</svg>')
scatter=''.join(sc)

h=f'''<!doctype html><meta charset="utf-8"><title>NC early voting sites, 2022-2026</title>
<style>body{{font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;max-width:760px;margin:40px auto;padding:0 20px;color:#222}}
h1{{font-size:24px;margin-bottom:4px}} h2{{font-size:17px;margin-top:34px;border-bottom:1px solid #e5e5e5;padding-bottom:5px}}
.sub{{color:#666;font-size:13px;margin-bottom:24px}} table{{border-collapse:collapse;width:100%;font-size:13.5px;margin:10px 0}}
th,td{{padding:6px 9px;border-bottom:1px solid #eee;text-align:right}} th:first-child,td:first-child{{text-align:left}}
th{{background:#f7f7f7;font-weight:600}} .note{{background:#fbf7e8;border-left:3px solid #d9b23a;padding:10px 14px;font-size:13px;margin:18px 0}}
.flex{{display:flex;gap:28px;flex-wrap:wrap}} figure{{margin:0}} figcaption{{font-size:12px;color:#666;margin-top:6px}}</style>
<h1>North Carolina early voting, 2022\u20132026</h1>
<div class="sub">In-person early votes in the first 6 days of each early-voting period \u00b7 source: NC absentee files</div>

<div class="note"><b>Important:</b> the 2026 file is a snapshot through Oct 20, 2026 \u2014 six days into early voting. All comparisons use matched 6-day windows (2022: Oct 20\u201325, 2024: Oct 17\u201322, 2026: Oct 15\u201320).</div>

<h2>Statewide</h2>
<table><tr><th>Year</th><th>Early-voting sites</th><th>Early votes (6 days)</th><th>Votes per site</th></tr>
<tr><td>2022 (midterm)</td><td>354</td><td>600,780</td><td>1,697</td></tr>
<tr><td>2024 (presidential)</td><td>415</td><td>1,606,500</td><td>3,871</td></tr>
<tr><td>2026 (midterm)</td><td>364</td><td>878,687</td><td>2,414</td></tr></table>

<div class="flex">
<figure>{bar([354,415,364],['2022','2024','2026'],'#2b6cb0')}<figcaption>Early-voting sites used</figcaption></figure>
<figure>{bar([1697,3871,2414],['2022','2024','2026'],'#c05621',fmt='{:,.0f}')}<figcaption>Early votes per site</figcaption></figure>
</div>

<h2>Site change vs. turnout change, by county</h2>
{scatter}
<p style="font-size:13px;color:#555">Counties that lost sites are not the counties that lost turnout. Median early-vote growth was +34.7% in counties that lost sites, +30.7% in counties with no change, and +49.8% in counties that gained sites.</p>

<h2>Who is voting early</h2>
<table><tr><th>Group</th><th>2022</th><th>2024</th><th>2026</th><th>26 vs 22</th></tr>
<tr><td>Black</td><td>19.1%</td><td>18.9%</td><td>23.4%</td><td>+4.3</td></tr>
<tr><td>White</td><td>74.1%</td><td>70.9%</td><td>66.2%</td><td>\u22127.9</td></tr>
<tr><td>Democratic</td><td>38.9%</td><td>34.4%</td><td>43.9%</td><td>+5.0</td></tr>
<tr><td>Republican</td><td>32.3%</td><td>34.4%</td><td>21.9%</td><td>\u221210.4</td></tr>
<tr><td>Unaffiliated</td><td>28.7%</td><td>30.8%</td><td>34.0%</td><td>+5.3</td></tr></table>
<p style="font-size:13px;color:#555">Shares of in-person early voters. These are not turnout <i>rates</i> \u2014 the files contain voters, not registered-voter denominators.</p>
'''
open('analysis/nc_early_voting_2026.html','w').write(h)
print("wrote analysis/nc_early_voting_2026.html")
