-- ============================================================================
-- Migration : V005__scope_bronze_record_idempotency.sql
-- Purpose   : Scope Bronze record uniqueness to the DHIS2 source instance.
--
-- Rationale:
--   A record_hash identifies the source representation of a record.
--   Different DHIS2 instances may legitimately produce the same hash.
--
--   Therefore uniqueness must be enforced on:
--
--       source_instance + record_hash
--
--   rather than record_hash alone.
-- ============================================================================


-- ============================================================================
-- 1. Remove the previous global uniqueness constraint
-- ============================================================================

ALTER TABLE bronze.dhis2_data
DROP CONSTRAINT uq_dhis2_record_hash;


-- ============================================================================
-- 2. Enforce uniqueness within each DHIS2 source instance
-- ============================================================================

ALTER TABLE bronze.dhis2_data
ADD CONSTRAINT uq_dhis2_source_record
UNIQUE (source_instance, record_hash);
