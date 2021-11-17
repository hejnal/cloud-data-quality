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

from clouddq.classes.dataplex_entity import DataplexEntity
import logging
import json

logger = logging.getLogger(__name__)

class TestMetadataIntegration:

    @pytest.mark.parametrize(
        "entity_id,expected_obj,expected_status",
        [
            pytest.param(
                'contact_details',
                {
                    "name": f"projects/<gcp_project_id>/locations/<gcp_dataplex_region>/lakes/<gcp_dataplex_lake_name>/"
                            f"zones/<gcp_dataplex_zone_id>/entities/contact_details",
                    "createTime": "2021-11-11T07:37:14.212950Z", "updateTime": "2021-11-11T07:37:14.212950Z",
                    "id": "contact_details", "type": "TABLE", "asset": "clouddq-test-asset-curated-bigquery",
                    "dataPath": f"projects/<gcp_project_id>/datasets/"
                                f"<gcp_dataplex_bigquery_dataset_id>/tables/contact_details",
                    "system": "BIGQUERY", "format": {"format": "OTHER"}, "schema": {
                    "fields": [{"name": "row_id", "type": "STRING", "mode": "REQUIRED"},
                               {"name": "contact_type", "type": "STRING", "mode": "REQUIRED"},
                               {"name": "value", "type": "STRING", "mode": "REQUIRED"},
                               {"name": "ts", "type": "TIMESTAMP", "mode": "REQUIRED"}]}},
                "SUCCEEDED",
                id="contact_details_with_full_entity_view"
            ),
            pytest.param(
                'asset_bucket',
                {
                    "name": f"projects/<gcp_project_id>/locations/<gcp_dataplex_region>/lakes/"
                            f"<gcp_dataplex_lake_name>/zones/<gcp_dataplex_zone_id>/"
                            f"entities/d6d0e5bc-163c-4993-8da2-68b4bad58633",
                    "createTime": "2021-10-25T02:35:36.207049Z", "updateTime": "2021-10-25T02:35:36.207049Z",
                    "id": "asset_bucket", "type": "TABLE", "asset": "asset-bucket",
                    "dataPath": f"gs://<gcp_dataplex_bucket_name>", "system": "CLOUD_STORAGE",
                    "format": {"format": "CSV", "mimeType": "text/csv",
                               "csv": {"encoding": "UTF-8", "headerRows": 1, "delimiter": ","}}, "schema": {
                    "fields": [{"name": "row_id", "type": "STRING", "mode": "NULLABLE"},
                               {"name": "contact_type", "type": "STRING", "mode": "NULLABLE"},
                               {"name": "value", "type": "STRING", "mode": "NULLABLE"},
                               {"name": "ts", "type": "STRING", "mode": "NULLABLE"}]}},
                "FAILED",
                id="asset_bucket_with_full_entity_view"
            ),
        ]
    )
    def test_dataplex_metadata_get_entity_valid(self,
                                                test_dq_dataplex_client,
                                                gcp_dataplex_zone_id,
                                                entity_id,
                                                expected_obj,
                                                expected_status,
                                                request, ):

        response = test_dq_dataplex_client.get_dataplex_entity(zone_id=gcp_dataplex_zone_id,
                                                      entity_id=entity_id,)
        assert response.status_code == 200
        print(response.text)

        expected_obj["name"] = expected_obj["name"].replace("<gcp_project_id>",
                                                            request.getfixturevalue("gcp_project_id")) \
            .replace("<gcp_dataplex_region>", request.getfixturevalue("gcp_dataplex_region")) \
            .replace("<gcp_dataplex_lake_name>", request.getfixturevalue("gcp_dataplex_lake_name")) \
            .replace("<gcp_dataplex_zone_id>", request.getfixturevalue("gcp_dataplex_zone_id"))

        expected_obj["dataPath"] = expected_obj["dataPath"].replace("<gcp_project_id>",
                                                                    request.getfixturevalue("gcp_project_id")) \
            .replace("<gcp_dataplex_bigquery_dataset_id>", request.getfixturevalue("gcp_dataplex_bigquery_dataset_id")) \
            .replace("<gcp_dataplex_bucket_name>", request.getfixturevalue("gcp_dataplex_bucket_name"))

        expected_entity = DataplexEntity.from_dict(kwargs=expected_obj)

        actual_entity: DataplexEntity = DataplexEntity.from_dict(kwargs=json.loads(response.text))

        print(f"Response Object is \n {actual_entity}")

        if actual_entity == expected_entity:
            actual_status = "SUCCEEDED"
        else:
            actual_status = "FAILED"

        assert actual_status == expected_status

    # We need another test to assert exact entity number once we have a fixture for creating entities
    def test_dataplex_metadata_list_entities(self,
                                             test_dq_dataplex_client,
                                             gcp_dataplex_zone_id, ):
        print(f"zone id is {gcp_dataplex_zone_id}")
        response = test_dq_dataplex_client.list_dataplex_entities(zone_id=gcp_dataplex_zone_id)
        print(f"Response is \n {response}")
        print(f"Total Entities are {len(response['entities'])}")
        assert len(response['entities']) > 0

    def test_dataplex_metadata_list_entities_with_prefix(self,
                                                         test_dq_dataplex_client,
                                                         gcp_dataplex_zone_id, ):
        print(f"zone id  is {gcp_dataplex_zone_id}")
        prefix = 'test_clouddq_'
        response = test_dq_dataplex_client.list_dataplex_entities(zone_id=gcp_dataplex_zone_id, prefix=prefix)
        print(f"Response is \n {response}")
        if "entities" in response:
            print(f"Total Entities are {len(response['entities'])}")
        assert len(response['entities']) > 0


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, '-vv', '-rP']))
