CREATE OR REPLACE VIEW gold.dhis2_observation_base AS
SELECT
    o.source_instance,
    o.dataset_id,

    o.org_unit AS org_unit_id,
    o.org_unit_name,

    o.data_element AS data_element_id,
    o.data_element_name,

    o.category_option_combo AS category_option_combo_id,
    o.category_option_combo_name,

    o.attribute_option_combo AS attribute_option_combo_id,
    o.attribute_option_combo_name,

    o.period,

    d.period_type,

    CASE
        WHEN d.period_type = 'Monthly'
             AND o.period ~ '^[0-9]{6}$'
             AND SUBSTRING(o.period FROM 5 FOR 2)::INTEGER
                 BETWEEN 1 AND 12
        THEN SUBSTRING(o.period FROM 1 FOR 4)::INTEGER
        ELSE NULL
    END AS period_year,

    CASE
        WHEN d.period_type = 'Monthly'
             AND o.period ~ '^[0-9]{6}$'
             AND SUBSTRING(o.period FROM 5 FOR 2)::INTEGER
                 BETWEEN 1 AND 12
        THEN SUBSTRING(o.period FROM 5 FOR 2)::INTEGER
        ELSE NULL
    END AS period_month,

    CASE
        WHEN d.period_type = 'Monthly'
             AND o.period ~ '^[0-9]{6}$'
             AND SUBSTRING(o.period FROM 5 FOR 2)::INTEGER
                 BETWEEN 1 AND 12
        THEN MAKE_DATE(
            SUBSTRING(o.period FROM 1 FOR 4)::INTEGER,
            SUBSTRING(o.period FROM 5 FOR 2)::INTEGER,
            1
        )
        ELSE NULL
    END AS period_start_date,

    o.value_numeric AS reported_value,
    o.quality_status,

    -- New V012 columns are appended so the existing V010
    -- view column contract remains compatible.
    d.dataset_name,

    CASE
        WHEN d.period_type = 'Monthly'
             AND o.period ~ '^[0-9]{6}$'
             AND SUBSTRING(o.period FROM 5 FOR 2)::INTEGER
                 BETWEEN 1 AND 12
        THEN (
            MAKE_DATE(
                SUBSTRING(o.period FROM 1 FOR 4)::INTEGER,
                SUBSTRING(o.period FROM 5 FOR 2)::INTEGER,
                1
            )
            + INTERVAL '1 month'
            - INTERVAL '1 day'
        )::DATE
        ELSE NULL
    END AS period_end_date

FROM silver.dhis2_observation AS o

LEFT JOIN silver.dhis2_dataset AS d
    ON d.source_instance = o.source_instance
   AND d.dataset_id = o.dataset_id;
