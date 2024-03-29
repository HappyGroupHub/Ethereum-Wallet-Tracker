import http.client
import logging

import requests

import utilities as utils

config = utils.read_config()
webhook_url = config.get('webhook_url')

alchemy_api_key = config.get('alchemy_api_key')
alchemy_webhook_auth_token = config.get('alchemy_webhook_auth_token')

# Uncomment these lines to see the http request and response headers and body.
# This is useful for debugging, but will become a security risk in production.
# Please don't commit these lines to git, make sure they are commented out.
# http.client.HTTPConnection.debuglevel = 1
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)

requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


def create_address_activity_webhook(network):
    """Create an address activity alchemy webhook.

    :param str network: The network of the webhook.
    :return str webhook_id: The id of the webhook.
    """
    url = "https://dashboard.alchemy.com/api/create-webhook"
    payload = {
        "network": network,
        "webhook_type": "ADDRESS_ACTIVITY",
        "webhook_url": webhook_url + "/alchemy",
        "addresses": ["0x92A5148906D08254Dfc9E4007cEAAE37d8c3DDd9"]
    }
    headers = {
        "accept": "application/json",
        "X-Alchemy-Token": alchemy_webhook_auth_token,
        "content-type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    webhook_id = response.json()['data']['id']
    return webhook_id


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


def add_tracking_address(webhook_id, address):
    """Add tracking address to alchemy webhook.

    :param str webhook_id: The id of alchemy address activity webhook.
    :param str address: The address to add.
    :return:
    """
    url = "https://dashboard.alchemy.com/api/update-webhook-addresses"
    payload = {
        "addresses_to_add": [address],
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


def remove_tracking_address(webhook_id, address):
    """Remove tracking address from alchemy webhook.

    :param str webhook_id: The id of alchemy address activity webhook.
    :param list address: The address to remove.
    :return:
    """
    url = "https://dashboard.alchemy.com/api/update-webhook-addresses"
    payload = {
        "addresses_to_add": [],
        "addresses_to_remove": [address],
        "webhook_id": webhook_id
    }
    headers = {
        "accept": "application/json",
        "X-Alchemy-Token": alchemy_webhook_auth_token,
        "content-type": "application/json"
    }
    response = requests.patch(url, json=payload, headers=headers)
    return response.json()


def get_nft_metadata(contract_address, token_id, token_type='ERC721', goerli=False):
    """Get NFT metadata from alchemy.

    :param str contract_address: The address of the NFT contract.
    :param str token_id: The id of the NFT.
    :param str token_type: The type of the NFT. ERC721 or ERC1155. Default is ERC721.
    :param bool goerli: Whether to use goerli test network.
    :return:
    """
    if not goerli:
        url = "https://eth-mainnet.g.alchemy.com/nft/v2/"
    else:
        url = "https://eth-goerli.g.alchemy.com/nft/v2/"
    url += (f"{alchemy_api_key}/getNFTMetadata?contractAddress={contract_address}&tokenId={token_id}"
            f"&tokenType={token_type}&refreshCache=false")
    headers = {
        "accept": "application/json"
    }
    response = requests.get(url, headers=headers).json()
    response['nft_image_url'] = response['media'][0]['thumbnail']
    return response
