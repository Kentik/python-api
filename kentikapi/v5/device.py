#!/usr/bin/env python

from __future__ import print_function
from builtins import str
from builtins import object
import json
import requests


"""Device API client"""


class Device(object):
    """Creates Kentik Device"""

    def __init__(self, api_email, api_token, base_url='https://api.kentik.com'):
        self.api_email = api_email
        self.api_token = api_token
        self.base_url = base_url

    def create(self, host, host_ip, site_id, plan_id, community="public", url='https://api.kentik.com/api/v5/device'):
        headers = {
            'User-Agent': 'kentik-python-api/0.2',
            'Content-Type': 'application/json',
            'X-CH-Auth-Email': self.api_email,
            'X-CH-Auth-API-Token': self.api_token
        }
        data = {
            'device': {
                "device_name": host.replace('.', '_'),
                "device_type": "router",
                "device_description": host,
                "sending_ips": [
                    host_ip
                ],
                "device_sample_rate": 4096,
                "plan_id": plan_id,
                "site_id": site_id,
                "minimize_snmp": False,
                "device_snmp_ip": host_ip,
                "device_snmp_community": community,
                "device_bgp_type": "none"
            }
        }
        resp = requests.post(url, headers=headers, json=data)

        # break out at first sign of trouble
        resp.raise_for_status()
        device = resp.json()

        return device
