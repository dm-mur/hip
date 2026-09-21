-- ============================================================================
-- Migration : V008__create_dhis2_metadata_cache.sql
-- Purpose   : Persist instance-scoped DHIS2 metadata for reusable enrichment.
-- ============================================================================

CREATE TABLE IF NOT EXISTS silver.dhis2_metadata (
    metadata_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_instance TEXT NOT NULL,
    metadata_type TEXT NOT NULL,
    uid TEXT NOT NULL,
    name TEXT NOT NULL,
    resolved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_silver_dhis2_metadata
        UNIQUE (source_instance, metadata_type, uid),

    CONSTRAINT chk_silver_dhis2_metadata_type
        CHECK (
            metadata_type IN (
                'DATA_ELEMENT',
                'ORG_UNIT',
                'CATEGORY_OPTION_COMBO',
                'ATTRIBUTE_OPTION_COMBO'
            )
        ),

    CONSTRAINT chk_silver_dhis2_metadata_uid
        CHECK (BTRIM(uid) <> ''),

    CONSTRAINT chk_silver_dhis2_metadata_name
        CHECK (BTRIM(name) <> '')
);

CREATE INDEX idx_silver_dhis2_metadata_lookup
ON silver.dhis2_metadata (
    source_instance,
    metadata_type,
    uid
);
