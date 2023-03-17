"""This python will handle some extra functions."""
import sys
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

# Time interval (in seconds) at which the program checks for new transactions on the tracked wallet addresses.
# Noted that Etherscan API has a rate limit per second and day!
# The default value is 15 seconds.
check_interval: 15

# The number of transactions to fetch per check.
# A smaller offset value will result in faster API response / process times.
# But may result in missing transactions if many transactions occur within a short time period.
# The default value is 10.
offset: 10
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
                'check_interval': data['check_interval'],
                'offset': data['offset']
            }
            return config
    except (KeyError, TypeError):
        print(
            "An error occurred while reading config.yml, please check if the file is corrected filled.\n"
            "If the problem can't be solved, consider delete config.yml and restart the program.\n")
        sys.exit()
