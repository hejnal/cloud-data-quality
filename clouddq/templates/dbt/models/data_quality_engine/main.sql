-- Copyright 2021 Google LLC
--
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.
-- You may obtain a copy of the License at
--
--      http://www.apache.org/licenses/LICENSE-2.0
--
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.

{{
  config(
    materialized = 'ephemeral',
  )
}}
{%- for rule_binding_id in var('target_rule_binding_ids') -%}
    SELECT
        '{{ invocation_id }}'  AS invocation_id,
        execution_ts,
        rule_binding_id,
        rule_id,
        table_id,
        column_id,
        dimension,
        metadata_json_string,
        configs_hashsum,
        dataplex_lake,
        dataplex_zone,
        dataplex_asset_id,
        dq_run_id,
        progress_watermark,
        rows_validated,
        complex_rule_validation_errors_count,
        last_modified,
        CASE WHEN complex_rule_validation_errors_count IS NOT NULL
          THEN rows_validated - complex_rule_validation_errors_count
          ELSE COUNTIF(simple_rule_row_is_valid IS TRUE)
        END
        AS success_count,
        CASE WHEN complex_rule_validation_errors_count IS NOT NULL
          THEN (rows_validated - complex_rule_validation_errors_count) / rows_validated
          ELSE COUNTIF(simple_rule_row_is_valid IS TRUE) / rows_validated
        END
        AS success_percentage,
        CASE WHEN complex_rule_validation_errors_count IS NOT NULL
          THEN complex_rule_validation_errors_count
          ELSE COUNTIF(simple_rule_row_is_valid IS FALSE)
        END
        AS failed_count,
        CASE WHEN complex_rule_validation_errors_count IS NOT NULL
          THEN complex_rule_validation_errors_count / rows_validated
          ELSE COUNTIF(simple_rule_row_is_valid IS FALSE) / rows_validated
        END
        AS failed_percentage,
        COUNTIF(column_value IS NULL) AS null_count,
        COUNTIF(column_value IS NULL) / rows_validated AS null_percentage
    FROM
        {{ ref(rule_binding_id) }}
    GROUP BY
        1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17
    {% if loop.nextitem is defined %}
    UNION ALL
    {% endif %}
{%- endfor -%}
