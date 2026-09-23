CREATE TABLE silver.dhis2_dataset (
    dataset_metadata_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    source_instance TEXT NOT NULL,
    dataset_id TEXT NOT NULL,
    dataset_name TEXT NOT NULL,
    period_type TEXT NOT NULL,

    resolved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_silver_dhis2_dataset
        UNIQUE (
            source_instance,
            dataset_id
        ),

    CONSTRAINT chk_silver_dhis2_dataset_source_instance
        CHECK (BTRIM(source_instance) <> ''),

    CONSTRAINT chk_silver_dhis2_dataset_id
        CHECK (BTRIM(dataset_id) <> ''),

    CONSTRAINT chk_silver_dhis2_dataset_name
        CHECK (BTRIM(dataset_name) <> ''),

    CONSTRAINT chk_silver_dhis2_dataset_period_type
        CHECK (BTRIM(period_type) <> '')
);

CREATE INDEX idx_silver_dhis2_dataset_lookup
ON silver.dhis2_dataset (
    source_instance,
    dataset_id
);
