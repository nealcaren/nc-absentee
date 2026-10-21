#!/usr/bin/env python3
"""Build the static tracker site.

The forecast is re-estimated on every run from all days observed so far. To keep
the scorecard honest, every run also appends the forecast it just issued to
data/vintages.json, keyed by the last day of data it had seen. A day's accuracy
is then measured against the vintage issued immediately before it, never against
a model that has since seen the answer.

Outputs _site/index.html, _site/report.html, _site/data.json.
Standard library only.
"""
import json, os, datetime

BASE = json.load(open('data/baseline.json'))
OBS = json.load(open('data/observed.json'))
VIN_PATH = 'data/vintages.json'
VIN = json.load(open(VIN_PATH)) if os.path.exists(VIN_PATH) else {}

ELECTION = datetime.date.fromisoformat(OBS['election'])
PARTS = ['DEM', 'REP', 'UNA']
LABEL = {'DEM': 'Democrat', 'REP': 'Republican', 'UNA': 'Unaffiliated'}
ALL = PARTS + ['OTH']
LAST = int(OBS['last_day'])
THROUGH = datetime.date.fromisoformat(OBS['through'])
DAYS_TO_GO = 17 - LAST

b22 = {int(k): v for k, v in BASE['days']['2022'].items()}
b24 = {int(k): v for k, v in BASE['days']['2024'].items()}
obs = {int(k): v for k, v in OBS['days'].items()}
T22 = sum(v['total'] for v in b22.values())
T24 = sum(v['total'] for v in b24.values())
BANKED = sum(obs[k]['total'] for k in range(1, LAST + 1))


def date_of(k):
    return ELECTION - datetime.timedelta(days=20 - k)


def ratio(part, days):
    """2026 / 2022 for a party over a set of days."""
    num = sum(obs[k][part] for k in days)
    den = sum(b22[k][part] for k in days)
    return num / den if den else 0.0


# --- pace estimates -------------------------------------------------------
S = {p: ratio(p, range(1, LAST + 1)) for p in ALL + ['total']}            # cumulative
RECENT = {p: ratio(p, range(max(1, LAST - 2), LAST + 1)) for p in ALL + ['total']}  # trailing 3 days


def s_low(part, k):
    """Lower bound: the surge stops after the last observed day."""
    return 1.0


def forecast(kind):
    out = {}
    for k in range(1, 18):
        if k <= LAST:
            out[k] = obs[k]['total']
        elif kind == 'high':
            out[k] = sum(round(b22[k][p] * S[p]) for p in ALL)
        else:
            out[k] = sum(round(b22[k][p] * s_low(p, k)) for p in ALL)
    return out


def forecast_party(part, kind):
    out = {}
    for k in range(1, 18):
        if k <= LAST:
            out[k] = obs[k][part]
        elif kind == 'high':
            out[k] = round(b22[k][part] * S[part])
        else:
            out[k] = round(b22[k][part] * s_low(part, k))
    return out


HI, LO = forecast('high'), forecast('low')
TOT_HI, TOT_LO = sum(HI.values()), sum(LO.values())

# --- record this run's forecast ------------------------------------------
if LAST < 17:
    key = str(LAST)
    if key not in VIN:                      # keep the first forecast issued on a given information set
        VIN[key] = {
            'issued': str(datetime.date.today()),
            'last_day': LAST,
            'through': str(THROUGH),
            'high': {str(k): HI[k] for k in range(LAST + 1, 18)},
            'low': {str(k): LO[k] for k in range(LAST + 1, 18)},
            'total_high': TOT_HI, 'total_low': TOT_LO,
            'scales': {p: round(S[p], 4) for p in PARTS},
        }
        json.dump(VIN, open(VIN_PATH, 'w'), indent=1, sort_keys=True)


def vintage_pred(k):
    """The forecast for day k issued just before day k was observed."""
    v = VIN.get(str(k - 1))
    if not v:
        return None
    return v['high'].get(str(k)), v['low'].get(str(k))


# --- scorecard ------------------------------------------------------------
rows, errs = [], []
for k in range(1, 18):
    d, dow = date_of(k).strftime('%b %-d'), date_of(k).strftime('%a')
    if k <= LAST:
        act = obs[k]['total']
        vp = vintage_pred(k)
        if vp and vp[0]:
            ph, pl = vp
            rh, rl = act / ph, act / pl
            errs.append((k, act, ph, pl))
            cls = lambda r: 'ok' if 0.9 <= r <= 1.1 else ('hi' if r > 1.1 else 'lo')
            rows.append(f'<tr class="seen"><td>{k}</td><td>{d}</td><td>{dow}</td>'
                        f'<td>{ph:,}</td><td>{pl:,}</td><td><b>{act:,}</b></td>'
                        f'<td class="{cls(rh)}">{rh:.2f}</td><td class="{cls(rl)}">{rl:.2f}</td></tr>')
        else:
            rows.append(f'<tr class="seen"><td>{k}</td><td>{d}</td><td>{dow}</td>'
                        f'<td>&middot;</td><td>&middot;</td><td><b>{act:,}</b></td><td></td><td></td></tr>')
    else:
        rows.append(f'<tr class="future"><td>{k}</td><td>{d}</td><td>{dow}</td>'
                    f'<td>{HI[k]:,}</td><td>{LO[k]:,}</td><td>&middot;</td><td></td><td></td></tr>')
scorecard = '\n'.join(rows)

mae = sum(abs(a - p) for _, a, p, _ in errs) / len(errs) if errs else None
bias = sum(a - p for _, a, p, _ in errs) / len(errs) if errs else None
mean_ratio = sum(a / p for _, a, p, _ in errs) / len(errs) if errs else None

# --- party table ----------------------------------------------------------
prow = []
for p in PARTS:
    bank = sum(obs[k][p] for k in range(1, LAST + 1))
    a, b = sum(forecast_party(p, 'high').values()), sum(forecast_party(p, 'low').values())
    prow.append(f'<tr><td><span class="dot {p.lower()}"></span>{LABEL[p]}</td><td>{bank:,}</td>'
                f'<td class="{"hi" if S[p] > 1.15 else ""}">{S[p]:.2f}&times;</td>'
                f'<td class="{"lo" if RECENT[p] < S[p] - 0.12 else ""}">{RECENT[p]:.2f}&times;</td>'
                f'<td>{a:,}</td><td>{b:,}</td></tr>')
party_table = '\n'.join(prow)

dem_bank = sum(obs[k]['DEM'] for k in range(1, LAST + 1))
rep_bank = sum(obs[k]['REP'] for k in range(1, LAST + 1))
bank_share = 100 * dem_bank / (dem_bank + rep_bank)
A_D, A_R = sum(forecast_party('DEM', 'high').values()), sum(forecast_party('REP', 'high').values())
B_D, B_R = sum(forecast_party('DEM', 'low').values()), sum(forecast_party('REP', 'low').values())
share_H = 100 * A_D / (A_D + A_R)
share_L = 100 * B_D / (B_D + B_R)

# --- chart ----------------------------------------------------------------
W, H, L, R, T, Bm = 860, 330, 66, 18, 18, 40


def cum(d):
    out, run = {}, 0
    for k in range(1, 18):
        run += d.get(k, 0)
        out[k] = run
    return out


CHI, CLO = cum(HI), cum(LO)
C22, C24 = cum({k: b22[k]['total'] for k in b22}), cum({k: b24[k]['total'] for k in b24})
COBS = cum({k: obs[k]['total'] for k in obs})
MAXV = max(CHI[17], CLO[17], C24[17]) * 1.06


def x(k):
    return L + (k - 1) / 16 * (W - L - R)


def y(v):
    return H - Bm - v / MAXV * (H - T - Bm)


def pline(series, color, width=2, dash=None, last=None):
    ks = [k for k in sorted(series) if last is None or k <= last]
    pts = ' '.join(f"{x(k):.1f},{y(series[k]):.1f}" for k in ks)
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}"'
            f' stroke-linejoin="round"{d}/>')


grid = []
step = 1_000_000
for v in range(0, int(MAXV) + 1, step):
    grid.append(f'<line x1="{L}" y1="{y(v):.1f}" x2="{W-R}" y2="{y(v):.1f}" stroke="#e8e8e8"/>')
    grid.append(f'<text x="{L-8}" y="{y(v)+4:.1f}" text-anchor="end" font-size="10.5" fill="#888">{v/1e6:.0f}M</text>')
for k in (1, 5, 9, 13, 17):
    grid.append(f'<text x="{x(k):.1f}" y="{H-Bm+16}" text-anchor="middle" font-size="10.5" fill="#888">'
                f'{date_of(k).strftime("%b %-d")}</text>')

chart = f'''<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="Cumulative in-person early votes">
{''.join(grid)}
{pline(C24, '#cfd6dd', 2)}
{pline(C22, '#9aa5b1', 2)}
{pline(CHI, '#2b6cb0', 2, dash='5 4')}
{pline(CLO, '#c05621', 2, dash='2 4')}
{pline(COBS, '#12395c', 3.2, last=LAST)}
<circle cx="{x(LAST):.1f}" cy="{y(COBS[LAST]):.1f}" r="4" fill="#12395c"/>
<text x="{L}" y="12" font-size="11" fill="#777">cumulative in-person early votes</text>
</svg>'''

# --- callout --------------------------------------------------------------
nxt = list(range(LAST + 1, min(LAST + 4, 18)))
if nxt:
    watch = (f'<b>What to watch.</b> Day {nxt[0]} ({date_of(nxt[0]).strftime("%b %-d")}) is next. '
             f'The persistent path expects {", ".join(f"{HI[k]:,}" for k in nxt)}; '
             f'the fading path expects {", ".join(f"{LO[k]:,}" for k in nxt)}.')
elif LAST < 17:
    watch = '<b>No data yet today.</b>'
else:
    watch = ('<b>Early voting has closed.</b> The forecasts below are final; the scorecard shows how they did '
             'against each day as it arrived.')

if errs:
    track = (f'<div class="note"><b>Track record.</b> {len(errs)} day(s) scored against the forecast issued the day before. '
             f'Mean absolute error <b>{mae:,.0f}</b> votes per day; average outcome was '
             f'<b>{mean_ratio:.2f}&times;</b> the persistent path, so the model was '
             f'{"too low" if bias > 0 else "too high"} by {abs(bias):,.0f} votes a day on average.</div>')
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
.hi{{color:var(--green);font-weight:600}} .lo{{color:var(--red);font-weight:600}} .ok{{color:#555}}
.note{{background:#fff;border:1px solid var(--line);border-left:3px solid var(--blue);border-radius:4px;padding:11px 14px;font-size:13.5px;margin:18px 0}}
.legend{{font-size:12px;color:#555;margin:2px 0 8px;display:flex;flex-wrap:wrap;gap:14px}}
.legend i{{display:inline-block;width:16px;height:3px;vertical-align:middle;margin-right:5px;border-radius:2px}}
.dot{{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:7px}}
.dot.dem{{background:var(--blue)}} .dot.rep{{background:var(--red)}} .dot.una{{background:#8a8f98}}
footer{{margin-top:44px;padding-top:14px;border-top:1px solid var(--line);font-size:12px;color:var(--mut)}}
@media(max-width:640px){{.cards{{grid-template-columns:repeat(2,1fr)}}h1{{font-size:21px}}}}
</style></head><body><div class="wrap">
<header class="top">
<h1>North Carolina early voting, 2026</h1>
<div class="sub">In-person early votes through <b>{THROUGH.strftime('%B %-d, %Y')}</b> &middot; day {LAST} of 17 &middot; {DAYS_TO_GO} days left &middot; model re-estimated each run</div>
<nav style="margin-top:9px"><a href="./">Tracker</a><a href="report.html">Full report</a><a href="data.json">Data</a></nav>
</header>

<div class="cards">
<div class="card"><div class="k">Banked so far</div><div class="v">{BANKED:,}</div><div class="n">in-person early votes</div></div>
<div class="card"><div class="k">Pace vs 2022</div><div class="v">{S['total']:.2f}&times;</div><div class="n">same days, 2022</div></div>
<div class="card"><div class="k">Projected total</div><div class="v">{TOT_LO/1e6:.2f}&ndash;{TOT_HI/1e6:.2f}M</div><div class="n">fading to persistent</div></div>
<div class="card"><div class="k">Democratic share</div><div class="v">{bank_share:.1f}%</div><div class="n">of banked D+R</div></div>
</div>

<div class="note">{watch}</div>
{track}

<h2>Prediction vs actual</h2>
<div class="legend">
<span><i style="background:#12395c"></i>2026 observed</span>
<span><i style="background:#2b6cb0"></i>persistent path</span>
<span><i style="background:#c05621"></i>surge-stops path</span>
<span><i style="background:#9aa5b1"></i>2022</span>
<span><i style="background:#cfd6dd"></i>2024</span>
</div>
{chart}
<div class="sub" style="margin:2px 0 14px">Cumulative in-person early votes. For days already observed, the forecast shown is the one issued the day before, not a revised model.</div>

<table>
<tr><th>Day</th><th>Date</th><th>Dow</th><th>Persistent</th><th>Surge stops</th><th>Actual</th><th>Act/Persist</th><th>Act/Stop</th></tr>
{scorecard}
</table>
<p class="sub">Ratios near 1.00 mean that day's forecast was accurate. Past rows use the vintage issued after the previous day's data; future rows use the current estimate.</p>

<h2>By party</h2>
<table>
<tr><th>Party</th><th>Banked</th><th>Pace vs 2022</th><th>Last 3 days</th><th>Persistent total</th><th>Fading total</th></tr>
{party_table}
</table>
<p>Republicans are tracking 2022 almost exactly; the increase is concentrated among Democrats and unaffiliated voters. The early two-party split lands at <b>{share_H:.1f}%</b> Democratic on the persistent path or <b>{share_L:.1f}%</b> on the surge-stops path, against 53.9% in 2022 and 48.9% in 2024.</p>

<h2>Method</h2>
<p>Every run recomputes each party's multiple of 2022 from all days observed so far, then applies it to 2022's remaining daily profile. The <b>persistent path</b> holds that multiple through the remaining days. The <b>surge-stops path</b> assumes the extra votes were pulled forward and the remaining days run at 2022's exact levels, so the two bracket the pull-forward question. The two bracket the pull-forward question: whether the surge is more turnout or the same voters voting earlier.</p>
<p>Because the model is re-estimated daily, each run also records the forecast it just issued in <code>data/vintages.json</code>, keyed by the last day of data it had seen. Accuracy is always scored against the vintage issued immediately before the day being scored, so a revised model can never be graded on hindsight. All three cycles open on a Thursday and close on a Saturday, so days-until-election needs no weekday adjustment. The full eight-section analysis is in the <a href="report.html">report</a>.</p>

<footer>Built {stamp}. Source: NCSBE ENRS daily absentee files. Party registration is not vote choice; these are turnout forecasts, not outcome forecasts.</footer>
</div></body></html>'''

os.makedirs('_site', exist_ok=True)
open('_site/index.html', 'w').write(page)

rep = open('analysis/nc_early_voting_2026.html').read()
rep = rep.replace('<h1>', '<p style="margin:0 0 14px"><a href="./" style="color:#2b6cb0;text-decoration:none">'
                        '&larr; Daily tracker</a></p>\n<h1>', 1)
open('_site/report.html', 'w').write(rep)

json.dump({
    'through': str(THROUGH), 'last_day': LAST, 'banked': BANKED,
    'pace_vs_2022': round(S['total'], 4),
    'projection': {'surge_stops': TOT_LO, 'persistent': TOT_HI},
    'scales': {p: round(S[p], 4) for p in PARTS},
    'recent_scales': {p: round(RECENT[p], 4) for p in PARTS},
    'accuracy': {'n': len(errs), 'mae': round(mae) if mae is not None else None,
                 'mean_ratio': round(mean_ratio, 3) if mean_ratio else None},
    'daily': [{'day': k, 'date': str(date_of(k)),
               'persistent': HI[k], 'fading': LO[k],
               'actual': obs[k]['total'] if k <= LAST else None,
               'dem_actual': obs[k]['DEM'] if k <= LAST else None,
               'rep_actual': obs[k]['REP'] if k <= LAST else None}
              for k in range(1, 18)],
}, open('_site/data.json', 'w'), indent=1)

if errs:
    print(f"built _site/  day {LAST}/17  banked {BANKED:,}  persistent {TOT_HI:,}  stops {TOT_LO:,}  "
          f"MAE {mae:,.0f} over {len(errs)} day(s)")
else:
    print(f"built _site/  day {LAST}/17  banked {BANKED:,}  persistent {TOT_HI:,}  stops {TOT_LO:,}  no scored days yet")
