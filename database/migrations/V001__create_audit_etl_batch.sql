CREATE TABLE IF NOT EXISTS audit.etl_batch (
    batch_id UUID PRIMARY KEY,
    source_system TEXT NOT NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    status TEXT NOT NULL,
    rows_loaded INTEGER DEFAULT 0
);