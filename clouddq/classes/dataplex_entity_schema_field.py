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

from clouddq.utils import assert_not_none_or_empty


@dataclass
class DataplexEntitySchemaField:
    """ """

    name: str
    data_type: str
    mode: str

    def to_dict(self: DataplexEntitySchemaField) -> dict:
        """
        Args:
          self: DataplexEntitySchemaField:

        Returns:

        """

        output = {
            "name": self.name,
            "data_type": self.data_type,
            "mode": self.mode,
        }

        return dict(output)

    @classmethod
    def from_dict(
        cls: DataplexEntitySchemaField, kwargs: dict
    ) -> DataplexEntitySchemaField:

        name = kwargs.get("name")
        assert_not_none_or_empty(
            value=name, error_msg="Name: must define non-empty value: 'name'."
        )

        data_type = kwargs.get("data_type")
        assert_not_none_or_empty(
            value=data_type,
            error_msg="DataType: must define non-empty value: 'data_type'.",
        )

        mode = kwargs.get("mode")
        assert_not_none_or_empty(
            value=mode, error_msg="Mode: must define non-empty value: 'mode'."
        )

        return DataplexEntitySchemaField(
            name=name,
            data_type=data_type,
            mode=mode,
        )
