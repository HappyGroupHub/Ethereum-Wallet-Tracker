import http.client
import logging

import requests

import utilities as utils

config = utils.read_config()

alchemy_webhook_auth_token = config.get('alchemy_webhook_auth_token')

http.client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


def get_all_tracking_addresses(webhook_id):
    """Get all tracking addresses from alchemy webhook.

    :param str webhook_id: The id of alchemy address activity webhook.
    :rtype:
    """
    url = f"https://dashboard.alchemy.com/api/webhook-addresses?webhook_id={webhook_id}&limit=100&after=5"
    headers = {
        "accept": "application/json",
        "X-Alchemy-Token": alchemy_webhook_auth_token
    }
    response = requests.get(url, headers=headers)
    return response.json()


def add_tracking_addresses(webhook_id, addresses):
    """Add tracking address to alchemy webhook.

    :param str webhook_id: The id of alchemy address activity webhook.
    :param list addresses: The addresses to add.
    :return:
    """
    url = "https://dashboard.alchemy.com/api/update-webhook-addresses"
    payload = {
        "addresses_to_add": addresses,
        "addresses_to_remove": [],
        "webhook_id": webhook_id
    }
    headers = {
        "accept": "application/json",
        "X-Alchemy-Token": alchemy_webhook_auth_token,
        "content-type": "application/json"
    }
    response = requests.patch(url, json=payload, headers=headers)
    return response.json()


def remove_tracking_addresses(webhook_id, addresses):
    """Remove tracking address from alchemy webhook.

    :param str webhook_id: The id of alchemy address activity webhook.
    :param list addresses: The addresses to remove.
    :return:
    """
    url = "https://dashboard.alchemy.com/api/update-webhook-addresses"
    payload = {
        "addresses_to_add": [],
        "addresses_to_remove": addresses,
        "webhook_id": webhook_id
    }
    headers = {
        "accept": "application/json",
        "X-Alchemy-Token": alchemy_webhook_auth_token,
        "content-type": "application/json"
    }
    response = requests.patch(url, json=payload, headers=headers)
    return response.json()
