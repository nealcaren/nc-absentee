"""Central forecast with a 90% interval.

For each party group, the 2026 multiple of a prior cycle is fit as a log-linear
trend across the weekdays observed so far (weekends move with site schedules and
are left out of the fit). The trend is extrapolated against two baselines, 2022
and 2024, whose late-period shapes differ: 2022 closed with a surge, 2024 was
front-loaded. The central estimate splits the difference in logs.

The interval comes from simulation. Each draw
  - redraws every group's trend level and slope from their sampling error,
  - blends the two baselines with weight 0.5 + z/2, z ~ N(0,1), shared across
    days and groups, so the draw can sit beyond either cycle's profile,
  - adds day-level noise at the size of the fit's residuals (larger on weekends).
Day and total intervals are the 5th and 95th percentiles of the draws.
"""
import math, random

GROUPS = {'DEM': ['DEM'], 'REP': ['REP'], 'UNA': ['UNA'], 'OTH': ['LIB', 'OTH']}
WEEKEND = {3, 4, 10, 11}
N_DAYS = 17


def _g(day, grp):
    return sum(day.get(p, 0) for p in GROUPS[grp])


def _fit(obs, base, grp, last):
    """OLS of log(2026/base) on day over observed weekdays.
    Returns (level at `last`, slope, var(level), var(slope), resid sd, weekend sd)."""
    ks = [k for k in range(1, last + 1) if k not in WEEKEND and _g(base[k], grp) and _g(obs[k], grp)]
    r = {k: math.log(_g(obs[k], grp) / _g(base[k], grp)) for k in ks}
    n = len(ks)
    mx, my = sum(ks) / n, sum(r.values()) / n
    sxx = sum((k - mx) ** 2 for k in ks)
    b = sum((k - mx) * (r[k] - my) for k in ks) / sxx if n >= 3 and sxx else 0.0
    res = [r[k] - my - b * (k - mx) for k in ks]
    s2 = sum(e * e for e in res) / max(n - 2, 1)
    wk = [math.log(_g(obs[k], grp) / _g(base[k], grp)) - my - b * (k - mx)
          for k in range(1, last + 1) if k in WEEKEND and _g(base[k], grp) and _g(obs[k], grp)]
    s_wk = max(math.sqrt(s2), math.sqrt(sum(e * e for e in wk) / len(wk))) if wk else 2 * math.sqrt(s2)
    lvl = my + b * (last - mx)
    var_lvl = s2 / n + (last - mx) ** 2 * s2 / sxx if sxx else s2 / n
    var_b = s2 / sxx if sxx else 0.0
    return lvl, b, var_lvl, var_b, math.sqrt(s2), s_wk


def band(xs, mid):
    """Point estimate with the 5th and 95th percentiles of the draws."""
    xs = sorted(xs)
    return mid, xs[int(0.05 * len(xs))], xs[int(0.95 * len(xs)) - 1]


def central(obs, b22, b24, last, sims=4000):
    """Returns {'day': {k: (mid, lo, hi)}, 'cum': {k: (mid, lo, hi)},
    'total': (mid, lo, hi), 'party': {grp: (mid, lo, hi)},
    'party_cum': {grp: {k: (mid, lo, hi)}},
    'party_point': {grp: mid}, 'party_sims': {grp: [draw, ...]}} for the full 17 days.
    Draws in party_sims are aligned, so functions of several parties (shares)
    can be banded with band()."""
    bases = (b22, b24)
    fits = {grp: [_fit(obs, B, grp, last) for B in bases] for grp in GROUPS}
    future = list(range(last + 1, N_DAYS + 1))
    banked = {grp: sum(_g(obs[k], grp) for k in range(1, last + 1)) for grp in GROUPS}

    def path(grp, z, draws, noise):
        out = {}
        for k in future:
            logs = [lvl + b * (k - last) + math.log(_g(B[k], grp))
                    for (lvl, b), B in zip(draws, bases)]
            mid = (logs[0] + logs[1]) / 2
            out[k] = math.exp(mid + z * (logs[0] - logs[1]) / 2 + noise.get(k, 0.0))
        return out

    point = {grp: path(grp, 0.0, [f[:2] for f in fits[grp]], {}) for grp in GROUPS}

    rng = random.Random(last)
    day_draws = {k: [] for k in future}
    cum_draws = {k: [] for k in future}
    party_draws = {grp: [] for grp in GROUPS}
    pcum_draws = {grp: {k: [] for k in future} for grp in GROUPS}
    for _ in range(sims):
        z = rng.gauss(0, 1)
        per_day = {k: 0.0 for k in future}
        for grp in GROUPS:
            draws = [(lvl + rng.gauss(0, math.sqrt(vl)), b + rng.gauss(0, math.sqrt(vb)))
                     for lvl, b, vl, vb, _, _ in fits[grp]]
            s, s_wk = fits[grp][0][4], fits[grp][0][5]
            noise = {k: rng.gauss(0, s_wk if k in WEEKEND else s) for k in future}
            p = path(grp, z, draws, noise)
            party_draws[grp].append(banked[grp] + sum(p.values()))
            prun = banked[grp]
            for k in future:
                per_day[k] += p[k]
                prun += p[k]
                pcum_draws[grp][k].append(prun)
        run = sum(banked.values())
        for k in future:
            day_draws[k].append(per_day[k])
            run += per_day[k]
            cum_draws[k].append(run)

    def rband(xs, mid):
        return tuple(round(v) for v in band(xs, mid))

    day, cum = {}, {}
    run = 0
    for k in range(1, N_DAYS + 1):
        if k <= last:
            v = obs[k]['total']
            day[k] = (v, v, v)
            run += v
            cum[k] = (run, run, run)
        else:
            mid = sum(point[grp][k] for grp in GROUPS)
            day[k] = rband(day_draws[k], mid)
            run += mid
            cum[k] = rband(cum_draws[k], run)
    party_cum = {}
    for grp in GROUPS:
        run, party_cum[grp] = 0, {}
        for k in range(1, N_DAYS + 1):
            if k <= last:
                run += _g(obs[k], grp)
                party_cum[grp][k] = (run, run, run)
            else:
                run += point[grp][k]
                party_cum[grp][k] = rband(pcum_draws[grp][k], run)
    party_point = {grp: banked[grp] + sum(point[grp].values()) for grp in GROUPS}
    if not future:
        party_draws = {grp: [banked[grp]] for grp in GROUPS}
    party = {grp: rband(party_draws[grp], party_point[grp]) for grp in GROUPS}
    return {'day': day, 'cum': cum, 'total': cum[N_DAYS], 'party': party, 'party_cum': party_cum,
            'party_point': party_point, 'party_sims': party_draws}
