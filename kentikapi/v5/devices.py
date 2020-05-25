#!/usr/bin/env python

from __future__ import print_function
from builtins import str
from builtins import object
import json

import requests


"""Site API client"""
_allowedCustomDimensionChars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_')

class Client(object):
    """Tagging client submits HyperScale batches to Kentik"""

    def __init__(self, api_email, api_token, base_url='https://api.kentik.com'):
        self.api_email = api_email
        self.api_token = api_token
        self.base_url = base_url

    def _submit_batch(self, url, batch):
        """Submit the batch, returning the JSON->dict from the last HTTP response"""
        # TODO: validate column_name
        batch_parts = batch.parts()

        guid = ""
        headers = {
            'User-Agent': 'kentik-python-api/0.2',
            'Content-Type': 'application/json',
            'X-CH-Auth-Email': self.api_email,
            'X-CH-Auth-API-Token': self.api_token
        }

        # submit each part
        last_part = dict()
        for batch_part in batch_parts:
            # submit
            resp = requests.post(url, headers=headers, data=batch_part.build_json(guid))

            # print the HTTP response to help debug
            print(resp.text)

            # break out at first sign of trouble
            resp.raise_for_status()
            last_part = resp.json()
            guid = last_part['guid']
            if guid is None or len(guid) == 0:
                raise RuntimeError('guid not found in batch response')

        return last_part

    def submit_populator_batch(self, column_name, batch):
        """Submit a populator batch

        Submit a populator batch as a series of HTTP requests in small chunks,
        returning the batch GUID, or raising exception on error."""
        if not set(column_name).issubset(_allowedCustomDimensionChars):
            raise ValueError('Invalid custom dimension name "%s": must only contain letters, digits, and underscores' % column_name)
        if len(column_name) < 3 or len(column_name) > 20:
            raise ValueError('Invalid value "%s": must be between 3-20 characters' % column_name)

        url = '%s/api/v5/batch/customdimensions/%s/populators' % (self.base_url, column_name)
        resp_json_dict = self._submit_batch(url, batch)
        if resp_json_dict.get('error') is not None:
            raise RuntimeError('Error received from server: %s' % resp_json_dict['error'])

        return resp_json_dict['guid']

    def submit_tag_batch(self, batch):
        """Submit a tag batch"""
        url = '%s/api/v5/batch/tags' % self.base_url
        self._submit_batch(url, batch)

    def fetch_batch_status(self, guid):
        """Fetch the status of a batch, given the guid"""
        url = '%s/api/v5/batch/%s/status' % (self.base_url, guid)
        headers = {
            'User-Agent': 'kentik-python-api/0.1',
            'Content-Type': 'application/json',
            'X-CH-Auth-Email': self.api_email,
            'X-CH-Auth-API-Token': self.api_token
        }

        resp = requests.get(url, headers=headers)

        # break out at first sign of trouble
        resp.raise_for_status()
        return BatchResponse(guid, resp.json())


class BatchResponse(object):
    """Manages the response JSON from batch status check"""

    def __init__(self, guid, status_dict):
        self.guid = guid
        self.status_dict = status_dict

    def is_finished(self):
        """Returns whether the batch has finished processing"""
        return not self.status_dict["is_pending"]

    def invalid_upsert_count(self):
        """Returns how many invalid upserts were found in the batch"""
        return int(self.status_dict['upserts']['invalid'])

    def invalid_delete_count(self):
        """Returns how many invalid deletes were found in the batch"""
        return int(self.status_dict['deletes']['invalid'])

    def full_response(self):
        """Return the full status JSON as a dictionary"""
        return self.status_dict

    def pretty_response(self):
        """Pretty print the full status response"""
        return json.dumps(self.status_dict, indent=4)
