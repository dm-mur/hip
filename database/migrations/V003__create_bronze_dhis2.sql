-- ============================================================================
-- Migration : V003__create_bronze_dhis2.sql
-- Author    : Doris Muriungi
-- Purpose   : Create the Bronze layer for DHIS2 aggregate data.
--
-- Design principles:
--   - Preserve the source representation
--   - Support different DHIS2 instances
--   - Retain the original source payload
--   - Maintain ingestion lineage through audit.etl_batch
--   - Avoid creating a separate table for every DHIS2 dataset
-- ============================================================================


-- ============================================================================
-- 1. Create the Bronze schema
-- ----------------------------------------------------------------------------
-- Bronze contains source-level data before business transformations.
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS bronze;


-- ============================================================================
-- 2. Create the DHIS2 Bronze table
-- ----------------------------------------------------------------------------
-- This table is intentionally generic so that multiple DHIS2 datasets and
-- instances can be ingested into the same structure.
-- ============================================================================

CREATE TABLE bronze.dhis2_data (

    -- ------------------------------------------------------------------------
    -- HIP ingestion and lineage metadata
    -- ------------------------------------------------------------------------

    bronze_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    batch_id UUID NOT NULL,

    source_system TEXT NOT NULL DEFAULT 'DHIS2',

    source_instance TEXT NOT NULL,

    ingested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,


    -- ------------------------------------------------------------------------
    -- DHIS2 dataset and dimensional information
    -- ------------------------------------------------------------------------

    dataset_id TEXT,

    data_element TEXT,

    data_element_name TEXT,

    org_unit TEXT,

    org_unit_name TEXT,

    period TEXT,


    -- ------------------------------------------------------------------------
    -- DHIS2 category dimensions
    -- ------------------------------------------------------------------------

    category_option_combo TEXT,

    category_option_combo_name TEXT,

    attribute_option_combo TEXT,

    attribute_option_combo_name TEXT,


    -- ------------------------------------------------------------------------
    -- DHIS2 reported value and source metadata
    -- ------------------------------------------------------------------------

    value TEXT,

    comment TEXT,

    followup TEXT,

    stored_by TEXT,

    created_at_source TIMESTAMPTZ,

    last_updated_at_source TIMESTAMPTZ,


    -- ------------------------------------------------------------------------
    -- Source preservation
    -- ------------------------------------------------------------------------
    -- raw_payload preserves the original DHIS2 record.
    -- This protects us from losing source information when the canonical
    -- model evolves.
    -- ------------------------------------------------------------------------

    raw_payload JSONB,


    -- ------------------------------------------------------------------------
    -- Record fingerprint
    -- ------------------------------------------------------------------------
    -- Used to identify duplicate source records and support idempotent
    -- ingestion.
    -- ------------------------------------------------------------------------

    record_hash TEXT NOT NULL
);


-- ============================================================================
-- 3. Link Bronze records to the ETL audit framework
-- ----------------------------------------------------------------------------
-- Every Bronze record should be traceable to the batch that ingested it.
-- ============================================================================

ALTER TABLE bronze.dhis2_data
ADD CONSTRAINT fk_dhis2_batch
FOREIGN KEY (batch_id)
REFERENCES audit.etl_batch(batch_id);


-- ============================================================================
-- 4. Create operational indexes
-- ----------------------------------------------------------------------------
-- These support common ingestion, lineage and analytical access patterns.
-- ============================================================================

CREATE INDEX idx_dhis2_batch_id
ON bronze.dhis2_data(batch_id);

CREATE INDEX idx_dhis2_dataset_id
ON bronze.dhis2_data(dataset_id);

CREATE INDEX idx_dhis2_data_element
ON bronze.dhis2_data(data_element);

CREATE INDEX idx_dhis2_org_unit
ON bronze.dhis2_data(org_unit);

CREATE INDEX idx_dhis2_period
ON bronze.dhis2_data(period);

CREATE INDEX idx_dhis2_source_instance
ON bronze.dhis2_data(source_instance);

CREATE INDEX idx_dhis2_record_hash
ON bronze.dhis2_data(record_hash);
