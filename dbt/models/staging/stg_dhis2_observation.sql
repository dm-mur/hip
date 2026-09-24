select
    silver_id,
    bronze_id,
    batch_id,
    source_system,
    source_instance,
    dataset_id,

    data_element,
    data_element_name,

    org_unit,
    org_unit_name,

    period,

    category_option_combo,
    category_option_combo_name,

    attribute_option_combo,
    attribute_option_combo_name,

    value_raw,
    value_numeric,

    quality_status,
    quality_reason,

    created_at_source,
    last_updated_at_source,
    processed_at

from {{ source('silver', 'dhis2_observation') }}
