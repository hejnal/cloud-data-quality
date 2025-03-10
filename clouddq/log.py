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

from datetime import datetime

import json
import logging
import sys
import traceback


APP_VERSION = "0.4.0"
APP_NAME = "clouddq"
LOG_LEVEL = logging._nameToLevel["DEBUG"]


class JsonEncoderStrFallback(json.JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError as exc:
            if "not JSON serializable" in str(exc):
                return str(obj)
            raise


class JsonEncoderDatetime(JsonEncoderStrFallback):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            return super().default(obj)


class JSONFormatter(logging.Formatter):
    def __init__(self):
        super().__init__()

    def format(self, record):
        record.msg = json.dumps(
            {
                "severity": record.levelname,
                "time": datetime.utcfromtimestamp(record.created)
                .astimezone()
                .isoformat()
                .replace("+00:00", "Z"),
                "logging.googleapis.com/sourceLocation": {
                    "file": record.pathname or record.filename,
                    "function": record.funcName,
                    "line": record.lineno,
                },
                "exception": record.exc_info,
                "traceback": traceback.format_exception(*record.exc_info)
                if record.exc_info
                else None,
                "message": record.getMessage(),
                "logging.googleapis.com/labels": {
                    "name": APP_NAME,
                    "releaseId": APP_VERSION,
                },
            },
            cls=JsonEncoderDatetime,
        )
        return super().format(record)


def get_json_logger():
    json_logger = logging.getLogger("clouddq-json-logger")
    if not len(json_logger.handlers):
        json_logger.setLevel(LOG_LEVEL)
        logging_stream_handler = logging.StreamHandler(sys.stdout)
        logging_stream_handler.setFormatter(JSONFormatter())
        json_logger.addHandler(logging_stream_handler)
    return json_logger


def get_logger():
    logger = logging.getLogger("clouddq")
    if not len(logger.handlers):
        logger.setLevel(LOG_LEVEL)
        logging_stream_handler = logging.StreamHandler(sys.stderr)
        stream_formatter = logging.Formatter(
            "{asctime} {name} {levelname:8s} {message}", style="{"
        )
        logging_stream_handler.setFormatter(stream_formatter)
        logger.addHandler(logging_stream_handler)
    return logger
