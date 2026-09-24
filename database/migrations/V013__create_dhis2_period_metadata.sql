CREATE TABLE silver.dhis2_period (
    period_metadata_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    source_instance TEXT NOT NULL,
    period_type TEXT NOT NULL,
    period TEXT NOT NULL,

    period_start_date DATE NOT NULL,
    period_end_date DATE NOT NULL,

    resolved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_silver_dhis2_period
        UNIQUE (
            source_instance,
            period_type,
            period
        ),

    CONSTRAINT chk_silver_dhis2_period_source_instance
        CHECK (BTRIM(source_instance) <> ''),

    CONSTRAINT chk_silver_dhis2_period_type
        CHECK (BTRIM(period_type) <> ''),

    CONSTRAINT chk_silver_dhis2_period
        CHECK (BTRIM(period) <> ''),

    CONSTRAINT chk_silver_dhis2_period_dates
        CHECK (period_end_date >= period_start_date)
);

CREATE INDEX idx_silver_dhis2_period_lookup
ON silver.dhis2_period (
    source_instance,
    period_type,
    period
);
