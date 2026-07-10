#!/usr/bin/env python3
"""Initialize the LOCAL feature store — a single SQLite file, zero setup.

This is the default backend: everything in the intelligence layer runs off
this file plus the JSONL logs. Supabase (db/supabase_schema.sql) is an
optional upgrade for cloud access or dashboards over live SQL; the schema
is the same, so switching later is an export, not a migration.

    python3 db/init_local.py            # creates data/cleanmail.db
    python3 db/init_local.py --path X   # elsewhere
"""

import argparse
import os
import sqlite3

DDL = """
CREATE TABLE IF NOT EXISTS senders (
    sender TEXT PRIMARY KEY,          -- address or domain, per grouping rule
    first_seen TEXT,
    last_seen TEXT,
    total_messages INTEGER DEFAULT 0,
    unread_messages INTEGER DEFAULT 0,
    replied_threads INTEGER DEFAULT 0,
    last_open_date TEXT,
    tier TEXT,                        -- KEEP | REVIEW | CUT | protected
    protected_reason TEXT
);

CREATE TABLE IF NOT EXISTS messages (
    message_id TEXT PRIMARY KEY,      -- Gmail message id; METADATA ONLY, no bodies
    thread_id TEXT,
    sender TEXT,
    subject_hash TEXT,                -- hash, not raw subject, by default
    received_date TEXT,
    gmail_category TEXT,
    list_id TEXT,
    category TEXT,                    -- engine category match, if any
    age_at_open_days INTEGER,         -- NULL if never opened
    observed_days INTEGER
);

CREATE TABLE IF NOT EXISTS actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT,
    pass TEXT,                        -- label | commit | spam-rescue | retention
    thread_id TEXT,
    sender TEXT,
    category TEXT,
    action TEXT,                      -- labeled | trashed | rescued | restored | vetoed
    reason TEXT,
    p_valuable REAL,
    policy TEXT DEFAULT 'champion'    -- champion | shadow:<name>
);

CREATE TABLE IF NOT EXISTS daily_counts (
    date TEXT,
    sender TEXT,
    count INTEGER,
    PRIMARY KEY (date, sender)
);

CREATE TABLE IF NOT EXISTS eval_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT,
    git_ref TEXT,
    junk_recall REAL,
    auto_stage_recall REAL,
    protected_false_positives INTEGER,
    passed INTEGER
);

CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender);
CREATE INDEX IF NOT EXISTS idx_actions_ts ON actions(ts);
CREATE INDEX IF NOT EXISTS idx_actions_action ON actions(action);
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default="data/cleanmail.db")
    args = ap.parse_args()
    os.makedirs(os.path.dirname(args.path) or ".", exist_ok=True)
    con = sqlite3.connect(args.path)
    con.executescript(DDL)
    con.commit()
    tables = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    con.close()
    print(f"initialized {args.path} with tables: {', '.join(tables)}")


if __name__ == "__main__":
    main()
