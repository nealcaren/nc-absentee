"""Where unaffiliated early voters are coming from, and what that implies.

County results cannot say how unaffiliated voters break statewide: the same
2022 total fits anything from about 35% to 60% Republican, depending on how
loyal partisans are assumed to be. They can say how each county's unaffiliated
voters broke relative to the others. Holding those county rates fixed and
re-weighting them by where 2026's unaffiliated voters live gives the shift in
the statewide break due to geography alone, and that shift barely moves with
the loyalty assumption.

For each county c, with D, R, U, O early voters and 2022 Senate One Stop votes,
the unaffiliated Republican rate solves
    votes_R = f * (d*D + (1-q)*R + u_c*U + O/2),   f = two-party votes / voters
for Democratic crossover d and Republican defection q. 2026 is compared with
the same days of 2022, so the comparison is not distorted by who votes early.
"""

LOYALTY = [(0.0, 0.0), (0.06, 0.03), (0.12, 0.06)]     # (Dem crossover, Rep defection); middle is the headline
BINS = [(0, .40, 'Strongly Democratic', 'R share under 40%'),
        (.40, .50, 'Lean Democratic', '40&ndash;50%'),
        (.50, .60, 'Lean Republican', '50&ndash;60%'),
        (.60, 1.01, 'Strongly Republican', '60% or more')]


def _sum(days, upto=None):
    out = {}
    for k, v in days.items():
        if upto is None or int(k) <= upto:
            for g, n in v.items():
                out[g] = out.get(g, 0) + n
    return out


def geography(base, counties26, last):
    cs = [c for c in base['counties'] if c in counties26]
    full = {c: _sum(base['counties'][c]['days']) for c in cs}
    same = {c: _sum(base['counties'][c]['days'], last) for c in cs}
    res = {c: base['counties'][c]['result'] for c in cs}
    lean = {c: res[c]['R'] / (res[c]['R'] + res[c]['D']) for c in cs}

    u22 = sum(same[c].get('UNA', 0) for c in cs)
    u26 = sum(counties26[c].get('UNA', 0) for c in cs)
    rows = []
    for lo, hi, label, note in BINS:
        b = [c for c in cs if lo <= lean[c] < hi]
        a22 = sum(same[c].get('UNA', 0) for c in b)
        a26 = sum(counties26[c].get('UNA', 0) for c in b)
        rows.append({'label': label, 'note': note, 'counties': len(b),
                     'share_2022': a22 / u22, 'share_2026': a26 / u26,
                     'growth': a26 / a22 if a22 else None})

    shifts = []
    for d, q in LOYALTY:
        u = {}
        for c in cs:
            n = sum(full[c].values())
            f = (res[c]['R'] + res[c]['D']) / n
            x = (res[c]['R'] / f - d * full[c].get('DEM', 0) - (1 - q) * full[c].get('REP', 0)
                 - .5 * full[c].get('OTH', 0)) / max(full[c].get('UNA', 0), 1)
            u[c] = min(max(x, .02), .98)
        w22 = sum(same[c].get('UNA', 0) * u[c] for c in cs) / u22
        w26 = sum(counties26[c].get('UNA', 0) * u[c] for c in cs) / u26
        shifts.append((w22, w26))

    growth = {c: counties26[c].get('UNA', 0) / same[c]['UNA'] for c in cs if same[c].get('UNA', 0) >= 2000}
    return {'rows': rows, 'shifts': shifts, 'lean': lean, 'growth': growth,
            'una_growth': u26 / u22}
