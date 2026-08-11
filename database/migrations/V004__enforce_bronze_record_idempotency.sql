-- ============================================================================
-- Migration : V004__enforce_bronze_record_idempotency.sql
-- Purpose   : Enforce uniqueness of Bronze record fingerprints
-- ============================================================================

ALTER TABLE bronze.dhis2_data
ADD CONSTRAINT uq_dhis2_record_hash
UNIQUE (record_hash);
