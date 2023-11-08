import urllib

import requests

import utilities as utils

config = utils.read_config()
webhook_url = config['webhook_url']
line_notify_id = config['line_notify_id']
line_notify_secret = config['line_notify_secret']


def send_message(message, token):
    """Send message to LINE Notify.

    :param str message: Message to send.
    :param str token: LINE Notify token.
    """
    headers = {"Authorization": "Bearer " + token}
    data = {'message': '\n' + message}
    requests.post("https://notify-api.line.me/api/notify",
                  headers=headers, data=data, timeout=5)


def create_auth_link(user_id):
    """Create LINE Notify auth link for user to connect.

    :param str user_id: The line user_id of the user.
    :return str: The auth link.
    """
    data = {
        'response_type': 'code',
        'client_id': line_notify_id,
        'redirect_uri': webhook_url + '/notify',
        'scope': 'notify',
        'state': user_id,
        'response_mode': 'form_post'
    }
    query_str = urllib.parse.urlencode(data)
    return f'https://notify-bot.line.me/oauth/authorize?{query_str}'


def get_notify_token_by_auth_code(auth_code):
    """Get LINE Notify token by auth code.

    :param str auth_code: The auth code.
    :return str: Line notify token of the user.
    """
    url = 'https://notify-bot.line.me/oauth/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': webhook_url + '/notify',
        'client_id': line_notify_id,
        'client_secret': line_notify_secret
    }
    response = requests.post(url, data=data, headers=headers)
    notify_token = response.json()['access_token']
    return notify_token


def send_notify(txn, txn_type, line_notify_tokens):
    message = ''
    if txn_type == 'normal':
        message = f"New Transaction Found!\n" \
                  f"------------------------------------\n" \
                  f"From: {txn['from']}\n" \
                  f"To: {txn['to']}\n" \
                  f"Time: {txn['time']}\n" \
                  f"Gas Price: {txn['gas_price']} Gwei\n" \
                  f"Value: {txn['eth_value']} ETH\n" \
                  f"Action: {txn['action']}\n" \
                  f"------------------------------------\n" \
                  f"Current Balance: {txn['wallet_balance']} ETH\n" \
                  f"{txn['txn_url']}"
    elif txn_type == 'internal':
        message = f"New Internal Transaction Found!\n" \
                  f"------------------------------------\n" \
                  f"From: {txn['from']}\n" \
                  f"To: {txn['to']}\n" \
                  f"Time: {txn['time']}\n" \
                  f"Value: {txn['eth_value']} ETH\n" \
                  f"------------------------------------\n" \
                  f"Current Balance: {txn['wallet_balance']} ETH\n" \
                  f"{txn['txn_url']}"
    elif txn_type == 'erc20':
        message = f"New ERC20 Transaction Found!\n" \
                  f"------------------------------------\n" \
                  f"From: {txn['from']}\n" \
                  f"To: {txn['to']}\n" \
                  f"Time: {txn['time']}\n" \
                  f"Gas Price: {txn['gas_price']} Gwei\n" \
                  f"ETH Spend: {txn['spend_value']}\n" \
                  f"Token Value: {txn['value']} {txn['token_symbol']}\n" \
                  f"------------------------------------\n" \
                  f"Current Balance: {txn['wallet_balance']} ETH\n" \
                  f"Token Balance: {txn['token_balance']['balance']} {txn['token_symbol']}\n" \
                  f"{txn['txn_url']}"
    elif txn_type == 'erc721':
        message = f"New NFT Transaction Found!\n" \
                  f"------------------------------------\n" \
                  f"From: {txn['from']}\n" \
                  f"To: {txn['to']}\n" \
                  f"Time: {txn['time']}\n" \
                  f"Gas Price: {txn['gas_price']} Gwei\n" \
                  f"ETH Spend: {txn['spend_value']}\n" \
                  f"------------------------------------\n" \
                  f"{txn['token_name']} #{txn['token_id']}\n" \
                  f"Current Balance: {txn['wallet_balance']} ETH\n" \
                  f"{txn['txn_url']}"
    elif txn_type == 'internal_721':
        message = f"New NFT SOLD Transaction Found!\n" \
                  f"------------------------------------\n" \
                  f"From: {txn['from']}\n" \
                  f"To: {txn['to']}\n" \
                  f"Time: {txn['time']}\n" \
                  f"Sell price: {txn['receive_value']}\n" \
                  f"Sold NFT: {txn['token_name']} #{txn['token_id']}" \
                  f"------------------------------------\n" \
                  f"Current Balance: {txn['wallet_balance']} ETH\n" \
                  f"{txn['txn_url']}"
    elif txn_type == 'normal_internal':
        message = f"New Swap Transaction Found!\n" \
                  f"------------------------------------\n" \
                  f"From: {txn['from']}\n" \
                  f"To: {txn['to']}\n" \
                  f"Time: {txn['time']}\n" \
                  f"Gas Price: {txn['gas_price']} Gwei\n" \
                  f"ETH Spend: {txn['eth_value']}\n" \
                  f"ETH Receive: {txn['receive_value']}\n" \
                  f"------------------------------------\n" \
                  f"Current Balance: {txn['wallet_balance']} ETH\n" \
                  f"{txn['txn_url']}"
    elif txn_type == 'normal_internal_20':
        message = f"New Swap Transaction Found!\n" \
                  f"------------------------------------\n" \
                  f"From: {txn['from']}\n" \
                  f"To: {txn['to']}\n" \
                  f"Time: {txn['time']}\n" \
                  f"Gas Price: {txn['gas_price']} Gwei\n" \
                  f"Token Spend: {txn['value']} {txn['token_symbol']}\n" \
                  f"ETH Receive: {txn['receive_value']}\n" \
                  f"------------------------------------\n" \
                  f"Current Balance: {txn['wallet_balance']} ETH\n" \
                  f"Token Balance: {txn['token_balance']['balance']} {txn['token_symbol']}\n" \
                  f"{txn['txn_url']}"
    elif txn_type == 'erc20_721':
        message = f"New NFT Transaction Found!\n" \
                  f"------------------------------------\n" \
                  f"From: {txn['from']}\n" \
                  f"To: {txn['to']}\n" \
                  f"Time: {txn['time']}\n" \
                  f"Gas Price: {txn['gas_price']} Gwei\n" \
                  f"Token Value: {txn['value']} {txn['token_symbol']}\n" \
                  f"{txn['token_name']} #{txn['token_id']}\n" \
                  f"------------------------------------\n" \
                  f"Current Balance: {txn['wallet_balance']} ETH\n" \
                  f"Token Balance: {txn['token_balance']['balance']} {txn['token_symbol']}\n" \
                  f"{txn['txn_url']}"
    elif txn_type == 'normal_20_721':
        message = f"New NFT Transaction Found!\n" \
                  f"------------------------------------\n" \
                  f"From: {txn['from']}\n" \
                  f"To: {txn['to']}\n" \
                  f"Time: {txn['time']}\n" \
                  f"Gas Price: {txn['gas_price']} Gwei\n" \
                  f"ETH Spend: {txn['spend_value']}\n" \
                  f"Action: {txn['action']}\n" \
                  f"------------------------------------\n" \
                  f"Token Value: {txn['value']} {txn['token_symbol']}\n" \
                  f"{txn['token_name']} #{txn['token_id']}\n" \
                  f"------------------------------------\n" \
                  f"Current Balance: {txn['wallet_balance']} ETH\n" \
                  f"Token Balance: {txn['token_balance']['balance']} {txn['token_symbol']}\n" \
                  f"{txn['txn_url']}"
    for token in line_notify_tokens:
        send_message(message, token)
