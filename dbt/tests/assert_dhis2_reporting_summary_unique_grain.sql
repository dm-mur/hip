select
    source_instance,
    dataset_id,
    org_unit,
    period,
    count(*) as row_count

from {{ ref('dhis2_reporting_summary') }}

group by
    source_instance,
    dataset_id,
    org_unit,
    period

having count(*) > 1
