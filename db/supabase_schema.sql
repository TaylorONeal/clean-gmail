-- OPTIONAL cloud backend (Supabase / Postgres).
--
-- The default backend is the local SQLite file created by db/init_local.py —
-- nothing in this repo requires Supabase. Apply this schema only if you want
-- cloud access, live SQL dashboards, or multi-device sharing, then set
-- storage.backend: "supabase" in config/profile.yaml. Tables mirror the
-- local schema one-to-one, so moving is an export/import, not a migration.
--
-- Privacy note: metadata only. No message bodies; subjects stored hashed.

create table if not exists senders (
    sender text primary key,
    first_seen date,
    last_seen date,
    total_messages integer default 0,
    unread_messages integer default 0,
    replied_threads integer default 0,
    last_open_date date,
    tier text check (tier in ('KEEP', 'REVIEW', 'CUT', 'protected')),
    protected_reason text
);

create table if not exists messages (
    message_id text primary key,
    thread_id text,
    sender text references senders(sender),
    subject_hash text,
    received_date date,
    gmail_category text,
    list_id text,
    category text,
    age_at_open_days integer,
    observed_days integer
);

create table if not exists actions (
    id bigint generated always as identity primary key,
    ts timestamptz not null default now(),
    pass text,
    thread_id text,
    sender text,
    category text,
    action text check (action in ('labeled', 'trashed', 'rescued', 'restored', 'vetoed')),
    reason text,
    p_valuable real,
    policy text default 'champion'
);

create table if not exists daily_counts (
    date date,
    sender text,
    count integer,
    primary key (date, sender)
);

create table if not exists eval_runs (
    id bigint generated always as identity primary key,
    ts timestamptz not null default now(),
    git_ref text,
    junk_recall real,
    auto_stage_recall real,
    protected_false_positives integer,
    passed boolean
);

create index if not exists idx_messages_sender on messages(sender);
create index if not exists idx_actions_ts on actions(ts);
create index if not exists idx_actions_action on actions(action);
