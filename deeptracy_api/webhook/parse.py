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

import logging

from deeptracy_api.webhook.providers.bitbucket import parse_from_bitbucket
from deeptracy_api.webhook.providers.github import parse_from_github

logger = logging.getLogger(__name__)


def parse_data(data):
    """
    Parse a JSON data payload from diferent repository providers.
    """
    if 'actor' in data \
            and 'links' in data['actor'] \
            and 'self' in data['actor']['links'] \
            and 'href' in data['actor']['links']['self'] \
            and 'bitbucket' in data['actor']['links']['self']['href']:
        logger.debug("BitBucket")
        parsed_data = parse_from_bitbucket(data)
    elif 'repository' in data and 'url' in data['repository']:
        logger.debug("GitHub")
        parsed_data = parse_from_github(data)
    else:
        parsed_data = []

    return parsed_data

def handle_data(response_data):
    """
    Automatically parse the JSON data received and dispatch the requests
    to the appropriate handlers specified in settings.py.
    """
    data_list = parse_data(response_data)
    logger.debug("raw data %s" % data_list)

    for parsed_data in data_list:
        provider_info = settings.PROVIDERS.get(parsed_data.provider, None)

        if provider_info:
            handler = provider_info.get('post_receive_handler', None)
            if handler:
                handler(parsed_data)