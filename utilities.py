"""This python will handle some extra functions."""
import json
import sys
import datetime
import pytz
from os.path import exists

import yaml
from yaml import SafeLoader


def config_file_generator():
    """Generate the template of config file"""
    with open('config.yml', 'w', encoding="utf8") as f:
        f.write("""# ++--------------------------------++
# | Ethereum Wallet Tracker          |
# | Made by LD                       |
# ++--------------------------------++

# Paste your etherscan api key here.
# You can get the api key from here: https://etherscan.io/myapikey
etherscan_api_key: ''

# Paste the wallet address you want to track here.
wallet_address: ''

# Line Notify Service
# Get notified by Line while there is a new transaction on the tracked wallet addresses.
# You can get the token from here: https://notify-bot.line.me/my/
line_notify_token: ''


# Alchemy Webhook Auth Token
alchemy_webhook_auth_token: ''
"""
                )
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
        with open('config.yml', 'r', encoding="utf8") as f:
            data = yaml.load(f, Loader=SafeLoader)
            config = {
                'etherscan_api_key': data['etherscan_api_key'],
                'wallet_address': data['wallet_address'],
                'line_notify_token': data['line_notify_token'],
                'alchemy_webhook_auth_token': data['alchemy_webhook_auth_token']
            }
            return config
    except (KeyError, TypeError):
        print(
            "An error occurred while reading config.yml, please check if the file is corrected filled.\n"
            "If the problem can't be solved, consider delete config.yml and restart the program.\n")
        sys.exit()


def get_tracking_wallets():
    data = json.load(open('tracking_wallets.json', 'r', encoding="utf8"))
    return data


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
