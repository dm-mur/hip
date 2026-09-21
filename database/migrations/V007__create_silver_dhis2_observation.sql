CREATE SCHEMA IF NOT EXISTS silver;

CREATE TABLE silver.dhis2_observation (
    silver_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    bronze_id BIGINT NOT NULL,
    batch_id UUID NOT NULL,
    source_system TEXT NOT NULL DEFAULT 'DHIS2',
    source_instance TEXT NOT NULL,

    dataset_id TEXT,
    data_element TEXT NOT NULL,
    data_element_name TEXT,

    org_unit TEXT NOT NULL,
    org_unit_name TEXT,

    period TEXT NOT NULL,

    category_option_combo TEXT,
    category_option_combo_name TEXT,

    attribute_option_combo TEXT,
    attribute_option_combo_name TEXT,

    value_raw TEXT,
    value_numeric NUMERIC,

    quality_status TEXT NOT NULL,
    quality_reason TEXT,

    created_at_source TIMESTAMPTZ,
    last_updated_at_source TIMESTAMPTZ,

    processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_silver_dhis2_bronze
        FOREIGN KEY (bronze_id)
        REFERENCES bronze.dhis2_data(bronze_id),

    CONSTRAINT fk_silver_dhis2_batch
        FOREIGN KEY (batch_id)
        REFERENCES audit.etl_batch(batch_id),

    CONSTRAINT chk_silver_dhis2_quality_status
        CHECK (
            quality_status IN (
                'VALID',
                'NON_NUMERIC',
                'INVALID'
            )
        )
);

CREATE UNIQUE INDEX uq_silver_dhis2_bronze_id
    ON silver.dhis2_observation(bronze_id);

CREATE INDEX idx_silver_dhis2_period
    ON silver.dhis2_observation(period);

CREATE INDEX idx_silver_dhis2_org_unit
    ON silver.dhis2_observation(org_unit);

CREATE INDEX idx_silver_dhis2_data_element
    ON silver.dhis2_observation(data_element);

CREATE INDEX idx_silver_dhis2_source_instance
    ON silver.dhis2_observation(source_instance);
