-- ============================================================================
-- Migration : V002__enhance_audit_batch.sql
-- Author    : Doris Muriungi
-- Purpose   : Enhance the enterprise audit batch table with operational
--             metadata, governance fields, constraints and indexes.
--
-- Why?
--   - Improve observability of ETL executions
--   - Support multiple environments
--   - Capture execution metrics
--   - Prepare the platform for monitoring dashboards
-- ============================================================================


-- ============================================================================
-- 1. Rename existing column for improved clarity
-- ----------------------------------------------------------------------------
-- 'rows_loaded' is ambiguous.
-- Rename it to 'total_rows' to clearly represent the total rows processed.
-- ============================================================================

ALTER TABLE audit.etl_batch
RENAME COLUMN rows_loaded TO total_rows;


-- ============================================================================
-- 2. Add new operational metadata columns
-- ----------------------------------------------------------------------------
-- These columns provide additional context for monitoring, governance,
-- troubleshooting and reporting.
-- ============================================================================

ALTER TABLE audit.etl_batch
    ADD COLUMN batch_name VARCHAR(200),
    ADD COLUMN environment VARCHAR(20),
    ADD COLUMN duration_seconds INTEGER,
    ADD COLUMN successful_rows BIGINT,
    ADD COLUMN failed_rows BIGINT,
    ADD COLUMN initiated_by VARCHAR(100),
    ADD COLUMN platform_version VARCHAR(30),
    ADD COLUMN remarks TEXT,
    ADD COLUMN created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP;


-- ============================================================================
-- 3. Strengthen the schema with NOT NULL constraints
-- ----------------------------------------------------------------------------
-- These fields are mandatory for every batch execution.
-- ============================================================================

ALTER TABLE audit.etl_batch
    ALTER COLUMN environment SET NOT NULL,
    ALTER COLUMN initiated_by SET NOT NULL;


-- ============================================================================
-- 4. Restrict allowed batch status values
-- ----------------------------------------------------------------------------
-- Only approved lifecycle states are allowed.
-- ============================================================================

ALTER TABLE audit.etl_batch
ADD CONSTRAINT chk_etl_batch_status
CHECK (
    status IN (
        'PENDING',
        'RUNNING',
        'SUCCESS',
        'FAILED',
        'CANCELLED'
    )
);


-- ============================================================================
-- 5. Restrict allowed environment values
-- ----------------------------------------------------------------------------
-- Standardize deployment environments across the platform.
-- ============================================================================

ALTER TABLE audit.etl_batch
ADD CONSTRAINT chk_etl_batch_environment
CHECK (
    environment IN (
        'DEV',
        'TEST',
        'UAT',
        'PROD'
    )
);


-- ============================================================================
-- 6. Create indexes for operational queries
-- ----------------------------------------------------------------------------
-- These indexes improve performance for monitoring dashboards and
-- operational troubleshooting.
-- ============================================================================

CREATE INDEX idx_etl_batch_status
ON audit.etl_batch(status);

CREATE INDEX idx_etl_batch_source_system
ON audit.etl_batch(source_system);

CREATE INDEX idx_etl_batch_started_at
ON audit.etl_batch(started_at);

CREATE INDEX idx_etl_batch_environment
ON audit.etl_batch(environment);
