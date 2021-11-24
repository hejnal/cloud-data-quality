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

"""todo: add classes docstring."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import typing

from clouddq.utils import assert_not_none_or_empty


class DataplexSupportedSchemes(str, Enum):
    DATAPLEX = "dataplex://"


class DataplexUnsupportedSchemes(str, Enum):
    BIGQUERY = "bigquery://"
    LOCAL = "local://"
    GS = "gs://"


@dataclass
class EntityUri:
    uri: str

    @property
    def scheme(self):
        return self.uri.split("/")[0].replace(":", "")

    @property
    def entity_id(self):
        return self.uri.split("/")[11]

    @property
    def project_id(self):
        return self.uri.split("/")[3]

    @property
    def location(self):
        return self.uri.split("/")[5]

    @property
    def lake(self):
        return self.uri.split("/")[7]

    @property
    def zone(self):
        return self.uri.split("/")[9]

    def get_db_primary_key(self):
        if self.scheme == "dataplex":
            return (
                    f"projects/{self.project_id}/locations/{self.location}/"
                    + f"lakes/{self.lake}/zones/{self.zone}/entities/{self.entity_id}"  # noqa: W503
            )
        else:
            raise NotImplementedError(
                f"EntityUri.get_db_primary_key() for scheme {self.scheme} is not yet supported."
            )

    @property
    def configs(self):
        return {
            "projects": self.project_id,
            "locations": self.location,
            "lakes": self.lake,
            "zones": self.zone,
            "entities": self.entity_id,
        }

    @classmethod
    def from_uri(cls: EntityUri, entity_uri: str) -> EntityUri:

        cls.validate_uri_and_assert(entity_uri=entity_uri)

        return EntityUri(
            uri=entity_uri,
        )

    def to_dict(self: EntityUri) -> dict:
        """
        Serialize Entity URI to dictionary
        Args:
          self: EntityUri:

        Returns:

        """

        output = {
            "uri": self.uri,
            "scheme": self.scheme,
            "entity_id": self.entity_id,
            "db_primary_key": self.get_db_primary_key(),
            "configs": self.configs,
        }

        return dict(output)

    @classmethod
    def convert_entity_uri_to_dict(
            cls: EntityUri, entity_uri: str, delimiter: str
    ) -> dict:

        entity_uri_list = entity_uri.split(delimiter)
        return dict(zip(entity_uri_list[::2], entity_uri_list[1::2]))

    @classmethod
    def check_for_special_characters(cls: EntityUri, entity_uri: str):
        entity_uri_without_scheme = entity_uri.split("//")[1]
        special_characters = ["@", "#", "?", ":"]
        if any(spec_char in entity_uri_without_scheme for spec_char in special_characters):
            raise ValueError(
                f"Invalid Entity URI : {entity_uri}, Special characters [@, #, ?, : ] are not allowed."
            )

    @classmethod
    def check_for_valid_scheme(cls: EntityUri, scheme: str):
        if any(unsupported_scheme.value == scheme for unsupported_scheme in DataplexUnsupportedSchemes):
            raise NotImplementedError(f"{scheme} scheme is not implemented.")

        if any(supported_scheme.value != scheme for supported_scheme in DataplexSupportedSchemes):
            raise ValueError(f"{scheme} scheme is invalid.")

    @classmethod
    def check_for_valid_entity_uri_dict(cls: EntityUri, entity_uri: str, entity_uri_dict: dict):

        project_id = entity_uri_dict.get("projects")
        assert_not_none_or_empty(
            value=project_id,
            error_msg=f"Required argument project_id is missing in the URI : {entity_uri}",
        )

        location_id = entity_uri_dict.get("locations")
        assert_not_none_or_empty(
            value=location_id,
            error_msg=f"Required argument location_id is missing in the URI : {entity_uri}",
        )

        lake_id = entity_uri_dict.get("lakes")
        assert_not_none_or_empty(
            value=lake_id,
            error_msg=f"Required argument lake_id is missing in the URI : {entity_uri}",
        )

        zone_id = entity_uri_dict.get("zones")
        assert_not_none_or_empty(
            value=zone_id,
            error_msg=f"Required argument zone_id is missing in the URI : {entity_uri}",
        )

        entity_id = entity_uri_dict.get("entities")
        assert_not_none_or_empty(
            value=entity_id,
            error_msg=f"Required argument entity_id is missing in the URI : {entity_uri}",
        )

        if entity_id.endswith("*"):
            raise NotImplementedError(
                f"{entity_id} wildcard filter is not implemented."
            )


    @classmethod
    def validate_uri_and_assert(
            cls: EntityUri, entity_uri: str
    ) -> typing.Any:  # noqa: C901

        entity_uri_dict = cls.convert_entity_uri_to_dict(entity_uri, delimiter="/")
        scheme = entity_uri.split("//")[0] + "//"
        EntityUri.check_for_valid_scheme(scheme=scheme)
        EntityUri.check_for_special_characters(entity_uri=entity_uri)

        valid_entity_uri_keys = ["dataplex:", "projects", "locations", "lakes", "zones", "entities"]
        if any(key not in valid_entity_uri_keys for key in entity_uri_dict):
            raise ValueError(f"Invalid Entity URI : {entity_uri}")

        if "projects" not in entity_uri_dict:
            if "locations" not in entity_uri_dict:
                if "lakes" not in entity_uri_dict:
                    if "zones" in entity_uri_dict:
                        raise NotImplementedError(
                            f"{entity_uri} is not implemented."
                        )

        EntityUri.check_for_valid_entity_uri_dict(entity_uri=entity_uri, entity_uri_dict=entity_uri_dict)
