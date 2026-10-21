import pickle
# ---- data (verified above) ----
sites={2022:354,2024:415,2026:364}
votes={2022:600780,2024:1606500,2026:878687}
race={'White':(10.36,25.10,13.02),'Black':(9.07,22.90,16.05),'Asian':(5.19,17.30,10.48),'Other':(4.26,13.25,8.04)}
party={'Democrat':(10.75,25.50,19.16),'Republican':(9.63,25.59,9.16),'Unaffiliated':(7.61,18.97,10.98)}
age={'18-24':(2.19,10.56,4.87),'25-34':(2.61,11.45,4.97),'35-44':(4.11,14.60,6.78),'45-54':(6.39,20.59,9.58),'55-64':(11.29,29.13,14.77),'65-74':(19.52,38.08,23.56),'75+':(19.98,37.40,24.65)}

def grouped(data,colors=('#9db4d0','#2b6cb0')):
    """data: dict label->(v22,v24,v26) ; grouped bars 2022 vs 2026"""
    labels=list(data); W=620; H=300; PAD=48; GW=(W-PAD-20)/len(labels); bw=GW*0.32
    maxv=max(max(v[0],v[2]) for v in data.values())*1.18
    o=[f'<svg viewBox="0 0 {W} {H}" width="100%" style="max-width:{W}px">']
    base=H-42
    for i,l in enumerate(labels):
        x0=PAD+i*GW
        for j,(val,col) in enumerate([(data[l][0],colors[0]),(data[l][2],colors[1])]):
            bh=(val/maxv)*(base-25)
            x=x0+GW*0.5-bw-2+j*(bw+4); y=base-bh
            o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{col}" rx="2"/>')
            o.append(f'<text x="{x+bw/2:.1f}" y="{y-5:.1f}" text-anchor="middle" font-size="10.5" fill="#333">{val:.1f}</text>')
        o.append(f'<text x="{x0+GW*0.5:.1f}" y="{base+17:.1f}" text-anchor="middle" font-size="11.5" fill="#555">{l}</text>')
    o.append(f'<line x1="{PAD}" y1="{base}" x2="{W-20}" y2="{base}" stroke="#ccc"/>')
    o.append(f'<text x="{PAD}" y="18" font-size="11" fill="#777">% of active registered voters</text>')
    o.append('</svg>')
    return ''.join(o)

h=f'''<!doctype html><meta charset="utf-8"><title>NC early voting 2026: sites, turnout, and group effects</title>
<style>body{{font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;max-width:780px;margin:40px auto;padding:0 20px;color:#1a1a1a}}
h1{{font-size:25px;margin-bottom:2px}} h2{{font-size:17px;margin-top:36px;border-bottom:1px solid #e3e3e3;padding-bottom:6px}} h3{{font-size:15px;margin-top:28px;color:#333}}
.sub{{color:#666;font-size:13px;margin-bottom:22px}}
table{{border-collapse:collapse;width:100%;font-size:13.5px;margin:12px 0}}
th,td{{padding:6px 9px;border-bottom:1px solid #eee;text-align:right}} th:first-child,td:first-child{{text-align:left}}
th{{background:#f6f7f9;font-weight:600}} .pos{{color:#1a6b3c;font-weight:600}} .neg{{color:#9b2c2c;font-weight:600}}
.note{{background:#fbf7e8;border-left:3px solid #d9b23a;padding:10px 14px;font-size:13px;margin:18px 0}}
.key{{background:#eef4fb;border-left:3px solid #2b6cb0;padding:10px 14px;font-size:13.5px;margin:18px 0}}
figure{{margin:16px 0}} figcaption{{font-size:12px;color:#666;margin-top:4px}}
.lg{{font-size:12px;color:#555;margin-bottom:-6px}} .sw{{display:inline-block;width:10px;height:10px;border-radius:2px;margin:0 4px 0 10px}}</style>
<h1>North Carolina early voting, 2022&ndash;2026</h1>
<div class="sub">Matched 6-day windows &middot; 2022: Oct 20&ndash;25 &middot; 2024: Oct 17&ndash;22 &middot; 2026: Oct 15&ndash;20 &middot; denominators: NCSBE active registered voters</div>

<div class="note"><b>Snapshot caveat.</b> The 2026 absentee file ends Oct 20, 2026, six days into early voting. Every turnover number below therefore describes <i>early voting only</i>, not final turnout.</div>

<h2>1. Were there fewer early-voting sites?</h2>
<table><tr><th>Year</th><th>Sites with votes</th><th>Early votes (6 days)</th><th>Votes / site</th></tr>
<tr><td>2022 (midterm)</td><td>354</td><td>600,780</td><td>1,697</td></tr>
<tr><td>2024 (presidential)</td><td>415</td><td>1,606,500</td><td>3,871</td></tr>
<tr><td>2026 (midterm)</td><td>364</td><td>878,687</td><td>2,414</td></tr></table>
<p>Counted here are sites that recorded votes in the six-day window; the official site lists are about 10% larger and appear directly below. On this measure, counts are down 12% from 2024 but <b>up 10 sites (2.8%) from 2022</b>. County-level: 17 gained sites, 70 unchanged, 10 lost. Every large county gained (Wake 15&rarr;18, Mecklenburg 24&rarr;25, Guilford 15&rarr;17). The apparent decline is the 2024 presidential build-out, not a midterm contraction.</p>

<h3>Hours: the better measure of access</h3>
<p>A site count treats a location open three afternoons a week the same as one open twelve hours a day for seventeen days. The NCSBE site lists publish full daily schedules, so total <i>site-hours</i> can be computed directly: each site's open hours multiplied by the number of days it operates.</p>
<table><tr><th>Year</th><th>Sites</th><th>Total site-hours</th><th>Hours / site</th><th>Hours per 1k registrants</th></tr>
<tr><td>2022 (midterm)</td><td>390</td><td>55,194</td><td>142</td><td>8.5</td></tr>
<tr><td>2024 (presidential)</td><td>449</td><td>66,284</td><td>148</td><td>9.5</td></tr>
<tr><td>2026 (midterm)</td><td>399</td><td>56,976</td><td>143</td><td>8.3</td></tr></table>
<p>These figures come from the official NCSBE site lists, which count every listed location rather than only those that recorded votes in the six-day window. They confirm the direction independently: <b>+9 sites and +3.2% site-hours versus 2022</b>, and &minus;11% sites and &minus;14% hours versus 2024.</p>

<div class="key"><b>Site counts hide real cuts.</b> 27 counties kept the same number of sites and cut their hours. Alamance is the clean example: five sites in both years, but 776 site-hours in 2022 and 716 in 2026, because one site's schedule fell from 152 hours to 87.5.</div>

<p>Across counties, 44 cut total site-hours and 46 added them; the median county change is exactly 0.0%, with the 10th and 90th percentiles at &minus;33% and +40%. The largest proportional losses were Lenoir (&minus;50%), Vance (&minus;47%), Sampson (&minus;44%), Johnston (&minus;41%) and Graham (&minus;42%). Hours per 1,000 active registrants are essentially unchanged statewide (8.5 to 8.3), so the cuts were offset elsewhere rather than concentrated.</p>
<p>The rules changed in 2026, but they did not produce a smaller early-voting footprint than the last midterm. They produced a <i>redistributed</i> one, with more counties cutting than the site counts suggest.</p>

<h2>2. Early turnout rate by group</h2>
<div class="key"><b>This is the finding that matters.</b> Black early turnout rose 7.0 points, from 9.1% to 16.1% of registered Black voters &mdash; and now exceeds the White rate. Republican early turnout was flat.</div>
<div class="lg"><span class="sw" style="background:#9db4d0"></span>2022 <span class="sw" style="background:#2b6cb0"></span>2026</div>
<figure>{grouped(race)}<figcaption>Early turnout rate by race, first six days</figcaption></figure>
<figure>{grouped(party)}<figcaption>Early turnout rate by registered party</figcaption></figure>
<table><tr><th>Group</th><th>2022</th><th>2024</th><th>2026</th><th>2026 vs 2022</th></tr>
<tr><td>White</td><td>10.4%</td><td>25.1%</td><td>13.0%</td><td class="pos">+2.7</td></tr>
<tr><td>Black</td><td>9.1%</td><td>22.9%</td><td>16.1%</td><td class="pos">+7.0</td></tr>
<tr><td>Democrat</td><td>10.8%</td><td>25.5%</td><td>19.2%</td><td class="pos">+8.4</td></tr>
<tr><td>Republican</td><td>9.6%</td><td>25.6%</td><td>9.2%</td><td class="neg">&minus;0.5</td></tr>
<tr><td>Unaffiliated</td><td>7.6%</td><td>19.0%</td><td>11.0%</td><td class="pos">+3.4</td></tr>
<tr><td>Age 75+</td><td>20.0%</td><td>37.4%</td><td>24.7%</td><td class="pos">+4.7</td></tr>
<tr><td>Age 18&ndash;24</td><td>2.2%</td><td>10.6%</td><td>4.9%</td><td class="pos">+2.7</td></tr></table>

<h2>3. Did losing a site suppress turnout?</h2>
<p>For each precinct I found the site its 2022 early voters used most. <b>654 of 1,918 precincts (34%) lost that site</b> before 2026.</p>
<table><tr><th>Precincts</th><th>Black 2022</th><th>Black 2026</th><th>Change</th><th>White 2022</th><th>White 2026</th><th>Change</th></tr>
<tr><td>Lost their site (654)</td><td>9.37%</td><td>16.40%</td><td class="pos">+7.03</td><td>10.41%</td><td>13.29%</td><td class="pos">+2.88</td></tr>
<tr><td>Retained site (1,264)</td><td>9.49%</td><td>16.42%</td><td class="pos">+6.93</td><td>10.92%</td><td>13.48%</td><td class="pos">+2.56</td></tr></table>
<p>No suppression. Within-county fixed-effects regression of turnout change on site loss: <b>+0.10 percentage points</b>, indistinguishable from zero. Precincts losing a site grew slightly <i>faster</i>, not slower.</p>
<p>The county-level hours test says the same thing. Regressing the change in each group's early turnout rate on the change in site-hours per 1,000 registrants gives a correlation of <b>+0.10 for White voters and +0.04 for Black voters</b> &mdash; no relationship. Counties that cut hours most still saw Black early turnout rise 6.7 points, against 7.3 in counties that added hours. The gradient is in the right direction and far too small to matter.</p>

<h2>4. Were closures targeted at Black precincts?</h2>
<p>Nationwide, siting disputes often turn on this. Within counties, no:</p>
<table><tr><th>Precincts (within county)</th><th>Lost their site</th></tr>
<tr><td>Above county median Black share (n=861)</td><td>34.7%</td></tr>
<tr><td>Below county median Black share (n=861)</td><td>36.4%</td></tr></table>
<p>An apparent statewide gradient (Blacker precincts lost sites at higher rates) disappears once you compare within counties. It reflects churn concentrated in large urban counties, not targeting.</p>

<h2>5. Can the early vote predict the outcome?</h2>
<div class="note"><b>Mostly no.</b> Early-vote composition measures <i>when</i> people vote, not <i>how many</i> will. The two prior cycles show the naive reading failing in the same direction both times.</div>
<table><tr><th>Year</th><th>Day-6 early D share of D+R</th><th>Naive read</th><th>Actual two-party result</th><th>Miss</th></tr>
<tr><td>2022</td><td>54.6%</td><td>D +9.2</td><td>R +4.1</td><td class="neg">&minus;13.3</td></tr>
<tr><td>2024</td><td>50.0%</td><td>D &minus;0.1</td><td>R +3.8</td><td class="neg">&minus;3.8</td></tr>
<tr><td>2026</td><td><b>66.7%</b></td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td></tr></table>

<p>The defensible version is reverse arithmetic: how much of the <i>remaining</i> vote does each side need?</p>
<table><tr><th>Measure</th><th>Value</th></tr>
<tr><td>Democratic early votes banked (6 days)</td><td>384,673</td></tr>
<tr><td>Republican early votes banked</td><td>192,295</td></tr>
<tr><td>Democratic lead</td><td>+192,378</td></tr>
<tr><td><b>R share of remaining two-party vote needed to tie</b></td><td><b>54.1%</b></td></tr>
<tr><td>R share actually won after day 6, 2022</td><td>51.4%</td></tr>
<tr><td>R share actually won after day 6, 2024</td><td>51.5%</td></tr></table>

<p>Republicans have never cleared 54% of the post-day-6 vote in either comparison cycle. If they repeat 51.5%, the registration margin lands at D+4.2; correcting for the historical gap between registration and actual vote (R gained 1.7 to 3.3 points in 2022 and 2024) gives <b>roughly D+1 to D+2.5</b>. If they hit 54%, it is a tie. At 55%, Republicans win by 1 to 3.</p>

<h2>6. What to expect each day</h2>
<p>The absentee file refreshes each morning, so the question becomes what the next day should look like. All three cycles open on a Thursday and close on a Saturday with the election the following Tuesday, so days-until-election lines up exactly and the first six days can be compared without adjustment.</p>

<h3>The weekly rhythm has not changed</h3>
<table><tr><th>Year</th><th>Thu</th><th>Fri</th><th>Sat</th><th>Sun</th><th>Mon</th><th>Tue</th></tr>
<tr><td>2022</td><td>22.9%</td><td>22.1%</td><td>5.8%</td><td>3.4%</td><td>23.6%</td><td>22.2%</td></tr>
<tr><td>2024</td><td>22.5%</td><td>21.2%</td><td>10.5%</td><td>4.7%</td><td>21.3%</td><td>19.8%</td></tr>
<tr><td>2026</td><td>23.2%</td><td>22.6%</td><td>7.0%</td><td>2.8%</td><td>23.2%</td><td>21.2%</td></tr></table>
<p style="font-size:13px;color:#555">Each year's share of its own first six days, by weekday.</p>
<p>Weekends are the trough and the shape is stable. 2026's Saturday runs at 30% of its Thursday, between 2022 (25%) and 2024 (47%). The Sunday dip is slightly deeper than either. Nothing so far indicates a different weekly rhythm this year, so a historical day-of-week template is safe to use.</p>

<h3>Running at 1.46 times 2022, but only for Democrats</h3>
<p>Day by day, 2026 sits close to 1.46 times 2022's level, and the ratio is steady across all six days (1.21 to 1.76, the low being Sunday and the high Saturday). Against 2024 it is far below, as a midterm should be. The scale is not uniform across parties:</p>
<table><tr><th>Party</th><th>Banked, day 6</th><th>vs 2022</th><th>Path A total</th><th>Path B total</th></tr>
<tr><td>Democrat</td><td>384,673</td><td class="pos">1.65&times;</td><td>1,250,248</td><td>908,946</td></tr>
<tr><td>Republican</td><td>192,295</td><td>0.99&times;</td><td>642,676</td><td>645,915</td></tr>
<tr><td>Unaffiliated</td><td>298,105</td><td class="pos">1.73&times;</td><td>1,041,472</td><td>726,949</td></tr></table>
<p>Republicans are at 0.99 times their 2022 pace &mdash; flat. The entire increase over the last midterm is Democrats and unaffiliated voters. That is the composition story from section 2 arriving in the daily flow.</p>

<h3>Two paths for the remaining eleven days</h3>
<p><b>Path A</b> assumes the 1.46&times; scale persists to the end: total in-person early voting of <b>2.94M</b>. <b>Path B</b> assumes the surge was front-loaded and the remaining days revert to their 2022 levels: <b>2.29M</b>. Both are defensible, and they differ by 650,000 votes.</p>
<p>Midterms back-load more than presidential years: the final four days were 33.7% of the 2022 early vote but only 24.2% in 2024. That argues for the lower path unless the ratio holds through the middle of the cycle. The end-of-cycle shape itself is stable, though: both templates peak on the final Friday (day 16) and fall back on the closing Saturday.</p>

<table><tr><th>Day</th><th>Date</th><th>Dow</th><th>2022</th><th>2026 seen</th><th>Path A</th><th>Path B</th><th>2024</th></tr><tr><td>1</td><td>Oct 15</td><td>Thu</td><td>137,387</td><td><b>203,247</b></td><td>200,036</td><td>203,247</td><td>360,192</td></tr>
<tr><td>2</td><td>Oct 16</td><td>Fri</td><td>132,506</td><td><b>197,760</b></td><td>193,453</td><td>197,760</td><td>339,865</td></tr>
<tr><td>3</td><td>Oct 17</td><td>Sat</td><td>35,027</td><td><b>61,744</b></td><td>52,598</td><td>61,744</td><td>168,619</td></tr>
<tr><td>4</td><td>Oct 18</td><td>Sun</td><td>20,272</td><td><b>24,542</b></td><td>31,161</td><td>24,542</td><td>75,556</td></tr>
<tr><td>5</td><td>Oct 19</td><td>Mon</td><td>141,489</td><td><b>203,566</b></td><td>205,918</td><td>203,566</td><td>341,326</td></tr>
<tr><td>6</td><td>Oct 20</td><td>Tue</td><td>133,127</td><td><b>186,117</b></td><td>193,577</td><td>186,117</td><td>317,717</td></tr>
<tr><td>7</td><td>Oct 21</td><td>Wed</td><td>124,614</td><td>&mdash;</td><td>181,313</td><td>124,614</td><td>292,050</td></tr>
<tr><td>8</td><td>Oct 22</td><td>Thu</td><td>120,505</td><td>&mdash;</td><td>175,970</td><td>120,505</td><td>275,686</td></tr>
<tr><td>9</td><td>Oct 23</td><td>Fri</td><td>133,689</td><td>&mdash;</td><td>194,827</td><td>133,689</td><td>287,489</td></tr>
<tr><td>10</td><td>Oct 24</td><td>Sat</td><td>60,607</td><td>&mdash;</td><td>90,235</td><td>60,607</td><td>138,244</td></tr>
<tr><td>11</td><td>Oct 25</td><td>Sun</td><td>32,765</td><td>&mdash;</td><td>50,021</td><td>32,765</td><td>76,933</td></tr>
<tr><td>12</td><td>Oct 26</td><td>Mon</td><td>125,987</td><td>&mdash;</td><td>183,059</td><td>125,987</td><td>274,373</td></tr>
<tr><td>13</td><td>Oct 27</td><td>Tue</td><td>135,209</td><td>&mdash;</td><td>196,053</td><td>135,209</td><td>255,398</td></tr>
<tr><td>14</td><td>Oct 28</td><td>Wed</td><td>138,863</td><td>&mdash;</td><td>202,251</td><td>138,863</td><td>243,442</td></tr>
<tr><td>15</td><td>Oct 29</td><td>Thu</td><td>157,145</td><td>&mdash;</td><td>229,163</td><td>157,145</td><td>225,365</td></tr>
<tr><td>16</td><td>Oct 30</td><td>Fri</td><td>212,679</td><td>&mdash;</td><td>311,407</td><td>212,679</td><td>307,777</td></tr>
<tr><td>17</td><td>Oct 31</td><td>Sat</td><td>169,019</td><td>&mdash;</td><td>251,271</td><td>169,019</td><td>243,702</td></tr></table>

<div class="key"><b>The next three days settle it.</b> If Oct 21&ndash;23 land near 175,000&ndash;195,000 a day, the surge is persisting and the total is about 2.9M. If they fall to 120,000&ndash;135,000, it was front-loaded and the total is about 2.3M. Run <code>python3 work/update_daily.py --download</code> each morning for the scorecard.</div>

<p>Because the scales differ so much by party, the daily numbers split accordingly. Through day 6 the Democrats banked 384,673, Republicans 192,295, and unaffiliated voters 298,105. The remaining days under each path:</p>
<table><tr><th>Day</th><th>Date</th><th>Path A Dem</th><th>A Rep</th><th>A Una</th><th>Path B Dem</th><th>B Rep</th><th>B Una</th></tr><tr><td>7</td><td>Oct 21</td><td>77,767</td><td>41,200</td><td>61,944</td><td>47,103</td><td>41,496</td><td>35,735</td></tr>
<tr><td>8</td><td>Oct 22</td><td>76,136</td><td>38,926</td><td>60,519</td><td>46,115</td><td>39,206</td><td>34,913</td></tr>
<tr><td>9</td><td>Oct 23</td><td>81,166</td><td>43,907</td><td>69,214</td><td>49,162</td><td>44,223</td><td>39,929</td></tr>
<tr><td>10</td><td>Oct 24</td><td>40,458</td><td>17,087</td><td>32,408</td><td>24,505</td><td>17,210</td><td>18,696</td></tr>
<tr><td>11</td><td>Oct 25</td><td>24,270</td><td>7,420</td><td>18,194</td><td>14,700</td><td>7,473</td><td>10,496</td></tr>
<tr><td>12</td><td>Oct 26</td><td>76,293</td><td>42,132</td><td>64,173</td><td>46,210</td><td>42,435</td><td>37,021</td></tr>
<tr><td>13</td><td>Oct 27</td><td>80,024</td><td>45,868</td><td>69,607</td><td>48,470</td><td>46,198</td><td>40,156</td></tr>
<tr><td>14</td><td>Oct 28</td><td>82,880</td><td>45,843</td><td>72,916</td><td>50,200</td><td>46,173</td><td>42,065</td></tr>
<tr><td>15</td><td>Oct 29</td><td>93,706</td><td>51,481</td><td>83,206</td><td>56,757</td><td>51,851</td><td>48,001</td></tr>
<tr><td>16</td><td>Oct 30</td><td>125,559</td><td>68,057</td><td>116,697</td><td>76,050</td><td>68,546</td><td>67,322</td></tr>
<tr><td>17</td><td>Oct 31</td><td>107,317</td><td>48,460</td><td>94,489</td><td>65,001</td><td>48,809</td><td>54,510</td></tr>
<tr><td colspan=2><b>Days 7&ndash;17</b></td><td><b>865,576</b></td><td><b>450,381</b></td><td><b>743,367</b></td><td><b>524,273</b></td><td><b>453,620</b></td><td><b>428,844</b></td></tr></table>

<p>The early-vote party split lands at either 66.0% Democratic (Path A) or 58.5% (Path B), against 53.9% in 2022 and 48.9% in 2024. Even the low path implies a Democratic early lead of 263,000 votes, and the high path 608,000.</p>

<h2>7. The precinct-level model</h2>
<p>The panel covers 2,434 precincts matched across 2022, 2024 and 2026, with early votes by party from the absentee files, total turnout by party and method from <code>history_stats</code>, and the precinct name&harr;code crosswalk taken from the voter file (which carries both fields). Election Day behaviour is then modelled as each precinct's own post-day-6 Republican share.</p>

<div class="key"><b>The precinct model does not beat the simple version.</b> Asking each precinct to carry its own Election Day behaviour adds noise rather than information. The county is the right level. Two backtests is thin evidence, but the ordering is identical in both, and the mechanism is straightforward: precinct-level shares are noisy and only weakly persistent across cycles, so the noise averages out before the signal does.</div>

<table><tr><th>Backtest</th><th>Precinct shares</th><th>County shares</th><th>Statewide constant</th></tr>
<tr><td>Predict 2024 from 2022</td><td class="neg">+0.89</td><td class="pos">&minus;0.11</td><td>+0.21</td></tr>
<tr><td>Predict 2022 from 2024</td><td class="neg">&minus;1.07</td><td class="pos">+0.07</td><td>&minus;0.25</td></tr>
<tr><td>Mean absolute error</td><td class="neg">0.98</td><td class="pos"><b>0.09</b></td><td>0.23</td></tr></table>
<p style="font-size:13px;color:#555">Errors are in percentage points of the two-party margin. Conditional on knowing the total vote, which the model still takes as an assumption.</p>

<p>Projection for 2026 using county-level post-day-6 shares, across final two-party electorates of 2.6M to 3.2M:</p>
<table><tr><th>Final D+R turnout</th><th>Dem</th><th>Rep</th><th>D&minus;R (registration)</th></tr>
<tr><td>2.6M</td><td>1,441,940</td><td>1,314,201</td><td>+4.63</td></tr>
<tr><td>2.9M</td><td>1,597,953</td><td>1,476,139</td><td>+3.96</td></tr>
<tr><td>3.2M</td><td>1,753,988</td><td>1,638,106</td><td>+3.42</td></tr></table>
<p>Registration margin <b>+3.4 to +4.6</b>. Applying the historical registration-to-vote correction gives a vote margin of <b>+0.1 to +2.9, centred on D+1.5</b>. A one-point shift in the Republican share of the remaining vote moves the margin about 1.6 points, so the result flips if Republicans outperform the 2022/2024 pattern by roughly 2.5 points.</p>

<h2>8. What the data cannot say</h2>
<ul style="font-size:13.5px">
<li><b>Hours, not capacity or distance.</b> Site-hours are measured now, but machines, staffing, lines, and how far a site is from the voters assigned to it are not. A location can stay open twelve hours a day and still serve far fewer people.</li>
<li><b>Addresses exist but distance was not computed.</b> The official site lists carry street addresses for all three cycles, so a distance measure is buildable; it would need geocoding and a travel-time model, which this analysis does not include.</li>
<li><b>Early voting only.</b> Election Day voters are absent. A group could shift from early to Election Day with no change in total turnout.</li>
<li><b>Renames.</b> Site names churn between cycles. Some precincts counted as &ldquo;lost their site&rdquo; may have kept the same building under a new name, which would bias the effect toward zero.</li>
<li><b>One cycle.</b> 2026 vs 2022 is a single comparison, confounded with the national environment that produced the Democratic surge.</li>
<li><b>Party registration is not vote choice.</b> Roughly 2.3M North Carolinians are registered Democrats, and they do not all vote Democratic. The 1.7&ndash;3.3 point registration-to-vote correction is itself estimated from only two elections.</li>
<li><b>Timing vs turnout is unidentified.</b> A Democratic early surge could mean Democrats will turn out more, or that they moved the same votes earlier. Six days of data cannot separate these, and the answer determines the forecast.</li>
<li><b>Six of seventeen days.</b> Most early voting, plus all of Election Day, is still unobserved.</li>
</ul>
'''
open('analysis/nc_early_voting_2026.html','w').write(h)
print("rewrote analysis/nc_early_voting_2026.html")
