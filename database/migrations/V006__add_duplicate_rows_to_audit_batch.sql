-- ============================================================================
-- Migration : V006__add_duplicate_rows_to_audit_batch.sql
-- Purpose   : Add duplicate-row observability to ETL batch auditing.
--
-- Duplicate rows are valid source records that were intentionally not
-- inserted because an equivalent Bronze record already exists.
-- ============================================================================

ALTER TABLE audit.etl_batch
ADD COLUMN duplicate_rows BIGINT NOT NULL DEFAULT 0;

ALTER TABLE audit.etl_batch
ADD CONSTRAINT chk_etl_batch_duplicate_rows_nonnegative
CHECK (duplicate_rows >= 0);
