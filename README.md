# Job Application Tracker

Tracking my own job search (company, role, date applied, source, status,
notes) the same way I'd build a pipeline for someone else's data: ingest →
validate → SQLite → (planned) Power BI dashboard on top.

Part of a rotating portfolio of small data analyst / data engineer projects
— real, incremental commits rather than one big dump.

## Plan

1. **Ingest** — validate and load `data/applications.csv` into SQLite (`sql/schema.sql`)
2. **Update** — a small CLI to add new applications and update their status as things progress, without ever losing the history of how a status changed over time
3. **Validate** — tests around the validation rules and the ingest/add/update behavior
4. **Dashboard** (manual follow-up, outside this repo's automation) — a Power BI report on top of `applications.db` showing the funnel, response rate by source, and applications-per-week

## Setup

```bash
pip install -r requirements.txt
python scripts/ingest.py
```

More usage docs land as each piece is built — see the commit history for
day-by-day progress.
