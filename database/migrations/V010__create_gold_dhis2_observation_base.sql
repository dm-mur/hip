CREATE VIEW gold.dhis2_observation_base AS
SELECT
    source_instance,
    dataset_id,

    org_unit AS org_unit_id,
    org_unit_name,

    data_element AS data_element_id,
    data_element_name,

    category_option_combo AS category_option_combo_id,
    category_option_combo_name,

    attribute_option_combo AS attribute_option_combo_id,
    attribute_option_combo_name,

    period,

    CASE
        WHEN period ~ '^[0-9]{6}$'
             AND SUBSTRING(period FROM 5 FOR 2)::INTEGER
                 BETWEEN 1 AND 12
        THEN 'MONTHLY'
        ELSE 'OTHER'
    END AS period_type,

    CASE
        WHEN period ~ '^[0-9]{6}$'
             AND SUBSTRING(period FROM 5 FOR 2)::INTEGER
                 BETWEEN 1 AND 12
        THEN SUBSTRING(period FROM 1 FOR 4)::INTEGER
        ELSE NULL
    END AS period_year,

    CASE
        WHEN period ~ '^[0-9]{6}$'
             AND SUBSTRING(period FROM 5 FOR 2)::INTEGER
                 BETWEEN 1 AND 12
        THEN SUBSTRING(period FROM 5 FOR 2)::INTEGER
        ELSE NULL
    END AS period_month,

    CASE
        WHEN period ~ '^[0-9]{6}$'
             AND SUBSTRING(period FROM 5 FOR 2)::INTEGER
                 BETWEEN 1 AND 12
        THEN MAKE_DATE(
            SUBSTRING(period FROM 1 FOR 4)::INTEGER,
            SUBSTRING(period FROM 5 FOR 2)::INTEGER,
            1
        )
        ELSE NULL
    END AS period_start_date,

    value_numeric AS reported_value,
    quality_status

FROM silver.dhis2_observation;
