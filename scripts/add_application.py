"""
Add a new application directly to the database (and appends the same row to
the CSV so the CSV stays the source of truth / stays importable elsewhere).

Usage:
    python scripts/add_application.py --company "Acme" --role "Data Analyst" \
        --date-applied 2026-09-26 --source LinkedIn --notes "Applied via referral"
"""
from __future__ import annotations

import argparse
import csv
import sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = ROOT / "data" / "applications.db"
DEFAULT_CSV = ROOT / "data" / "applications.csv"
DEFAULT_SCHEMA = ROOT / "sql" / "schema.sql"


def add_application(
    company: str,
    role: str,
    date_applied: str,
    source: str,
    notes: str,
    status: str = "applied",
    db_path: Path = DEFAULT_DB,
    csv_path: Path = DEFAULT_CSV,
    schema_path: Path = DEFAULT_SCHEMA,
) -> int:
    datetime.strptime(date_applied, "%Y-%m-%d")  # raises ValueError if malformed

    conn = sqlite3.connect(db_path)
    conn.executescript(schema_path.read_text(encoding="utf-8"))
    cur = conn.execute(
        """
        INSERT INTO applications (company, role, date_applied, source, status, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (company, role, date_applied, source, status, notes),
    )
    conn.execute(
        "INSERT INTO status_history (application_id, status) VALUES (?, ?)",
        (cur.lastrowid, status),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    file_exists = csv_path.exists()
    with csv_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["company", "role", "date_applied", "source", "status", "notes"])
        writer.writerow([company, role, date_applied, source, status, notes])

    return new_id


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Add a new job application.")
    parser.add_argument("--company", required=True)
    parser.add_argument("--role", required=True)
    parser.add_argument("--date-applied", required=True, help="YYYY-MM-DD")
    parser.add_argument("--source", default="")
    parser.add_argument("--status", default="applied")
    parser.add_argument("--notes", default="")
    args = parser.parse_args(argv)

    new_id = add_application(
        company=args.company,
        role=args.role,
        date_applied=args.date_applied,
        source=args.source,
        notes=args.notes,
        status=args.status,
    )
    print(f"Added application #{new_id}: {args.company} — {args.role}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
