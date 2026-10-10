-- Schema for the job application tracker.
-- One row per application; status_history lets the funnel (applied -> interview -> offer)
-- be reconstructed even as a single application's status changes over time.

CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    role TEXT NOT NULL,
    date_applied TEXT NOT NULL,        -- ISO date, YYYY-MM-DD
    source TEXT,                        -- e.g. LinkedIn, Referral, Company site, Handshake
    status TEXT NOT NULL DEFAULT 'applied',  -- applied | interview | offer | rejected | withdrawn
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS status_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL REFERENCES applications(id),
    status TEXT NOT NULL,
    changed_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_date ON applications(date_applied);
