# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

import pytest

from clouddq import lib
from clouddq.classes.dq_configs_cache import DqConfigsCache
from clouddq.classes.dq_entity import DqEntity
from clouddq.classes.dq_entity import get_custom_entity_configs
from clouddq.classes.dq_row_filter import DqRowFilter
from clouddq.classes.dq_rule import DqRule
from clouddq.classes.dq_rule_binding import DqRuleBinding
from clouddq.classes.rule_type import RuleType


logger = logging.getLogger(__name__)


class TestClasses:

    def test_dq_rule_parse_failure(self):
        """ """
        with pytest.raises(ValueError):
            DqRule.from_dict(
                rule_id="valid",
                kwargs={
                    "rule_type": "",
                },
            )

    def test_dq_entity_missing_columns_failure(self):
        """ """
        dq_entity_dict_not_valid = {
            "source_database": "BIGQUERY",
            "table_name": "valid",
            "database_name": "valid",
            "instance_name": "valid",
        }
        with pytest.raises(ValueError):
            DqEntity.from_dict(entity_id="valid", kwargs=dq_entity_dict_not_valid)

    def test_dq_entity_invalid_source_database(self):
        """ """
        dq_entity_dict_not_valid = {
            "source_database": "invalid",
            "table_name": "valid",
            "database_name": "valid",
            "instance_name": "valid",
            "columns": {
                "TEST_COLUMN": {
                    "description": "test column description",
                    "name": "test_column",
                    "data_type": "STRING"
                }},
        }
        with pytest.raises(NotImplementedError):
            DqEntity.from_dict(entity_id="valid", kwargs=dq_entity_dict_not_valid)

    @pytest.mark.parametrize(
        "configs_map,source_database,expected",
        [
            pytest.param(
                {"table_name": "table", "dataset_name": "dataset", "project_name": "project"},
                "BIGQUERY",
                "dataset",
                id="bigquery_native"
            ),
            pytest.param(
                {"table_name": "table", "database_name": "dataset", "project_name": "project"},
                "BIGQUERY",
                "dataset",
                id="bigquery_backwards_compatible"
            ),
        ],
    )
    def test_get_custom_entity_configs_database_name(self, configs_map, source_database, expected):
        output = get_custom_entity_configs('test', configs_map, source_database, "database_name")
        assert output == expected

    @pytest.mark.parametrize(
        "configs_map,source_database,expected",
        [
            pytest.param(
                {"table_name": "table", "lake_name": "lake", "zone_name": "zone", "project_name": "project"},
                "DATAPLEX_BQ_EXTERNAL_TABLE",
                "lake_zone",
                id="dataplex_native"
            ),
            pytest.param(
                {"table_name": "table", "database_name": "lake_zone", "project_name": "project"},
                "DATAPLEX_BQ_EXTERNAL_TABLE",
                "lake_zone",
                id="dataplex_backwards_compatible"
            ),
        ],
    )
    def test_get_custom_entity_configs_database_name_fail(self, configs_map, source_database, expected):
        with pytest.raises(NotImplementedError):
            get_custom_entity_configs('test', configs_map, source_database, "database_name")

    def test_dq_entity_parse_bigquery_configs(self):
        """ """
        bq_entity_input_dict = {
            "source_database": "BIGQUERY",
            "table_name": "table_name",
            "dataset_name": "dataset_name",
            "project_name": "project_name",
            "columns": {
                "TEST_COLUMN": {
                    "description": "test column description",
                    "name": "test_column",
                    "data_type": "STRING"
                }},
        }
        bq_entity_configs = DqEntity.from_dict(entity_id="test_bq_entity", kwargs=bq_entity_input_dict)
        bq_entity_configs_expected = {
            "test_bq_entity": {
                "source_database": "BIGQUERY",
                "table_name": "table_name",
                "database_name": "dataset_name",
                "dataset_name": "dataset_name",
                "instance_name": "project_name",
                "project_name": "project_name",
                "columns": {
                    "TEST_COLUMN": {
                        "description": "test column description",
                        "name": "test_column",
                        "data_type": "STRING"
                    }},
            }
        }
        assert bq_entity_configs.to_dict() == bq_entity_configs_expected

    def test_dq_entity_parse_bigquery_configs_backwards_compatible(self):
        """ """
        bq_entity_input_dict = {
            "source_database": "BIGQUERY",
            "table_name": "table_name",
            "database_name": "dataset_name",
            "instance_name": "project_name",
            "columns": {
                "TEST_COLUMN": {
                    "description": "test column description",
                    "name": "test_column",
                    "data_type": "STRING"
                }},
        }
        bq_entity_configs = DqEntity.from_dict(entity_id="test_bq_entity", kwargs=bq_entity_input_dict)
        bq_entity_configs_expected = {
            "test_bq_entity": {
                "source_database": "BIGQUERY",
                "table_name": "table_name",
                "database_name": "dataset_name",
                "dataset_name": "dataset_name",
                "instance_name": "project_name",
                "project_name": "project_name",
                "columns": {
                    "TEST_COLUMN": {
                        "description": "test column description",
                        "name": "test_column",
                        "data_type": "STRING"
                    }},
            }
        }
        assert bq_entity_configs.to_dict() == bq_entity_configs_expected

    def test_dq_entity_parse_dataplex_configs_fails(self):
        """ """
        dataplex_entity_input_dict = {
            "source_database": "DATAPLEX_BQ_EXTERNAL_TABLE",
            "table_name": "table",
            "lake_name": "lake",
            "zone_name": "zone",
            "project_name": "project_name",
            "columns": {
                "TEST_COLUMN": {
                    "description": "test column description",
                    "name": "test_column",
                    "data_type": "STRING"
                }},
        }
        with pytest.raises(NotImplementedError):
            dataplex_entity_configs = DqEntity.from_dict(
                entity_id="test_dataplex_entity",
                kwargs=dataplex_entity_input_dict
            )
            dataplex_entity_configs_expected = {
                "test_dataplex_entity": {
                    "source_database": "DATAPLEX_BQ_EXTERNAL_TABLE",
                    "table_name": "table",
                    "database_name": "lake_zone",
                    "instance_name": "project_name",
                    "columns": {
                        "TEST_COLUMN": {
                            "description": "test column description",
                            "name": "test_column",
                            "data_type": "STRING"
                        }},
                }
            }
            assert dataplex_entity_configs.to_dict() == dataplex_entity_configs_expected

    def test_dq_filter_parse_failure(self):
        """ """
        with pytest.raises(ValueError):
            DqRowFilter.from_dict(
                row_filter_id="valid",
                kwargs=dict(),
            )

    def test_dq_rule_binding_invalid_id_parse_failure(self):
        """ """
        dq_rule_binding_dict_not_valid = {
            "entity_id": "",
            "column_id": "",
            "row_filter_id": "",
            "rule_ids": ["invalid"],
        }
        with pytest.raises(ValueError):
            DqRuleBinding.from_dict(
                rule_binding_id="valid",
                kwargs=dq_rule_binding_dict_not_valid,
            )

    def test_dq_rule_binding_invalid_list_parse_failure(self):
        """ """
        dq_rule_binding_dict_not_valid = {
            "entity_id": "valid",
            "column_id": "valid",
            "row_filter_id": "valid",
            "rule_ids": "invalid",
        }
        with pytest.raises(ValueError):
            DqRuleBinding.from_dict(
                rule_binding_id="valid",
                kwargs=dq_rule_binding_dict_not_valid,
            )

    def test_rule_type_not_implemented(self):
        """ """
        with pytest.raises(NotImplementedError):
            RuleType.to_sql("not_implemented", dict())

    @pytest.mark.parametrize(
        "params",
        [
            dict(),
            {"custom_sql_expr": ""},
            {"custom_sql_expr": "'; drop table Students; select ?;--"},
            {"custom_sql_expr": "'; drop table Students; select ?;#"},
            {"custom_sql_expr": "'; drop table Students; select ?/*"},
        ],
    )
    def test_rule_type_custom_to_sql_failure(self, params):
        """ """
        with pytest.raises(ValueError):
            RuleType.CUSTOM_SQL_EXPR.to_sql(params)

    def test_rule_type_custom_to_sql_special_characters(self):
        """ """
        params = {"custom_sql_expr": "column_name in (select column from `project-id.dataset_id.table_id`)"}
        sql = RuleType.CUSTOM_SQL_EXPR.to_sql(params).substitute(column="column_name")
        assert sql == params["custom_sql_expr"]

    def test_rule_type_custom_to_sql(self):
        """ """
        params = {"custom_sql_expr": "length(column_name) < 20"}
        sql = RuleType.CUSTOM_SQL_EXPR.to_sql(params).substitute(column="column_name")
        assert sql == params["custom_sql_expr"]

    def test_rule_type_not_null(self):
        """ """
        expected = "column_name IS NOT NULL"
        sql = RuleType.NOT_NULL.to_sql(params={}).substitute(column="column_name")
        assert sql == expected

    def test_rule_type_not_blank(self):
        """ """
        expected = "TRIM(column_name) != ''"
        sql = RuleType.NOT_BLANK.to_sql(params={}).substitute(column="column_name")
        assert sql == expected

    @pytest.mark.parametrize(
        "params",
        [
            dict(),
            {"pattern": ""},
            {"pattern": "'; drop table Students; select true;--"},
        ],
    )
    def test_rule_type_regex_to_sql_failure(self, params):
        """ """
        with pytest.raises(ValueError):
            RuleType.REGEX.to_sql(params)

    def test_rule_type_regex_to_sql(self):
        """ """
        params = {"pattern": "^[^@]+[@]{1}[^@]+$"}
        sql = RuleType.REGEX.to_sql(params).substitute(column="column_name")
        expected = "REGEXP_CONTAINS( CAST( column_name  AS STRING), '^[^@]+[@]{1}[^@]+$' )"
        assert sql == expected

    def test_configs_cache_rules(self, temp_configs_dir):

        def assertRulesEqual(rule_id, rule_config, rule_loaded):

            print(f"rule ID {rule_id}")
            print(f"  rule: {rule_loaded}")
            print(f"  dict: {rule_loaded.to_dict()[rule_id]}")
            print(f"  conf: {rule_config}")

            assert DqRule.from_dict(rule_id, rule_config) == rule_loaded, rule_id

            # To compare the dictionaries, we need to remove the SQL expression.
            # To avoid relying on the specific key, just compare the keys from
            # the original dict
            loaded_rule_dict = rule_loaded.to_dict()[rule_id]
            loaded_rule_dict_clean = {}
            for k in loaded_rule_dict:
                if k in rule_config:
                    loaded_rule_dict_clean[k] = loaded_rule_dict[k]

            assert rules[rule_id] == loaded_rule_dict_clean, rule_id

        rules = lib.load_rules_config(temp_configs_dir)

        # Skip custom SQL because we will be going back and forth
        # from dicts to objects and we haven't bound SQL params yet
        complex_types = ['CUSTOM_SQL_EXPR', 'CUSTOM_SQL_STATEMENT']
        rule_ids = sorted([id for id in rules.keys() if rules[id]['rule_type'] not in complex_types])

        rule_id1 = rule_ids[0]
        rule_ids = rule_ids[1:]

        # Give one rule a dimension
        rules[rule_id1]['dimension'] = 'completeness'

        cache = DqConfigsCache()
        cache.load_all_rules_collection(rules)

        rule_config1 = rules[rule_id1]
        rule_loaded1 = cache.get_rule_id(rule_id1)
        assert rule_loaded1.dimension == 'completeness', rule_id1
        assertRulesEqual(rule_id1, rule_config1, rule_loaded1)

        # test the other rules
        for rule_id in rule_ids:

            rule_config = rules[rule_id]
            rule_loaded = cache.get_rule_id(rule_id)
            assert rule_loaded.dimension is None, rule_id
            assertRulesEqual(rule_id, rule_config, rule_loaded)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, '-vv', '-rP', '-n', 'auto']))
