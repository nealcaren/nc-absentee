# NC early voting 2026 — daily tracker

A live forecast of North Carolina in-person early voting, rebuilt each morning
from the NCSBE daily absentee file and published on GitHub Pages.

Each run issues one forecast with 90% ranges, for every remaining day, the
17-day total, and each party's votes, change from 2022 and share
(`work/central.py`). It fits a trend to each party's 2026 multiple over the
weekdays observed so far, extends it against both the 2022 and 2024 daily
profiles, and splits the difference; the ranges come from simulation over trend
error, the 2022-vs-2024 shape disagreement, and day-level noise.

The page closes with a projected Democratic vs Republican early vote
(`work/geography.py`): forecast turnout by party, voting as its members did in
2022 in the same county, with ranges over turnout, partisan loyalty, and a
1.5-point swing from 2022 behavior. Early votes only.

Every run appends the forecast it just made to `data/vintages.json`, keyed by
the last day of data it had seen. Accuracy is scored against the vintage issued
immediately before the day being scored, so a model that has been revised can
never be graded on hindsight.

## Layout

```
work/ingest.py             download + parse the current absentee file -> data/observed.json
work/build_site.py         build _site/ from baseline + observed + vintages
work/bootstrap_baseline.py one-time: 2022/2024 archives -> data/baseline.json
work/bootstrap_counties.py one-time: 2022 archive + county results -> data/county_baseline.json
work/central.py            forecast and 90% ranges
work/geography.py          where unaffiliated voters come from, and the implied shift
data/baseline.json         daily counts by party, 2022 and 2024 (committed)
data/county_baseline.json  2022 county early voters by day and party, plus Senate One Stop results
data/observed.json         2026 daily counts (committed, updated by CI)
data/vintages.json         every forecast ever issued (committed, updated by CI)
analysis/                  static eight-section report and supporting CSVs
_site/                     generated output (gitignored)
```

The 2022 and 2024 archives are ~300MB and stay out of the repo. `baseline.json`
is a few kilobytes and is built once.

## Local run

```bash
python3 work/bootstrap_baseline.py          # once, needs the 2022/2024 zips
python3 work/ingest.py                      # downloads the current file
python3 work/build_site.py                  # writes _site/
open _site/index.html
```

`work/ingest.py --zip some_file.zip` uses a local archive instead of downloading.

Everything is standard library only, so no dependencies to install.

## Deployment

The repository must be public for GitHub Pages on a free account.

1. Push to `main`.
2. Settings → Pages → Source: **GitHub Actions**.
3. Run the *Update tracker* workflow once manually (Actions → Run workflow).

After that it polls every two hours (minute 17 of even UTC hours), commits the
day's data when it changes, and republishes the site. Repeated runs are cheap:
the workflow checks the archive's Last-Modified header and skips the 48MB
download when nothing has been re-posted.

## Caveats

The vote projection is the only outcome estimate, and it assumes 2022 behavior. Party registration is not
vote choice, and early-vote composition measures when people vote rather than
how many will. See the report for the full discussion.
