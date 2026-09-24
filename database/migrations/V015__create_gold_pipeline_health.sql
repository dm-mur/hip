CREATE VIEW gold.pipeline_health AS
SELECT
    batch_id,
    source_system,
    batch_name,
    environment,
    status,

    started_at,
    completed_at,
    duration_seconds,

    total_rows,
    successful_rows,
    failed_rows,
    duplicate_rows,

    initiated_by,
    platform_version,
    remarks,
    created_at

FROM audit.etl_batch;
