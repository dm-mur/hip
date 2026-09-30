with pipeline_runs as (

    select
        batch_id,
        source_system,
        batch_name,
        environment,
        status,
        started_at,
        completed_at,
        duration_seconds,
        coalesce(total_rows, 0) as total_rows,
        coalesce(successful_rows, 0) as successful_rows,
        coalesce(failed_rows, 0) as failed_rows,
        coalesce(duplicate_rows, 0) as duplicate_rows,
        initiated_by,
        platform_version,
        remarks,
        created_at

    from {{ source('gold', 'pipeline_health') }}

)

select
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
    successful_rows - duplicate_rows as inserted_rows,
    duplicate_rows,
    failed_rows,

    case
        when total_rows > 0
        then duplicate_rows::numeric / total_rows
        else 0
    end as duplicate_rate,

    case
        when total_rows > 0
        then failed_rows::numeric / total_rows
        else 0
    end as failure_rate,

    status = 'SUCCESS' as is_success,
    status = 'FAILED' as is_failure,
    status in ('SUCCESS', 'FAILED', 'CANCELLED') as is_complete,

    initiated_by,
    platform_version,
    remarks,
    created_at

from pipeline_runs
