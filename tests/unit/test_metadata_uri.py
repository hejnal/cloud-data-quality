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

import pytest

from clouddq.classes.dq_entity_uri import EntityUri


class TestEntityURI:

    @pytest.mark.parametrize(
        "entity_uri,error_type",
        [
            pytest.param(
                "dataplex://",
                ValueError,
                id="incomplete_dataplex"
            ),
            pytest.param(
                "bigquery://",
                ValueError,
                id="incomplete_bigquery"
            ),
            pytest.param(
                "local://",
                NotImplementedError,
                id="incomplete_local"
            ),
            pytest.param(
                "gs://",
                NotImplementedError,
                id="not_implemented_scheme"
            ),
            pytest.param(
                "dataplex:bigquery://",
                NotImplementedError,
                id="invalid_scheme"
            ),
            pytest.param(
                "dataplex://projects/project-id/locations/us-central1/lakes/lake-id/zones/zone-id/entities",
                ValueError,
                id="missing_entity_id"
            ),
            pytest.param(
                "dataplex://projects/project-id/locations/us-central1/lakes/lake-id/zones/zone-id/entities/",
                ValueError,
                id="missing_entity_id_1"
            ),
            pytest.param(
                "dataplex://projects@",
                ValueError,
                id="unsupported_@"
            ),
            pytest.param(
                "dataplex://projects:",
                ValueError,
                id="unsupported_:"
            ),
            pytest.param(
                "dataplex://projects?",
                ValueError,
                id="unsupported_?"
            ),
            pytest.param(
                "dataplex://projects#",
                ValueError,
                id="unsupported_#"
            ),
        ],
    )
    def test_entity_uri_parse_failure(self, entity_uri, error_type):
        """ """
        with pytest.raises(error_type):
            EntityUri.from_uri(entity_uri)

    def test_entity_uri_parse_dataplex_uri_without_default_configs(self):
        """ """
        entity_uri = "dataplex://projects/project-id/locations/us-central1/lakes" \
                     "/lake-id/zones/zone-id/entities/entity-id"
        parsed_uri = EntityUri.from_uri(entity_uri)
        expected_entity_dict = {
            "uri": "dataplex://projects/project-id/locations/us-central1/lakes"
                   "/lake-id/zones/zone-id/entities/entity-id",
            "scheme": "dataplex",
            "entity_id": "entity-id",
            "db_primary_key": "projects/project-id/locations/us-central1/lakes/lake-id/zones/zone-id/entities/entity-id",  # noqa: E501
            "configs": {
                "projects": "project-id",
                "locations": "us-central1",
                "lakes": "lake-id",
                "zones": "zone-id",
                "entities": "entity-id",
            }
        }
        assert parsed_uri.scheme == expected_entity_dict["scheme"]
        assert parsed_uri.uri_configs_string == (
            "projects/project-id/locations/us-central1/lakes"
            "/lake-id/zones/zone-id/entities/entity-id"
            )
        assert parsed_uri.default_configs is None
        assert parsed_uri.complete_uri_string == expected_entity_dict["uri"]
        assert parsed_uri.get_entity_id() == expected_entity_dict["entity_id"]
        assert parsed_uri.configs_dict == expected_entity_dict["configs"]
        assert parsed_uri.get_db_primary_key() == expected_entity_dict["db_primary_key"]
        assert parsed_uri.to_dict() == expected_entity_dict

    @pytest.mark.parametrize(
        "entity_uri,error_type",
        [
            pytest.param(
                "dataplex://project/project-id/locations/us-central1/lakes/lake-id/zones/zone-id/entities/entity-id",  # noqa: E501
                ValueError,
                id="typo_project"
            ),
            pytest.param(
                "dataplex://projects/project-id/location/us-central1/lakes/lake-id/zones/zone-id/entities/entity-id",
                ValueError,
                id="typo_location"
            ),
            pytest.param(
                "dataplex://projects/project-id/locations/us-central1/lake/lake-id/zones/zone-id/entities/entity-id",
                ValueError,
                id="typo_lake"
            ),
            pytest.param(
                "dataplex://projects/project-id/locations/us-central1/lakes/lake-id/zone/zone-id/entities/entity-id",
                ValueError,
                id="typo_zone"
            ),
            pytest.param(
                "dataplex://projects/project-id/locations/us-central1/lakes/lake-id/zones/zone-id/entity/entity-id",
                ValueError,
                id="typo_entity"
            ),
            pytest.param(
                "dataplex://projects/project-id/locations/us-central1/lakes/lake-id/zones/zone-id/entity/entity-id",
                ValueError,
                id="typo_entity"
            ),
            pytest.param(
                "dataplex://project/project-id/location/us-central1/lakes/lake-id/zones/zone-id/entities/entity-id",
                ValueError,
                id="typo_project_location"
            ),
            pytest.param(
                "dataplex://projects/project-id/location/us-central1/lake/lake-id/zones/zone-id/entities/entity-id",
                ValueError,
                id="typo_location_lake"
            ),
            pytest.param(
                "dataplex://project/project-id/location/us-central1/lake/lake-id/zones/zone-id/entities/entity-id",
                ValueError,
                id="typo_project_location_lake"
            ),
            pytest.param(
                "dataplex://project/project-id/location/us-central1/lake/lake-id/zone/zone-id/entities/entity-id",
                ValueError,
                id="typo_project_location_lake_zone"
            ),
            pytest.param(
                "dataplex://project/project-id/location/us-central1/lake/lake-id/zone/zone-id/entity/entity-id",
                ValueError,
                id="typo_project_location_lake_zone_entity"
            ),
            pytest.param(
                "dataplex://project/project-id/location//lakes/lake-id/zones/zone-id/entities/entity-id",
                ValueError,
                id="missing_location"
            ),
        ],
    )
    def test_entity_uri_typo_parse_failure(self, entity_uri, error_type):
        with pytest.raises(error_type):
            EntityUri.from_uri(entity_uri)

    def test_entity_uri_parse_asset_id_failure(self):
        """ """
        entity_uri = "dataplex://projects/project-id/locations/us-central1/lakes" \
                     "/lake-id/zones/zone-id/assets/asset-id"

        with pytest.raises(ValueError):
            EntityUri.from_uri(entity_uri)

    def test_entity_uri_parse_partition_failure(self):
        """ """
        entity_uri = "dataplex://projects/project-id/locations/us-central1/lakes" \
                     "/lake-id/zones/zone-id/partitions/partition-id"
        with pytest.raises(ValueError):
            EntityUri.from_uri(entity_uri)

    def test_entity_uri_parse_elide_project_lake_id_failure(self):
        """ """
        entity_uri = "dataplex://zones/zone-id/entities/entity-id"
        default_configs = {
            "projects": "project-id",
            "locations": "us-central1",
            "lakes": "lake-id",
        }
        # This should fail without metadata_defaults
        with pytest.raises(ValueError):
            EntityUri.from_uri(entity_uri)
        parsed_uri = EntityUri.from_uri(uri_string=entity_uri, default_configs=default_configs)
        assert parsed_uri.complete_uri_string == entity_uri
        assert parsed_uri.get_db_primary_key() == (
            "projects/project-id/locations/us-central1/lakes"
            "/lake-id/zones/zone-id/entities/entity-id"
            )

    def test_entity_uri_parse_override_project_lake_id_failure(self):
        """ """
        entity_uri = "dataplex://projects/project-id-2/zones/zone-id/entities/entity-id"
        default_configs = {
            "projects": "project-id-1",
            "locations": "us-central1",
            "lakes": "lake-id",
        }
        # This should fail without metadata_defaults
        with pytest.raises(ValueError):
            EntityUri.from_uri(entity_uri)
        parsed_uri = EntityUri.from_uri(uri_string=entity_uri, default_configs=default_configs)
        assert parsed_uri.complete_uri_string == entity_uri
        assert parsed_uri.get_db_primary_key() == (
            "projects/project-id-2/locations/us-central1/lakes"
            "/lake-id/zones/zone-id/entities/entity-id"
            )

    def test_entity_uri_parse_glob_failure(self):
        """ """
        entity_uri = "dataplex://projects/project-id/locations/us-central1/lakes" \
                     "/lake-id/zones/zone-id/entities/test_entity_*"
        # This should be supported eventually
        with pytest.raises(NotImplementedError):
            EntityUri.from_uri(entity_uri)

    def test_entity_uri_parse_bigquery_uri_without_default_configs(self):
        """ """
        bigquery_uri = "bigquery://projects/project-id/datasets/dataset-id/tables/table-id"
        parsed_uri = EntityUri.from_uri(bigquery_uri)
        print(parsed_uri)
        expected_entity_dict = {
            "uri": "bigquery://projects/project-id/datasets/dataset-id/tables/table-id",
            "scheme": "bigquery",
            "entity_id": "projects/project-id/datasets/dataset-id/tables/table-id",
            "db_primary_key": "projects/project-id/datasets/dataset-id/tables/table-id",
            "configs": {
                "projects": "project-id",
                "datasets": "dataset-id",
                "tables": "table-id",
            }
        }
        assert parsed_uri.scheme == expected_entity_dict["scheme"]
        assert parsed_uri.uri_configs_string == "projects/project-id/datasets/dataset-id/tables/table-id"
        assert parsed_uri.default_configs is None
        assert parsed_uri.complete_uri_string == expected_entity_dict["uri"]
        assert parsed_uri.get_entity_id() == expected_entity_dict["entity_id"]
        assert parsed_uri.get_db_primary_key() == expected_entity_dict["db_primary_key"]
        assert parsed_uri.configs_dict == expected_entity_dict["configs"]
        assert parsed_uri.to_dict() == expected_entity_dict


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, '-vv', '-rP', '-n', 'auto']))
