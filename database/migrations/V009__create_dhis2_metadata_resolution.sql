-- ============================================================================
-- Migration : V009__create_dhis2_metadata_resolution.sql
-- Purpose   : Track unresolved and subsequently resolved DHIS2 metadata.
-- ============================================================================

CREATE TABLE IF NOT EXISTS silver.dhis2_metadata_resolution (
    resolution_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_instance TEXT NOT NULL,
    metadata_type TEXT NOT NULL,
    uid TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'UNRESOLVED',
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_attempted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    attempt_count INTEGER NOT NULL DEFAULT 1,
    resolved_at TIMESTAMPTZ,

    CONSTRAINT uq_silver_dhis2_metadata_resolution
        UNIQUE (source_instance, metadata_type, uid),

    CONSTRAINT chk_silver_dhis2_metadata_resolution_type
        CHECK (
            metadata_type IN (
                'DATA_ELEMENT',
                'ORG_UNIT',
                'CATEGORY_OPTION_COMBO',
                'ATTRIBUTE_OPTION_COMBO'
            )
        ),

    CONSTRAINT chk_silver_dhis2_metadata_resolution_status
        CHECK (
            status IN (
                'UNRESOLVED',
                'RESOLVED'
            )
        ),

    CONSTRAINT chk_silver_dhis2_metadata_resolution_uid
        CHECK (BTRIM(uid) <> ''),

    CONSTRAINT chk_silver_dhis2_metadata_resolution_attempt_count
        CHECK (attempt_count >= 1),

    CONSTRAINT chk_silver_dhis2_metadata_resolution_state
        CHECK (
            (
                status = 'UNRESOLVED'
                AND resolved_at IS NULL
            )
            OR
            (
                status = 'RESOLVED'
                AND resolved_at IS NOT NULL
            )
        )
);

CREATE INDEX idx_silver_dhis2_metadata_resolution_unresolved
ON silver.dhis2_metadata_resolution (
    source_instance,
    metadata_type,
    uid
)
WHERE status = 'UNRESOLVED';
