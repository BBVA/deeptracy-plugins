# Copyright 2017 BBVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utils to be used in the API"""
from flask import jsonify
from deeptracy_api.api.exc import APIError


def api_error_response(msg: str):
    """Returns a json representation of an API error

    :param msg: Message to be returned
    """
    return jsonify({'error': {'msg': msg}})


def get_required_field(data: dict, field: str):
    """Checks a required field in a dictionary that comes from a request
    If the field is not present or is '', raises an APIError

    :param data: Dictionary to check for the field
    :param field: Field key to check

    :raises APIError: on not found or empty field
    :rtype value: field value if the field is found in the dictionary
    """
    field_value = data.get(field, None)
    if field_value is None or field_value == '':
        raise APIError('missing {}'.format(field), status_code=400)
    return field_value