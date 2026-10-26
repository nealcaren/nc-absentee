#!/usr/bin/env python3
"""Build the static tracker site.

The forecast is re-estimated on every run from all days observed so far (see
work/central.py). To keep the scorecard honest, every run also appends the
forecast it just issued to data/vintages.json, keyed by the last day of data it
had seen. A day's accuracy is then measured against the vintage issued
immediately before it, never against a model that has since seen the answer.

Outputs _site/index.html, _site/report.html, _site/data.json.
Standard library only.
"""
import json, os, datetime
from central import central, band, GROUPS
from geography import geography, vote_choice

BASE = json.load(open('data/baseline.json'))
OBS = json.load(open('data/observed.json'))
VIN_PATH = 'data/vintages.json'
VIN = json.load(open(VIN_PATH)) if os.path.exists(VIN_PATH) else {}

ELECTION = datetime.date.fromisoformat(OBS['election'])
PARTS = ['DEM', 'REP', 'UNA', 'OTH']
LABEL = {'DEM': 'Democrat', 'REP': 'Republican', 'UNA': 'Unaffiliated', 'OTH': 'Libertarian &amp; other'}
LAST = int(OBS['last_day'])
THROUGH = datetime.date.fromisoformat(OBS['through'])
DAYS_TO_GO = 17 - LAST

b22 = {int(k): v for k, v in BASE['days']['2022'].items()}
b24 = {int(k): v for k, v in BASE['days']['2024'].items()}
obs = {int(k): v for k, v in OBS['days'].items()}
BANKED = sum(obs[k]['total'] for k in range(1, LAST + 1))


def date_of(k):
    return ELECTION - datetime.timedelta(days=20 - k)


def grp(day, p):
    return sum(day.get(q, 0) for q in GROUPS[p])


F22 = {p: sum(grp(b22[k], p) for k in b22) for p in PARTS}    # 2022 final, by party
T22 = sum(F22.values())
BANK = {p: sum(grp(obs[k], p) for k in range(1, LAST + 1)) for p in PARTS}

# --- forecast (both baselines, all observed days) -------------------------
C = central(obs, b22, b24, LAST)
MID, MLO, MHI = C['total']
PT, SIMS = C['party_point'], C['party_sims']
NS = len(SIMS['DEM'])
sim_tot = [sum(SIMS[p][i] for p in PARTS) for i in range(NS)]


def pct_band(f, point):
    """90% band, in percent, for a function of one draw's party totals."""
    draws = [100 * f({p: SIMS[p][i] for p in PARTS}) for i in range(NS)]
    return band(draws, 100 * f(point))


CHANGE = {p: pct_band(lambda d, p=p: d[p] / F22[p] - 1, PT) for p in PARTS}
SHARE = {p: pct_band(lambda d, p=p: d[p] / sum(d.values()), PT) for p in PARTS}
TOT_CHANGE = band([100 * (t / T22 - 1) for t in sim_tot], 100 * (MID / T22 - 1))
DSHARE = pct_band(lambda d: d['DEM'] / (d['DEM'] + d['REP']), PT)
DSHARE22 = 100 * F22['DEM'] / (F22['DEM'] + F22['REP'])
DSHARE_BANK = 100 * BANK['DEM'] / (BANK['DEM'] + BANK['REP'])

# --- record this run's forecast ------------------------------------------
if LAST < 17:
    key = str(LAST)
    v = VIN.setdefault(key, {'issued': str(datetime.date.today()), 'last_day': LAST, 'through': str(THROUGH)})
    fresh = {'central': {str(k): list(C['day'][k]) for k in range(LAST + 1, 18)},
             'total_central': list(C['total']),
             'party_central': {p: list(C['party'][p]) for p in PARTS},
             'party_day': {p: {str(k): list(C['party_day'][p][k]) for k in range(LAST + 1, 18)} for p in PARTS}}
    missing = {f: val for f, val in fresh.items() if f not in v}
    if missing:                             # keep the first forecast issued on a given information set
        v.update(missing)
        json.dump(VIN, open(VIN_PATH, 'w'), indent=1, sort_keys=True)


# --- scorecard ------------------------------------------------------------
def vintage_central(k):
    """Central forecast and interval for day k, issued just before day k was observed.
    Days before the forecast was introduced are replayed from data through day k-1
    and flagged, so they can be shown but never counted as issued."""
    v = VIN.get(str(k - 1), {}).get('central', {}).get(str(k))
    if v:
        return v, False
    if k - 1 >= 5:                          # need three weekdays to fit a trend
        return list(central(obs, b22, b24, k - 1)['day'][k]), True
    return None, False


def rng(lo, hi):
    return f'{lo/1000:,.0f}&ndash;{hi/1000:,.0f}k'


rows, cerrs, rerrs = [], [], []
for k in range(1, 18):
    d = date_of(k).strftime('%a %b %-d')
    if k <= LAST:
        act = obs[k]['total']
        vc, replay = vintage_central(k)
        if vc:
            m, lo, hi = vc
            (rerrs if replay else cerrs).append((k, act, m, lo <= act <= hi))
            cls = 'ok' if lo <= act <= hi else ('hi' if act > hi else 'lo')
            rows.append(f'<tr class="seen"><td>{k}</td><td>{d}</td><td>{m:,}</td><td class="rng">{rng(lo, hi)}</td>'
                        f'<td><b>{act:,}</b></td><td class="{cls}">{act / m:.2f}</td></tr>')
            if replay:
                rows[-1] = rows[-1].replace(f'<td>{m:,}</td>', f'<td class="rng">{m:,}&#8224;</td>', 1)
        else:
            rows.append(f'<tr class="seen"><td>{k}</td><td>{d}</td><td>&middot;</td><td></td>'
                        f'<td><b>{act:,}</b></td><td></td></tr>')
    else:
        m, lo, hi = C['day'][k]
        rows.append(f'<tr class="future"><td>{k}</td><td>{d}</td><td>{m:,}</td><td class="rng">{rng(lo, hi)}</td>'
                    f'<td>&middot;</td><td></td></tr>')
scorecard = '\n'.join(rows)

c_mae = sum(abs(a - m) for _, a, m, _ in cerrs) / len(cerrs) if cerrs else None
c_in = sum(inside for *_, inside in cerrs)
r_in = sum(inside for *_, inside in rerrs)

# --- daily error by party -------------------------------------------------
EPARTS = ['DEM', 'REP', 'UNA']
_replays = {}


def party_vintage(k):
    """Each party's forecast for day k, issued after day k-1 (or replayed, flagged)."""
    v = VIN.get(str(k - 1), {}).get('party_day')
    if v:
        return {p: v[p][str(k)] for p in PARTS}, False
    if k - 1 < 5:
        return None, False
    if k not in _replays:
        _replays[k] = central(obs, b22, b24, k - 1)['party_day']
    return {p: list(_replays[k][p][k]) for p in PARTS}, True


def err_cell(act, fc):
    m, lo, hi = fc
    e = act - m
    cls = 'neg' if e < 0 else 'pos'
    out = ' out' if not lo <= act <= hi else ''
    txt = f'{e:+,}'.replace('-', '&minus;')
    return (f'<td class="{cls}{out}" title="forecast {m:,} ({lo:,}&ndash;{hi:,}), actual {act:,}">{txt}</td>', e)


erows, ERR = [], {p: [] for p in EPARTS + ['total']}
for k in range(1, LAST + 1):
    pv, replay = party_vintage(k)
    tv, _ = vintage_central(k)
    if not pv or not tv:
        continue
    cells = []
    for p in EPARTS:
        c, e = err_cell(grp(obs[k], p), pv[p])
        cells.append(c)
        ERR[p].append({'day': k, 'forecast': pv[p][0], 'actual': grp(obs[k], p), 'error': e,
                       'replayed': replay})
    c, e = err_cell(obs[k]['total'], tv)
    cells.append(c)
    ERR['total'].append({'day': k, 'forecast': tv[0], 'actual': obs[k]['total'], 'error': e})
    mark = '&#8224;' if replay else ''
    erows.append(f'<tr><td>{k}{mark}</td><td>{date_of(k).strftime("%a %b %-d")}</td>{"".join(cells)}</tr>')
if erows:
    mean = ''.join(f'<td>{round(sum(r["error"] for r in ERR[p]) / len(ERR[p])):+,}</td>'.replace('-', '&minus;')
                   for p in EPARTS + ['total'])
    erows.append(f'<tr class="tot"><td colspan="2">Average</td>{mean}</tr>')
error_table = '\n'.join(erows)
FIRST_PD = min((int(k) + 1 for k, v in VIN.items() if 'party_day' in v), default=LAST + 1)


# --- party table ----------------------------------------------------------
def signed(v):
    return f'{v:+.0f}%'.replace('-', '&minus;')


prow = []
for p in PARTS:
    m, lo, hi = C['party'][p]
    ch, sh = CHANGE[p], SHARE[p]
    prow.append(f'<tr><td><span class="dot {p.lower()}"></span>{LABEL[p]}</td><td>{F22[p]:,}</td>'
                f'<td><b>{m:,}</b><div class="rng">{rng(lo, hi)}</div></td>'
                f'<td><b>{signed(ch[0])}</b><div class="rng">{signed(ch[1])} to {signed(ch[2])}</div></td>'
                f'<td>{100 * F22[p] / T22:.1f}%</td>'
                f'<td><b>{sh[0]:.1f}%</b><div class="rng">{sh[1]:.1f}&ndash;{sh[2]:.1f}%</div></td></tr>')
prow.append(f'<tr class="tot"><td>Total</td><td>{T22:,}</td><td><b>{MID:,}</b><div class="rng">{rng(MLO, MHI)}</div></td>'
            f'<td><b>{signed(TOT_CHANGE[0])}</b><div class="rng">{signed(TOT_CHANGE[1])} to {signed(TOT_CHANGE[2])}</div></td>'
            f'<td>100%</td><td>100%</td></tr>')
party_table = '\n'.join(prow)

ranked = sorted(['DEM', 'REP', 'UNA'], key=lambda p: -CHANGE[p][0])
WHO = {'DEM': 'Democrats', 'REP': 'Republicans', 'UNA': 'unaffiliated voters'}


def moved(p):
    v = CHANGE[p][0]
    return f'{"up" if v >= 0 else "down"} {abs(v):.0f}% from {WHO[p]}'


party_text = (f'Compared with 2022, early votes are projected {moved(ranked[0])}, '
              f'{moved(ranked[1])} and {moved(ranked[2])}. '
f'Democrats hold <b>{DSHARE[0]:.1f}%</b> of the two-party early vote in the forecast '
              f'(90% range {DSHARE[1]:.1f}&ndash;{DSHARE[2]:.1f}%), against {DSHARE22:.1f}% in 2022. '
              f'Their share of votes banked so far is higher, {DSHARE_BANK:.1f}%, because Democrats have voted '
              f'earlier in the period than Republicans.')

# --- unaffiliated geography ---------------------------------------------
GEO = None
if OBS.get('counties') and os.path.exists('data/county_baseline.json'):
    GEO = geography(json.load(open('data/county_baseline.json')), OBS['counties'], LAST)

geo_section = ''
if GEO:
    grow = sorted(GEO['growth'].items(), key=lambda kv: -kv[1])
    name = lambda c: c.title().replace('Mcdowell', 'McDowell')
    fast = ', '.join(f'{name(c)} {g:.2f}&times;' for c, g in grow[:4])
    slow = ', '.join(f'{name(c)} {g:.2f}&times;' for c, g in grow[-3:])
    grow_rows = '\n'.join(
        f'<tr><td>{r["label"]} <span class="rng">({r["note"]})</span></td><td>{r["counties"]}</td>'
        f'<td>{100 * r["share_2022"]:.1f}%</td><td><b>{100 * r["share_2026"]:.1f}%</b></td>'
        f'<td>{100 * (r["share_2026"] - r["share_2022"]):+.1f}</td><td>{r["growth"]:.2f}&times;</td></tr>'
        for r in GEO['rows'])
    sh = [100 * (b - a) for a, b in GEO['shifts']]
    mid = sh[1]
    toward = 'Democrats' if mid < 0 else 'Republicans'
    geo_section = f'''<h2>Where unaffiliated voters are coming from</h2>
<table class="party">
<tr><th>County type, by 2022 early-vote result</th><th>Counties</th><th>2022</th><th>2026</th><th>Change (pts)</th><th>Growth</th></tr>
{grow_rows}
</table>
<p class="sub">Share of the state's unaffiliated in-person early voters living in each type of county, over the first {LAST} days of early voting in each year.</p>
<p>Unaffiliated early votes are up {GEO['una_growth']:.2f}&times; over the same days of 2022, but the growth is uneven. Among the larger counties it is fastest in {fast}, and slowest in {slow}. If each county's unaffiliated voters break the way they did in 2022, the shift in where they live moves the statewide unaffiliated vote <b>{abs(mid):.1f} points toward {toward}</b> ({min(map(abs, sh)):.1f} to {max(map(abs, sh)):.1f} across assumptions about party loyalty).</p>
<p class="sub">How unaffiliated voters break overall cannot be estimated from county results: the 2022 total fits anything from about 35% to 60% Republican, depending on how many registered Democrats voted Republican and the reverse. Each county's break relative to the others is better determined, so the shift is reported rather than the level. It assumes a new unaffiliated voter in, say, Wake votes like Wake's 2022 unaffiliated voters; if the surge is younger and newer to the rolls, the true shift is probably larger.</p>

'''

# --- bottom line: projected Democratic vs Republican early vote ----------
VC = None
finish = ''
if GEO:
    VC = vote_choice(json.load(open('data/county_baseline.json')), OBS['counties'], PT, SIMS)
    (dm, dlo, dhi), (rm, rlo, rhi), (mm, mlo, mhi) = VC['dem'], VC['rep'], VC['margin']
    ds = VC['dem_share']
    a22d, a22r = VC['actual_2022']
    lead = 'Democrats' if mm >= 0 else 'Republicans'
    pct = 100 * dm / (dm + rm)
    finish = f'''<section class="finish">
<div class="fk">The bottom line &middot; projected in-person early vote, all 17 days</div>
<div class="duel">
<div class="side dem"><div class="who">Democratic candidates</div><div class="big">{dm/1e6:.2f}M</div><div class="rng">90% range {dlo/1e6:.2f}&ndash;{dhi/1e6:.2f}M</div></div>
<div class="side rep"><div class="who">Republican candidates</div><div class="big">{rm/1e6:.2f}M</div><div class="rng">90% range {rlo/1e6:.2f}&ndash;{rhi/1e6:.2f}M</div></div>
</div>
<div class="bar"><span class="bd" style="width:{pct:.1f}%"></span><span class="br" style="width:{100-pct:.1f}%"></span><i style="left:50%"></i></div>
<div class="margin">{lead} <b>+{abs(mm)/1000:,.0f}k</b> &middot; {ds[0]:.1f}% of the two-party early vote (90% range {ds[1]:.1f}&ndash;{ds[2]:.1f}%)</div>
<div class="was">2022 early vote, US Senate: Beasley {a22d/1e6:.2f}M, Budd {a22r/1e6:.2f}M, Democrats +{(a22d-a22r)/1000:,.0f}k ({100*a22d/(a22d+a22r):.1f}%).</div>
<p class="sub">Each party's forecast turnout, voting the way its members did in 2022 in the same county: registered Democrats and Republicans mostly loyal (crossover up to 12% and 6%), unaffiliated voters at their county's 2022 rate, weighted by where they are turning out now. The range covers turnout, the loyalty assumption, and a 1.5-point swing in either direction from 2022 behavior. Early votes only; Election Day voters lean more Republican, so this is not a statewide result.</p>
</section>

'''

# --- chart ----------------------------------------------------------------
W, H, L, R, T, Bm = 860, 330, 66, 96, 18, 40
CPARTS = ['DEM', 'REP', 'UNA']
COLOR = {'DEM': '#2b6cb0', 'REP': '#9b2c2c', 'UNA': '#6b7280'}


def cum(d):
    out, run = {}, 0
    for k in range(1, 18):
        run += d.get(k, 0)
        out[k] = run
    return out


PC = C['party_cum']
C22P = {p: cum({k: grp(b22[k], p) for k in b22}) for p in CPARTS}
MAXV = max(max(PC[p][17][2], C22P[p][17]) for p in CPARTS) * 1.06


def x(k):
    return L + (k - 1) / 16 * (W - L - R)


def y(v):
    return H - Bm - v / MAXV * (H - T - Bm)


def pline(series, color, width=2, dash=None, last=None, first=None, opacity=1):
    ks = [k for k in sorted(series) if (last is None or k <= last) and (first is None or k >= first)]
    pts = ' '.join(f"{x(k):.1f},{y(series[k]):.1f}" for k in ks)
    d = f' stroke-dasharray="{dash}"' if dash else ''
    o = f' stroke-opacity="{opacity}"' if opacity < 1 else ''
    return (f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}"'
            f' stroke-linejoin="round"{d}{o}/>')


grid = []
step = 250_000
for v in range(0, int(MAXV) + 1, step):
    grid.append(f'<line x1="{L}" y1="{y(v):.1f}" x2="{W-R}" y2="{y(v):.1f}" stroke="#e8e8e8"/>')
    grid.append(f'<text x="{L-8}" y="{y(v)+4:.1f}" text-anchor="end" font-size="10.5" fill="#888">'
                f'{v/1e6:.2f}M</text>'.replace('.00M', 'M').replace('0.50M', '0.5M').replace('1.50M', '1.5M').replace('>0M<', '>0<'))
for k in (1, 5, 9, 13, 17):
    grid.append(f'<text x="{x(k):.1f}" y="{H-Bm+16}" text-anchor="middle" font-size="10.5" fill="#888">'
                f'{date_of(k).strftime("%b %-d")}</text>')

marks = []
band_ks = range(LAST, 18)
for p in CPARTS:
    col, pc = COLOR[p], PC[p]
    if LAST < 17:
        marks.append('<polygon points="' + ' '.join(f"{x(k):.1f},{y(pc[k][2]):.1f}" for k in band_ks) + ' '
                     + ' '.join(f"{x(k):.1f},{y(pc[k][1]):.1f}" for k in reversed(band_ks))
                     + f'" fill="{col}" fill-opacity=".13" stroke="none"/>')
    marks.append(pline(C22P[p], col, 1.6, dash='2 3', opacity=.75))
    marks.append(pline({k: pc[k][0] for k in pc}, col, 2, dash='5 4', first=LAST))
    marks.append(pline({k: pc[k][0] for k in pc}, col, 3.2, last=LAST))
    marks.append(f'<circle cx="{x(LAST):.1f}" cy="{y(pc[LAST][0]):.1f}" r="4" fill="{col}"/>')

# end labels, nudged apart so they never overlap
ends = sorted(((y(PC[p][17][0]), p) for p in CPARTS))
for i in range(1, len(ends)):
    if ends[i][0] - ends[i - 1][0] < 28:
        ends[i] = (ends[i - 1][0] + 28, ends[i][1])
for yy, p in ends:
    marks.append(f'<text x="{W-R+8}" y="{yy:.1f}" font-size="11.5" font-weight="600" fill="{COLOR[p]}">'
                 f'{WHO[p].split()[0].capitalize()}</text>'
                 f'<text x="{W-R+8}" y="{yy+13:.1f}" font-size="11" fill="{COLOR[p]}">{PC[p][17][0]/1000:,.0f}k</text>')

chart = f'''<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="Cumulative in-person early votes by party, projected, with 2022">
{''.join(grid)}
{''.join(marks)}
<text x="{L}" y="12" font-size="11" fill="#777">cumulative in-person early votes, by party registration</text>
</svg>'''

# --- callout --------------------------------------------------------------
nxt = list(range(LAST + 1, min(LAST + 4, 18)))
if nxt:
    watch = (f'<b>What to watch.</b> Day {nxt[0]} ({date_of(nxt[0]).strftime("%a %b %-d")}) is next: '
             f'expect about <b>{C["day"][nxt[0]][0]:,}</b> votes '
             f'(90% range {C["day"][nxt[0]][1]:,}&ndash;{C["day"][nxt[0]][2]:,}).')
elif LAST < 17:
    watch = '<b>No data yet today.</b>'
else:
    watch = ('<b>Early voting has closed.</b> The forecasts below are final; the scorecard shows how they did '
             'against each day as it arrived.')

if cerrs:
    track = (f'<div class="note"><b>Track record.</b> {len(cerrs)} day(s) scored against the forecast issued the day before: '
             f'mean absolute error <b>{c_mae:,.0f}</b> votes per day, and <b>{c_in} of {len(cerrs)}</b> landed inside the 90% range.</div>')
elif rerrs:
    track = (f'<div class="note"><b>Track record.</b> No issued forecast has been scored yet. Replayed on days '
             f'{rerrs[0][0]}&ndash;{rerrs[-1][0]} using only the data available the night before, the forecast missed by '
             f'{sum(abs(a - m) for _, a, m, _ in rerrs) / len(rerrs):,.0f} votes a day on average, and '
             f'{r_in} of {len(rerrs)} days landed inside the 90% range.</div>')
else:
    track = ('<div class="note"><b>No scored days yet.</b> The first forecast was issued after day '
             f'{sorted(VIN)[0] if VIN else LAST}; accuracy appears once a full day has passed.</div>')

stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NC early voting 2026 &mdash; daily tracker</title>
<meta name="description" content="Rolling forecasts of North Carolina in-person early voting, scored against what actually happened.">
<style>
:root{{--ink:#1a1a1a;--mut:#666;--line:#e6e6e6;--blue:#2b6cb0;--deep:#12395c;--orange:#c05621;
--green:#1a6b3c;--red:#9b2c2c;--bg:#fbfbfc}}
*{{box-sizing:border-box}}
body{{margin:0;font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;color:var(--ink);background:var(--bg)}}
.wrap{{max-width:900px;margin:0 auto;padding:32px 20px 64px}}
header.top{{border-bottom:1px solid var(--line);padding-bottom:14px;margin-bottom:26px}}
h1{{font-size:26px;margin:0 0 3px;letter-spacing:-.3px}}
.sub{{color:var(--mut);font-size:13.5px}}
nav a{{color:var(--blue);text-decoration:none;font-size:13.5px;margin-right:16px}}
nav a:hover{{text-decoration:underline}}
.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:22px 0 6px}}
.card{{background:#fff;border:1px solid var(--line);border-radius:8px;padding:13px 14px}}
.card .k{{font-size:11.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--mut);margin-bottom:5px}}
.card .v{{font-size:23px;font-weight:650;letter-spacing:-.5px}}
.card .n{{font-size:12px;color:var(--mut);margin-top:3px}}
h2{{font-size:17px;margin:38px 0 6px;padding-bottom:6px;border-bottom:1px solid var(--line)}}
p{{margin:9px 0}}
table{{border-collapse:collapse;width:100%;font-size:13.5px;margin:12px 0}}
th,td{{padding:6px 8px;border-bottom:1px solid #efefef;text-align:right;white-space:nowrap}}
th:first-child,td:first-child,th:nth-child(2),td:nth-child(2),th:nth-child(3),td:nth-child(3){{text-align:left}}
th{{background:#f5f6f8;font-weight:600;font-size:12.5px;color:#444}}
tr.future td{{color:#9aa3ad}}
.rng{{color:var(--mut);font-size:12px}}
.neg{{color:var(--orange)}} .pos{{color:var(--green)}} td.out{{font-weight:700}}
table.err td:nth-child(n+3){{font-variant-numeric:tabular-nums}}
.hi{{color:var(--green);font-weight:600}} .lo{{color:var(--red);font-weight:600}} .ok{{color:#555}}
.note{{background:#fff;border:1px solid var(--line);border-left:3px solid var(--blue);border-radius:4px;padding:11px 14px;font-size:13.5px;margin:18px 0}}
.legend{{font-size:12px;color:#555;margin:2px 0 8px;display:flex;flex-wrap:wrap;gap:14px}}
.legend i{{display:inline-block;width:16px;height:3px;vertical-align:middle;margin-right:5px;border-radius:2px}}
.dot{{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:7px}}
.dot.dem{{background:var(--blue)}} .dot.rep{{background:var(--red)}} .dot.una{{background:#8a8f98}} .dot.oth{{background:#c9a227}}
tr.tot td{{border-top:2px solid #ddd;font-weight:600}}
table.party td{{vertical-align:top}}
table.party td:nth-child(n+2),table.party th:nth-child(n+2){{text-align:right}}
.finish{{margin:44px 0 10px;padding:22px 22px 14px;background:#fff;border:1px solid var(--line);border-top:4px solid var(--deep);border-radius:8px}}
.finish .fk{{font-size:12px;text-transform:uppercase;letter-spacing:.07em;color:var(--mut);margin-bottom:12px}}
.duel{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.side .who{{font-size:13px;font-weight:600}} .side.dem .who{{color:var(--blue)}} .side.rep .who{{color:var(--red)}}
.side.rep{{text-align:right}}
.side .big{{font-size:44px;font-weight:700;letter-spacing:-1.5px;line-height:1.1}}
.side.dem .big{{color:var(--blue)}} .side.rep .big{{color:var(--red)}}
.bar{{position:relative;display:flex;height:14px;border-radius:7px;overflow:hidden;margin:14px 0 10px}}
.bar .bd{{background:var(--blue)}} .bar .br{{background:var(--red)}}
.bar i{{position:absolute;top:-3px;bottom:-3px;width:2px;background:#fff}}
.finish .margin{{font-size:17px;text-align:center}}
.finish .was{{font-size:13px;color:var(--mut);text-align:center;margin:4px 0 10px}}
@media(max-width:640px){{.side .big{{font-size:32px}}}}
footer{{margin-top:44px;padding-top:14px;border-top:1px solid var(--line);font-size:12px;color:var(--mut)}}
@media(max-width:640px){{.cards{{grid-template-columns:repeat(2,1fr)}}h1{{font-size:21px}}table{{display:block;overflow-x:auto}}.finish{{padding:16px 14px 10px}}}}
</style></head><body><div class="wrap">
<header class="top">
<h1>North Carolina early voting, 2026</h1>
<div class="sub">In-person early votes through <b>{THROUGH.strftime('%B %-d, %Y')}</b> &middot; day {LAST} of 17 &middot; {DAYS_TO_GO} days left &middot; model re-estimated each run</div>
<nav style="margin-top:9px"><a href="./">Tracker</a><a href="report.html">Full report</a><a href="data.json">Data</a></nav>
</header>

<div class="cards">
<div class="card"><div class="k">Banked so far</div><div class="v">{BANKED:,}</div><div class="n">in-person early votes</div></div>
<div class="card"><div class="k">Projected total</div><div class="v">{MID/1e6:.2f}M</div><div class="n">90% range {MLO/1e6:.2f}&ndash;{MHI/1e6:.2f}M</div></div>
<div class="card"><div class="k">Change vs 2022</div><div class="v">{signed(TOT_CHANGE[0])}</div><div class="n">range {signed(TOT_CHANGE[1])} to {signed(TOT_CHANGE[2])}</div></div>
<div class="card"><div class="k">Dem share of D+R</div><div class="v">{DSHARE[0]:.1f}%</div><div class="n">range {DSHARE[1]:.1f}&ndash;{DSHARE[2]:.1f}% &middot; 2022: {DSHARE22:.1f}%</div></div>
</div>

<div class="note">{watch}</div>
{track}

<h2>Projected early vote by party</h2>
<div class="legend">
<span><i style="background:var(--blue)"></i>Democrats</span>
<span><i style="background:var(--red)"></i>Republicans</span>
<span><i style="background:#6b7280"></i>Unaffiliated</span>
</div>
{chart}
<div class="sub" style="margin:2px 0 14px">Cumulative in-person early votes by party registration. Solid lines are 2026 so far, dashed lines the forecast with its 90% range shaded, and dotted lines 2022 on the same day of early voting. Libertarian and other voters (about 1%) are left out.</div>

<h2>Prediction vs actual</h2>

<table>
<tr><th>Day</th><th>Date</th><th>Forecast</th><th>90% range</th><th>Actual</th><th>Act/Fcst</th></tr>
{scorecard}
</table>
<p class="sub">Past rows show the forecast issued after the previous day's data, with the ratio in green or red when the actual fell outside the range. Future rows use the current estimate. &#8224; Replayed: the same model run on data through the previous day, after the fact, not a forecast issued at the time.</p>

<h2>Daily miss by party</h2>
<table class="err">
<tr><th>Day</th><th>Date</th><th>Democrats</th><th>Republicans</th><th>Unaffiliated</th><th>Total</th></tr>
{error_table}
</table>
<p class="sub">Actual votes minus the forecast made the night before, using data through the previous day: <span class="neg">&minus;</span> means fewer votes than forecast, <span class="pos">+</span> more. Bold marks a day outside the 90% range; hover a cell for the numbers. A run of minus signs in one column means the model keeps overestimating that group, and its trend is drifting down. &#8224; Replayed after the fact; per-party forecasts were recorded from day {FIRST_PD} on.</p>

<h2>By party, compared with 2022</h2>
<table class="party">
<tr><th>Party</th><th>2022 final</th><th>2026 forecast</th><th>Change</th><th>2022 share</th><th>2026 share</th></tr>
{party_table}
</table>
<p class="sub">Votes cast by voters registered with each party, across all 17 days of in-person early voting. Ranges are 90% intervals.</p>
<p>{party_text}</p>

{geo_section}{finish}<h2>Method</h2>
<p>Every run re-estimates the forecast from all days observed so far. For each party it fits a trend to the 2026 multiple of the prior cycle across the weekdays seen so far (weekends move with site schedules), then extends that trend against 2022's remaining days and, separately, 2024's. The two cycles disagree about the final stretch, with 2022 ending in a surge and 2024 front-loaded, so the forecast splits the difference. The 90% ranges come from 4,000 simulations that redraw each trend from its sampling error, let the late-period shape land anywhere from one cycle's profile to past the other's, and add day-to-day noise at the size the fit has shown so far. Shares and changes are computed within each simulation, so their ranges reflect how the parties move together.</p>
<p>Each run records the forecast it issued in <code>data/vintages.json</code>, keyed by the last day of data it had seen, and every day is scored against the forecast issued the night before, so a revised model is never graded on hindsight. All three cycles open on a Thursday and close on a Saturday, so days need no weekday adjustment. The full eight-section analysis is in the <a href="report.html">report</a>.</p>

<footer>Built {stamp}. Source: NCSBE ENRS daily absentee files. Party registration is not vote choice; the vote projection assumes 2022 behavior and covers early votes only.</footer>
</div></body></html>'''

os.makedirs('_site', exist_ok=True)
open('_site/index.html', 'w').write(page)

rep = open('analysis/nc_early_voting_2026.html').read()
rep = rep.replace('<h1>', '<p style="margin:0 0 14px"><a href="./" style="color:#2b6cb0;text-decoration:none">'
                        '&larr; Daily tracker</a></p>\n<h1>', 1)
open('_site/report.html', 'w').write(rep)

json.dump({
    'through': str(THROUGH), 'last_day': LAST, 'banked': BANKED,
    'projection': {'total': MID, 'total_90': [MLO, MHI],
                   'change_vs_2022_pct': [round(v, 1) for v in TOT_CHANGE],
                   'dem_two_party_share_pct': [round(v, 1) for v in DSHARE],
                   'dem_two_party_share_2022_pct': round(DSHARE22, 1)},
    'party': {p: {'final_2022': F22[p], 'banked': BANK[p],
                  'forecast': C['party'][p][0], 'forecast_90': list(C['party'][p][1:]),
                  'change_vs_2022_pct': [round(v, 1) for v in CHANGE[p]],
                  'share_pct': [round(v, 1) for v in SHARE[p]],
                  'share_2022_pct': round(100 * F22[p] / T22, 1)} for p in PARTS},
    'vote_projection': None if not VC else {
        'dem': VC['dem'], 'rep': VC['rep'], 'margin': VC['margin'],
        'dem_two_party_pct': [round(v, 1) for v in VC['dem_share']],
        'actual_2022_dem_rep': VC['actual_2022']},
    'unaffiliated_geography': None if not GEO else {
        'bins': GEO['rows'],
        'una_rep_share_shift_pts': [round(100 * (b - a), 2) for a, b in GEO['shifts']],
        'una_growth_same_days': round(GEO['una_growth'], 3)},
    'daily_error_by_party': ERR,
    'daily': [{'day': k, 'date': str(date_of(k)),
               'forecast': C['day'][k][0] if k > LAST else None,
               'forecast_90': [C['day'][k][1], C['day'][k][2]] if k > LAST else None,
               'actual': obs[k]['total'] if k <= LAST else None}
              for k in range(1, 18)],
}, open('_site/data.json', 'w'), indent=1)

print(f"built _site/  day {LAST}/17  banked {BANKED:,}  forecast {MID:,} [{MLO:,}-{MHI:,}]  "
      f"D share {DSHARE[0]:.1f}% [{DSHARE[1]:.1f}-{DSHARE[2]:.1f}]")
