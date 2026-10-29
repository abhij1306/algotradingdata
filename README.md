# algotradingdata

The private data record of Hire a Trader (HAT): what the code repo (`abhij1306/algotrading`) does
not version. Code is not here. Nothing here is a credential: the pre-push guard refuses them.

| Folder | Holds | Written by |
| --- | --- | --- |
| `snapshots/` | One record per snapshot release: every asset's size and sha256, every file each tar holds | `scripts/hat_snapshot.py` |
| `manifests/` | One CSV per data store: path, rows, min/max date, bytes, sha256 of every file | the daily update's `record` step |
| `reference/` | Source-of-truth tables exported from `hat_live` as CSV; `ca-data/` (the downloaded NSE corporate action, board meeting and results files) and `corrections/` | `record` step (tables); seeded by hand (`ca-data`, `corrections`) |
| `research/` | Strategy notes, briefs, plans, portfolio/sweep/policy YAML and run reports, study scripts and reports (`studies/`), the orchestrator handoff and open items. No caches, Parquet or files over 1 MB | by hand |
| `audits/` | Dated coverage and verification reports (`workspace/`, `data-root/`; W1 reports go here) | by hand and the verify command |

## Snapshots (GitHub Releases)

Each release `snapshot-<date>` holds numbered assets, each under 1.9 GB:

- `<db>.dump.partNN`: `pg_dump --format=custom` of `hat_live` and `hat_state`;
- `<part>.tar.gz.partNN`: a gzipped tar of a folder;
- `SHA256SUMS` and `<tag>.json` (the same record as `snapshots/<tag>.json`).

The first release, `snapshot-2026-10-29`, is a full set: both databases; parts `raw` and `bars_5m`
(the data root's NSE source files and 5-minute bars, which cannot be rebuilt), `data_root` (the
rest of the data root except `features_daily/`, which is rebuilt from bars and the DB, and the
DuckDB `tmp/`), `kotak` (the Kotak raw 5-minute downloads, without its `venv/`), `ca_data`, and
`workspace` (research folders with their caches, the NIFTY 500 and overlay working folders,
notes, briefs, backtest YAML and logs, audits, archive). Every part leaves out `venv`, `.venv`,
`__pycache__`, `*.pyc`, `.git`, `node_modules` and any credential-looking file (`.env*`, keys,
`*token*`, `*secret*`, `*cookie*`, browser profiles). The weekly releases (Sundays) are
incremental: both dumps, plus the `raw/` and `bars_5m/` files the earlier records do not hold.

## Restore

```bash
gh release download snapshot-2026-10-29 --repo abhij1306/algotradingdata --dir <scratch>
cd <scratch> && sha256sum -c SHA256SUMS
cat hat_live.dump.part* > hat_live.dump
createdb hat_restore && pg_restore -d hat_restore --no-owner hat_live.dump     # pg_restore 18
cat raw.tar.gz.part* | tar -xz -C <HAT_DATA_ROOT>/raw                         # each part to its source
```

A record's `parts.<name>.source` is the folder the part was taken from and `files` every file
it holds with its sha256. Restore the full release first, then each later (incremental) release in
date order; after unpacking one, delete the files its record lists under `removed`. Rebuild
`features_daily/` with the features command (code repo runbook). The code repo's runbook
(Snapshot and restore) has the procedure and the drill.

## Manifests

`manifests/<store>.csv` is rewritten after every daily update and committed only when it
changed, so `git log -p manifests/` is the history of the stores. A new session adds lines; a
changed `sha256` on an existing line is a rewrite of stored data, and the commit message
(`record <date>: bars_5m +1 ~0 -0`: added, rewritten, removed) counts them. `rows` and the
dates come from the Parquet metadata (a `date=` partition gives its date); `raw/` files have no
rows.

## Secret guard

`.githooks/pre-push` refuses a push whose new commits add a credential-looking file name or text.
Enable it in every clone:

```bash
git config core.hooksPath .githooks
```

The daily update's `record` step refuses to commit while it is off.
