#!/usr/bin/env python

from __future__ import print_function
from builtins import str
from builtins import object
import json
import requests


"""Site API client"""


class Site(object):
    """Returns all Kentik Sites"""

    def __init__(self, api_email, api_token, base_url='https://api.kentik.com'):
        self.api_email = api_email
        self.api_token = api_token
        self.base_url = base_url

    def list(self, url='https://api.kentik.com/api/v5/sites'):
        headers = {
            'User-Agent': 'kentik-python-api/0.2',
            'Content-Type': 'application/json',
            'X-CH-Auth-Email': self.api_email,
            'X-CH-Auth-API-Token': self.api_token
        }
        resp = requests.get(url, headers=headers)

        # print the HTTP response to help debug
        # print(resp.text)

        # break out at first sign of trouble
        resp.raise_for_status()
        sites = resp.json()

        return sites
