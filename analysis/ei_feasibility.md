# Feasibility: ecological inference from NC results + absentee files

## Join quality
| Level | Result |
|---|---|
| County | **Validated.** Results "One Stop" totals vs absentee accepted in-person: 0.5% median discrepancy across all 100 counties (statewide 2,003,761 vs 2,010,890). |
| Precinct | **Fails.** Only 635 of 2,928 results precincts (21.7%) match absentee `precinct_desc` after normalization. Many counties use numeric codes in results (`01`, `035`, `03C`) and names in the absentee file (`BURLINGTON 4`). A crosswalk is required. |

## Ecological regression attempt (2022 US Senate, One Stop voters only)
Dependent variable: Republican share of One Stop Senate vote by county.
Regressor: racial composition of One Stop voters by county (from absentee file).

| Specification | Black REP share | Non-Black REP share | Note |
|---|---|---|---|
| 3-group Goodman, unweighted | 0.223 | 0.750 | intercept = -0.613, impossible |
| 2-group, unweighted | 0.122 | 0.664 | implied statewide 0.560 vs actual 0.473 |
| 2-group, weighted | -0.013 | 0.588 | negative rate, impossible |
| 2-group, constrained [0,1], unweighted | 0.560 | 0.560 | collapses to no group difference |
| 2-group, constrained [0,1], weighted | 0.470 | 0.470 | collapses to no group difference |

Actual statewide One Stop Senate result: REP 47.3%.

**Conclusion:** estimates span 0 to 0.75 depending on specification. The county-level design does not identify group-level rates.

## Why it fails
- Only 98 usable aggregate units.
- Between-county variation in racial composition is collinear with urban/rural partisanship.
- The regressor (composition of early voters) is itself a function of the turnout process being studied.

## What is required for a credible design
1. NCSBE voter registration file (individual-level: race, party, age, precinct) — supplies the missing denominators.
2. NCSBE precinct lookup / crosswalk — enables the precinct-level join (~2,928 units).
3. 2024 results — out-of-sample validation.
4. Site addresses/coordinates and hours — the treatment variable.
5. 2026 results after Nov 3 — otherwise any "prediction" is an unvalidated forecast.

## Key point
With registration denominators, early-vote **turnout rates by race** are computed directly (early voters by race / registered voters by race). Ecological inference is not needed for that. EI is only needed to allocate **Election Day** voters by race, or to estimate **vote choice** by group.

## King (1997) deterministic bounds applied to this data

Using the same 2022 One Stop Senate data, with X = Black share of One Stop voters and
T = Republican share of One Stop votes:

| Units | Weighted bounds on Black Republican share | Median unit bound width |
|---|---|---|
| 97 counties | [0.000, 0.938] | 1.000 |
| 236 matched precincts (10 counties) | [0.000, 0.741] | 1.000 |

The bounds are vacuous: the data are consistent with anything from 0% to 94% of Black
early voters supporting Budd. This is King's own diagnostic showing the aggregate units
carry almost no identifying information.

Source of method and examples: King, Gary. 1997. *A Solution to the Ecological Inference
Problem*. Princeton University Press. Replication archive: doi:10.7910/DVN/XXGY0B.
Note the archived EI 1.0 program is Gauss source from 1995 and will not run today; use
`eiPack` or `ei` in R, or `pyei` in Python.
