"""This python will handle some extra functions."""
import datetime
import json
import sys
from os.path import exists

import pytz
import yaml
from yaml import SafeLoader


def config_file_generator():
    """Generate the template of config file"""
    with open('config.yml', 'w', encoding="utf8") as file:
        file.write("""# ++--------------------------------++
# | Ethereum Wallet Tracker          |
# | Made by LD                       |
# ++--------------------------------++

# Paste your endpoint for the webhook here.
# You can use ngrok to get a free static endpoint now!
# Find out more here: https://ngrok.com/
webhook_url: 'https://advanced-romantic-seagull.ngrok-free.app'

# Paste your etherscan api key here.
# You can get the api key from here: https://etherscan.io/myapikey
etherscan_api_key: ''

# Alchemy Webhook Auth Token
alchemy_webhook_auth_token: ''

# Line Bot Tokens
line_channel_access_token: ''
line_channel_secret: ''

# Line notify
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
    data = json.load(open(f'{network}_wallets.json', 'r', encoding="utf8"))
    return data


def update_json(file, data):
    """Update a json file.

    :param str file: The file to update.
    :param dict data: The data to update.
    """
    with open(file, 'w', encoding="utf8") as file:
        json.dump(data, file, indent=4)
        file.close()


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


def add_tracking_address_by_user_id(user_id, network, address):
    """Add tracking address by line user id.

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


def get_tracking_addresses_by_user_id(user_id, network):
    """Get tracking addresses by line user id.

    :param str user_id: The line user id of the user.
    :param str network: Network type you would like to search.
    :return list: The list of tracking addresses.
    """
    data = json.load(open('user_tracking_list.json', 'r', encoding="utf8"))
    if user_id not in data[network]:
        return None
    return data[network][user_id]


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


def to_localtime(timestamp_from_alchemy, timezone="Asia/Taipei"):
    dt = datetime.datetime.strptime(timestamp_from_alchemy[:-1], "%Y-%m-%dT%H:%M:%S.%f")
    utc_tz = pytz.timezone("UTC")
    utc_dt = utc_tz.localize(dt)
    local_tz = pytz.timezone(timezone)
    local_dt = utc_dt.astimezone(local_tz)
    local_dt_str = local_dt.strftime("%Y-%m-%d %H:%M:%S")
    return local_dt_str
