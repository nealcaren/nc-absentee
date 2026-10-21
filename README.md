# NC early voting 2026 — daily tracker

A live forecast of North Carolina in-person early voting, rebuilt each morning
from the NCSBE daily absentee file and published on GitHub Pages.

Two forecasts are issued with every run:

- **Persistent** — each party's current multiple of 2022 holds through the
  remaining days.
- **Surge stops** — the extra votes were pulled forward and the remaining days
  run at 2022's exact levels.

They bracket the question the data cannot settle: more turnout, or the same
voters voting earlier.

Every run appends the forecast it just made to `data/vintages.json`, keyed by
the last day of data it had seen. Accuracy is scored against the vintage issued
immediately before the day being scored, so a model that has been revised can
never be graded on hindsight.

## Layout

```
work/ingest.py             download + parse the current absentee file -> data/observed.json
work/build_site.py         build _site/ from baseline + observed + vintages
work/bootstrap_baseline.py one-time: 2022/2024 archives -> data/baseline.json
data/baseline.json         daily counts by party, 2022 and 2024 (committed)
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

After that it runs at 10:30 and 16:30 Eastern daily, commits the day's data,
and republishes the site.

## Caveats

These are turnout forecasts, not outcome forecasts. Party registration is not
vote choice, and early-vote composition measures when people vote rather than
how many will. See the report for the full discussion.
