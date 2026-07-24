-- LandLead schema. SQLite-first; the DDL is intentionally portable to Postgres
-- (adjust AUTOINCREMENT -> SERIAL and datetime defaults if you migrate).

-- Every raw record captured from a source, before dedup/normalization.
CREATE TABLE IF NOT EXISTS raw_records (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source      TEXT    NOT NULL,          -- e.g. 'arcgis_parcels', 'tax_deed_auctions'
    county      TEXT,
    state       TEXT,
    apn         TEXT,                       -- may be NULL for non-parcel sources
    payload     TEXT    NOT NULL,           -- JSON blob of the raw record
    fetched_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_raw_apn ON raw_records(apn);
CREATE INDEX IF NOT EXISTS idx_raw_source ON raw_records(source);

-- Canonical lead, one row per parcel (APN). Merged from many raw records.
CREATE TABLE IF NOT EXISTS leads (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    apn                     TEXT,                    -- display form (may keep separators)
    apn_key                 TEXT    UNIQUE,          -- normalized canonical dedup key
    county                  TEXT,
    state                   TEXT,
    sources                 TEXT,                    -- JSON array of contributing sources
    owner_name              TEXT,
    owner_mailing_address   TEXT,
    property_address        TEXT,
    latitude                REAL,
    longitude               REAL,
    acreage                 REAL,
    land_value              REAL,
    assessed_value          REAL,
    last_sale_date          TEXT,
    last_sale_price         REAL,
    -- enrichment signals
    absentee                INTEGER DEFAULT 0,       -- mailing addr != situs
    out_of_state_owner      INTEGER DEFAULT 0,
    tax_delinquent          INTEGER DEFAULT 0,
    tax_delinquent_amount   REAL,
    probate_signal          INTEGER DEFAULT 0,
    code_violation          INTEGER DEFAULT 0,
    vacant_confirmed        INTEGER DEFAULT 0,
    -- scoring / pipeline
    lead_score              INTEGER DEFAULT 0,
    priority                INTEGER DEFAULT 0,
    status                  TEXT    NOT NULL DEFAULT 'New',
    score_breakdown         TEXT,                    -- JSON explanation
    created_at              TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at              TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_leads_score ON leads(lead_score);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_county ON leads(county, state);

-- Owner contact info (skip-trace results or manual entry).
CREATE TABLE IF NOT EXISTS contacts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id     INTEGER NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    name        TEXT,
    phone       TEXT,
    email       TEXT,
    mailing_address TEXT,
    provider    TEXT,                        -- skip-trace source
    confidence  REAL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_contacts_lead ON contacts(lead_id);

-- Free-form notes on a lead.
CREATE TABLE IF NOT EXISTS notes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id     INTEGER NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    body        TEXT NOT NULL,
    author      TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_notes_lead ON notes(lead_id);

-- Pipeline transition history.
CREATE TABLE IF NOT EXISTS status_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id     INTEGER NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    from_status TEXT,
    to_status   TEXT NOT NULL,
    changed_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Follow-up tasks (call / mail / skip_trace).
CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id     INTEGER NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    type        TEXT NOT NULL,               -- call | mail | skip_trace
    status      TEXT NOT NULL DEFAULT 'open',-- open | done | skipped
    due_date    TEXT,
    detail      TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_tasks_lead ON tasks(lead_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);

-- Direct-mail queue: rendered, merge-ready letters awaiting send.
CREATE TABLE IF NOT EXISTS mail_queue (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id     INTEGER NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    template    TEXT NOT NULL,               -- motivated_seller | probate_heir | tax_delinquent
    rendered    TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'queued', -- queued | printed | sent | cancelled
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    sent_at     TEXT
);
CREATE INDEX IF NOT EXISTS idx_mail_status ON mail_queue(status);

-- Per-source run log for observability + fault tolerance.
CREATE TABLE IF NOT EXISTS scrape_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source      TEXT NOT NULL,
    county      TEXT,
    state       TEXT,
    started_at  TEXT NOT NULL DEFAULT (datetime('now')),
    finished_at TEXT,
    status      TEXT NOT NULL DEFAULT 'running', -- running | ok | error | skipped
    records_found INTEGER DEFAULT 0,
    message     TEXT
);
CREATE INDEX IF NOT EXISTS idx_scrapelog_source ON scrape_log(source);
