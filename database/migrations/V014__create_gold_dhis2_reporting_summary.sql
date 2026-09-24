CREATE VIEW gold.dhis2_reporting_summary AS
SELECT
    source_instance,
    dataset_id,
    dataset_name,

    org_unit_id,
    org_unit_name,

    period,
    period_type,
    period_year,
    period_month,
    period_start_date,
    period_end_date,

    COUNT(*) AS observation_count,

    COUNT(*) FILTER (
        WHERE quality_status = 'VALID'
    ) AS valid_observation_count,

    COUNT(*) FILTER (
        WHERE quality_status = 'NON_NUMERIC'
    ) AS non_numeric_observation_count,

    COUNT(*) FILTER (
        WHERE quality_status = 'INVALID'
    ) AS invalid_observation_count,

    COUNT(reported_value) AS reported_value_count

FROM gold.dhis2_observation_base

GROUP BY
    source_instance,
    dataset_id,
    dataset_name,
    org_unit_id,
    org_unit_name,
    period,
    period_type,
    period_year,
    period_month,
    period_start_date,
    period_end_date;
