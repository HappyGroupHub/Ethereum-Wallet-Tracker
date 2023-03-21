import requests

import etherscan as eth
import utilities as utils

config = utils.read_config()
wallet_address = config.get('wallet_address')
token = config.get('line_notify_token')


def send_message(message):
    """Send message to LINE Notify.
    :param str message: Message to send.
    """
    headers = {"Authorization": "Bearer " + token}
    data = {'message': '\n' + message}
    requests.post("https://notify-api.line.me/api/notify",
                  headers=headers, data=data, timeout=5)


def notify_new_txns(new_txns):
    for txn in new_txns:
        message = ''
        if txn['type'] == 'normal':
            message = f"""New Transaction Found!
------------------------------------
From: {txn['from']}
To: {txn['to']}
Time: {txn['time']}
Value: {txn['eth_value']} ETH
Action: {txn['action']}
Gas Price: {txn['gwei']} Gwei
------------------------------------
Current Balance: {eth.get_wallet_balance(wallet_address).get('balance')} ETH
{txn['txn_url']}
"""
        elif txn['type'] == 'erc721':
            if 'erc20_token_name' in txn:  # NFT txn with erc20 txn
                message = f"""New NFT Transaction Found!
------------------------------------
From: {txn['from']}
To: {txn['to']}
Time: {txn['time']}
Price: {txn['eth_value']} {txn['erc20_token_symbol']}
{txn['tokenName']} #{txn['tokenID']}
------------------------------------
Current Balance: {eth.get_wallet_balance(wallet_address).get('balance')} ETH
Current token balance: {eth.get_erc20_token_balance(wallet_address, txn['erc20_token_contract'])
                .get('balance')} {txn['erc20_token_symbol']}
{txn['txn_url']}
                """
            else:
                message = f"""New NFT Transaction Found!
------------------------------------
From: {txn['from']}
To: {txn['to']}
Time: {txn['time']}
Price: {txn['eth_value']} ETH
{txn['tokenName']} #{txn['tokenID']}
------------------------------------
Current Balance: {eth.get_wallet_balance(wallet_address).get('balance')} ETH
{txn['txn_url']}
"""

        send_message(message)
        print(message)
