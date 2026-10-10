"""
Ingest applications.csv into the SQLite database, validating rows and
recording a status_history entry for each application's current status.

Usage:
    python scripts/ingest.py                       # uses data/applications.csv -> data/applications.db
    python scripts/ingest.py --csv path/to/file.csv --db path/to/out.db
"""
from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

VALID_STATUSES = {"applied", "interview", "offer", "rejected", "withdrawn"}
REQUIRED_COLUMNS = {"company", "role", "date_applied", "source", "status", "notes"}


class RowError(Exception):
    pass


def _validate_row(row: dict, line_no: int) -> dict:
    missing = REQUIRED_COLUMNS - row.keys()
    if missing:
        raise RowError(f"line {line_no}: missing columns {sorted(missing)}")

    company = row["company"].strip()
    role = row["role"].strip()
    if not company or not role:
        raise RowError(f"line {line_no}: company and role are required")

    date_applied = row["date_applied"].strip()
    try:
        datetime.strptime(date_applied, "%Y-%m-%d")
    except ValueError:
        raise RowError(f"line {line_no}: date_applied '{date_applied}' is not YYYY-MM-DD")

    status = row["status"].strip().lower() or "applied"
    if status not in VALID_STATUSES:
        raise RowError(f"line {line_no}: status '{status}' not in {sorted(VALID_STATUSES)}")

    return {
        "company": company,
        "role": role,
        "date_applied": date_applied,
        "source": row["source"].strip(),
        "status": status,
        "notes": row["notes"].strip(),
    }


def load_schema(conn: sqlite3.Connection, schema_path: Path) -> None:
    conn.executescript(schema_path.read_text(encoding="utf-8"))


def ingest(csv_path: Path, db_path: Path, schema_path: Path) -> tuple[int, list[str]]:
    conn = sqlite3.connect(db_path)
    load_schema(conn, schema_path)

    inserted = 0
    errors: list[str] = []

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for line_no, raw_row in enumerate(reader, start=2):  # header is line 1
            try:
                row = _validate_row(raw_row, line_no)
            except RowError as e:
                errors.append(str(e))
                continue

            cur = conn.execute(
                """
                INSERT INTO applications (company, role, date_applied, source, status, notes)
                VALUES (:company, :role, :date_applied, :source, :status, :notes)
                """,
                row,
            )
            conn.execute(
                "INSERT INTO status_history (application_id, status) VALUES (?, ?)",
                (cur.lastrowid, row["status"]),
            )
            inserted += 1

    conn.commit()
    conn.close()
    return inserted, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest applications.csv into SQLite.")
    root = Path(__file__).resolve().parent.parent
    parser.add_argument("--csv", default=str(root / "data" / "applications.csv"))
    parser.add_argument("--db", default=str(root / "data" / "applications.db"))
    parser.add_argument("--schema", default=str(root / "sql" / "schema.sql"))
    args = parser.parse_args(argv)

    csv_path, db_path, schema_path = Path(args.csv), Path(args.db), Path(args.schema)
    if not csv_path.exists():
        print(f"Error: {csv_path} not found", file=sys.stderr)
        return 1

    inserted, errors = ingest(csv_path, db_path, schema_path)
    print(f"Inserted {inserted} application(s) into {db_path}")
    if errors:
        print(f"\n{len(errors)} row(s) skipped:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
