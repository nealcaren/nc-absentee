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


def vote_choice(base, counties26, party_point, party_sims, swing_sd=0.015, seed=7):
    """Projected Democratic and Republican early votes.

    Applies 2022 behavior to the forecast electorate: partisans with crossover d
    and defection q, and unaffiliated voters at their county's 2022 rate weighted
    by where 2026's unaffiliated voters live. Each draw pairs one turnout draw
    with a loyalty draw (d up to 12%, q up to 6%) and a uniform swing in the
    Republican share (sd 1.5 points, about the gap between applying 2022 and 2024
    behavior to the same electorate), since 2026 voters need not vote like 2022's.
    Votes are two-party, scaled by 2022's two-party votes per early voter.
    Returns (dem, rep, margin) as (mid, lo, hi) and the Democratic two-party share.
    """
    import random
    from central import band
    cs = [c for c in base['counties'] if c in counties26]
    full = {c: _sum(base['counties'][c]['days']) for c in cs}
    res = {c: base['counties'][c]['result'] for c in cs}
    f_state = sum(res[c]['R'] + res[c]['D'] for c in cs) / sum(sum(full[c].values()) for c in cs)
    w = {c: counties26[c].get('UNA', 0) for c in cs}

    def u_eff(d, q):
        num = 0.0
        for c in cs:
            n = sum(full[c].values())
            f = (res[c]['R'] + res[c]['D']) / n
            x = (res[c]['R'] / f - d * full[c].get('DEM', 0) - (1 - q) * full[c].get('REP', 0)
                 - .5 * full[c].get('OTH', 0)) / max(full[c].get('UNA', 0), 1)
            num += w[c] * min(max(x, .02), .98)
        return num / sum(w.values())

    def split(P, d, q, u, s=0.0):
        n = f_state * sum(P.values())
        rep = f_state * (d * P['DEM'] + (1 - q) * P['REP'] + u * P['UNA'] + .5 * P['OTH']) + s * n
        return n - rep, rep

    d0, q0 = LOYALTY[1]
    dem0, rep0 = split(party_point, d0, q0, u_eff(d0, q0))
    rng = random.Random(seed)
    dem_d, rep_d, mar_d, sh_d = [], [], [], []
    for i in range(len(party_sims['DEM'])):
        d, q = rng.uniform(0, .12), rng.uniform(0, .06)
        P = {g: party_sims[g][i] for g in party_sims}
        dem, rep = split(P, d, q, u_eff(d, q), rng.gauss(0, swing_sd))
        dem_d.append(dem); rep_d.append(rep); mar_d.append(dem - rep); sh_d.append(100 * dem / (dem + rep))
    r = lambda xs, m: tuple(round(v) for v in band(xs, m))
    return {'dem': r(dem_d, dem0), 'rep': r(rep_d, rep0), 'margin': r(mar_d, dem0 - rep0),
            'dem_share': band(sh_d, 100 * dem0 / (dem0 + rep0)),
            'actual_2022': (sum(res[c]['D'] for c in cs), sum(res[c]['R'] for c in cs))}
