"""This is the main file of the project."""

import utilities as utils
import etherscan

config = utils.read_config()
wallet_address = config.get('wallet_address')

print(etherscan.get_wallet_balance(wallet_address))

