select
    source_instance,
    dataset_id,
    org_unit,
    org_unit_name,
    period,

    count(*) as observation_count,

    count(*) filter (
        where quality_status = 'VALID'
    ) as valid_observation_count,

    count(*) filter (
        where quality_status = 'NON_NUMERIC'
    ) as non_numeric_observation_count,

    count(*) filter (
        where quality_status = 'INVALID'
    ) as invalid_observation_count,

    count(value_numeric) as reported_value_count

from {{ ref('stg_dhis2_observation') }}

group by
    source_instance,
    dataset_id,
    org_unit,
    org_unit_name,
    period
