"""This python will handle some extra functions."""
import json
import sys
from os.path import exists

import yaml
from yaml import SafeLoader

import alchemy


def initial_checks():
    if not exists('./tracking_wallets.json'):
        print("Wallet tracking list not found, creating one by default.")
        eth_id = alchemy.create_address_activity_webhook('ETH_MAINNET')
        eth_goerli_id = alchemy.create_address_activity_webhook('ETH_GOERLI')
        with open('tracking_wallets.json', 'w', encoding="utf8") as file:
            file.write("""{
        "ETH_MAINNET": {
            "webhook_id": "%s"
            },
        "ETH_GOERLI": {
            "webhook_id": "%s"
            }
        }""" % (eth_id, eth_goerli_id))
        file.close()
    if not exists('./notify_token_pairs.json'):
        print("Line user_id to notify_token pairs file not found, creating one by default.")
        with open('notify_token_pairs.json', 'w', encoding="utf8") as file:
            file.write("{}")
        file.close()
    if not exists('./user_tracking_list.json'):
        print("User tracking list not found, creating one by default.")
        with open('user_tracking_list.json', 'w', encoding="utf8") as file:
            file.write("""{
        "ETH_MAINNET": {},
        "ETH_GOERLI": {}
        }""")
        file.close()


def config_file_generator():
    """Generate the template of config file"""
    with open('config.yml', 'w', encoding="utf8") as file:
        file.write("""# ++--------------------------------++
# | Ethereum Wallet Tracker  v0.1.0  |
# | Made by LD & K                   |
# ++--------------------------------++

# Paste your endpoint for the webhook here.
# You can use ngrok to get a free static endpoint now!
# Find out more here: https://ngrok.com/
# Notes: Make sure the webhook url is started with https:// and ended without a slash (/)
webhook_url: ''
# Port for the webhook to listen on. Default is 5000.
# If you change this, make sure to change the port in your reverse proxy as well.
webhook_port: 5000

# Paste your Etherscan api key and Alchemy Webhook Auth Token here.
# Etherscan: https://etherscan.io/myapikey
# Alchemy: https://dashboard.alchemyapi.io/webhooks
etherscan_api_key: ''
alchemy_webhook_auth_token: ''

# Paste yor Line Bot and Line Notify tokens and secrets here.
# Line bot: https://developers.line.biz/console/
# Line Notify: https://notify-bot.line.me/my/services/
line_channel_access_token: ''
line_channel_secret: ''
line_notify_id: ''
line_notify_secret: ''
"""
                   )
        file.close()
    sys.exit()


def read_config():
    """Read config file.

    Check if config file exists, if not, create one.
    if exists, read config file and return config with dict type.

    :rtype: dict
    """
    if not exists('./config.yml'):
        print("Config file not found, create one by default.\nPlease finish filling config.yml")
        with open('config.yml', 'w', encoding="utf8"):
            config_file_generator()

    try:
        with open('config.yml', 'r', encoding="utf8") as file:
            data = yaml.load(file, Loader=SafeLoader)
            config = {
                'webhook_url': data['webhook_url'],
                'webhook_port': data['webhook_port'],
                'etherscan_api_key': data['etherscan_api_key'],
                'alchemy_webhook_auth_token': data['alchemy_webhook_auth_token'],
                'line_channel_access_token': data['line_channel_access_token'],
                'line_channel_secret': data['line_channel_secret'],
                'line_notify_id': data['line_notify_id'],
                'line_notify_secret': data['line_notify_secret']
            }
            file.close()
            return config
    except (KeyError, TypeError):
        print(
            "An error occurred while reading config.yml, please check if the file is corrected filled.\n"
            "If the problem can't be solved, consider delete config.yml and restart the program.\n")
        sys.exit()


def get_tracking_wallets(network):
    """Get tracking wallets from tracking_wallets.json.

    This is the file that saved all the tracking info's from alchemy webhooks.
    Structure of the file should start with a network_type key and the value should be a dict.
    The dict should contain a webhook_id key value pair, then the address key should return a list
    of line_notify_token values.

    :param str network: The network of the target. (ETH_MAINNET or ETH_GOERLI)
    :return dict: Tracking wallets of the network.
    """
    data = json.load(open('tracking_wallets.json', 'r', encoding="utf8"))
    return data[network]


def add_tracking_wallet(network, address, notify_token):
    """Add tracking wallet to tracking_wallets.json.

    This is the file that saved all the tracking info's from alchemy webhooks.
    Structure of the file should start with a network_type key and the value should be a dict.
    The dict should contain a webhook_id key value pair, then the address key should return a list
    of line_notify_token values.

    :param str network: The network of the target. (ETH_MAINNET or ETH_GOERLI)
    :param str address: The address to add.
    :param str notify_token: The notify token of the user.
    """
    data = json.load(open('tracking_wallets.json', 'r', encoding="utf8"))
    if address not in data[network]:
        data[network][address] = [notify_token]
    else:
        data[network][address].append(notify_token)
    update_json('tracking_wallets.json', data)


def remove_tracking_wallet(network, address, notify_token):
    """Remove tracking wallet from tracking_wallets.json.

    This is the file that saved all the tracking info's from alchemy webhooks.
    Structure of the file should start with a network_type key and the value should be a dict.
    The dict should contain a webhook_id key value pair, then the address key should return a list
    of line_notify_token values.

    :param str network: The network of the target. (ETH_MAINNET or ETH_GOERLI)
    :param str address: The address to remove.
    :param str notify_token: The notify token of the user.
    """
    data = json.load(open('tracking_wallets.json', 'r', encoding="utf8"))
    if len(data[network][address]) == 1:
        data[network].pop(address)
    else:
        data[network][address].remove(notify_token)
    update_json('tracking_wallets.json', data)


def add_notify_token_by_user_id(user_id, notify_token):
    """Add notify token by user id.

    :param str user_id: The user id of the user.
    :param str notify_token: The notify token of the user.
    """
    data = json.load(open('notify_token_pairs.json', 'r', encoding="utf8"))
    data[user_id] = notify_token
    update_json('notify_token_pairs.json', data)


def get_notify_token_by_user_id(user_id):
    """Get line notify token by user id.

    :param str user_id: The user id of the user.
    :return str: The notify token of the user.
    """
    data = json.load(open('notify_token_pairs.json', 'r', encoding="utf8"))
    if user_id not in data:
        return None
    return data[user_id]


def get_tracking_addresses_by_user_id(user_id, network):
    """Get tracking addresses by line user id from user_tracking_list.json.

    This is the file that saved all tracking addresses based on a line user id.
    Structure of the file should start with a network_type key and the value should be a dict.
    The dict should contain a line user id as key, and a list of addresses as value.

    :param str user_id: The line user id of the user.
    :param str network: Network type you would like to search.
    :return list: The list of tracking addresses.
    """
    data = json.load(open('user_tracking_list.json', 'r', encoding="utf8"))
    if user_id not in data[network]:
        return []
    return data[network][user_id]


def add_tracking_address_by_user_id(user_id, network, address):
    """Add tracking address by line user id to user_tracking_list.json.

    This is the file that saved all tracking addresses based on a line user id.
    Structure of the file should start with a network_type key and the value should be a dict.
    The dict should contain a line user id as key, and a list of addresses as value.

    :param str user_id: The line user id of the user.
    :param str network: The network of the address.
    :param str address: The address to add.
    """
    data = json.load(open('user_tracking_list.json', 'r', encoding="utf8"))
    if user_id not in data[network]:
        data[network][user_id] = [address]
    else:
        data[network][user_id].append(address)
    update_json('user_tracking_list.json', data)


def remove_tracking_address_by_user_id(user_id, network, address):
    """Remove tracking address by line user id from user_tracking_list.json.

    This is the file that saved all tracking addresses based on a line user id.
    Structure of the file should start with a network_type key and the value should be a dict.
    The dict should contain a line user id as key, and a list of addresses as value.

    :param str user_id: The line user id of the user.
    :param str network: The network of the address.
    :param str address: The address to remove.
    """
    data = json.load(open('user_tracking_list.json', 'r', encoding="utf8"))
    if len(data[network][user_id]) == 1:
        data[network].pop(user_id)
    else:
        data[network][user_id].remove(address)
    update_json('user_tracking_list.json', data)


def update_json(file, data):
    """Update a json file.

    :param str file: The file to update.
    :param dict data: The data to update.
    """
    with open(file, 'w', encoding="utf8") as file:
        json.dump(data, file, indent=4)
        file.close()


def wei_to_eth(wei):
    """Convert wei to eth.

    :param int wei: Amount of wei
    :rtype: float
    """
    return round(wei / 10 ** 18, 4)


def wei_to_gwei(wei):
    """Convert wei to gwei.

    :param int wei: Amount of wei
    :rtype: int
    """
    return int(round(wei / 10 ** 9, 0))
