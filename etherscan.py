"""This python file will call etherscan api to get info's of wallets."""

import requests

import utilities as utils

config = utils.read_config()


def get_api_url(module, action, api_key=config.get('etherscan_api_key'), address=None,
                start_block=None, end_block=None, sort=None,
                page=None, offset=None, contract_address=None, tag=None, ):
    url = f'https://api.etherscan.io/api?module={module}&action={action}&apikey={api_key}'

    if address:
        url += f'&address={address}'
    if start_block:
        url += f'&startblock={start_block}'
    if end_block:
        url += f'&endblock={end_block}'
    if sort:
        url += f'&sort={sort}'
    if page:
        url += f'&page={page}'
    if offset:
        url += f'&offset={offset}'
    if contract_address:
        url += f'&contractaddress={contract_address}'
    if tag:
        url += f'&tag={tag}'

    return url


def get_wallet_balance(wallet_address):
    """Get wallet balance.

    :param str wallet_address: Wallet address
    :rtype: dict
    """
    url = get_api_url('account', 'balance', address=wallet_address, tag='latest')
    response = requests.get(url).json()

    if response['status'] == '1' and response['message'] == 'OK':
        balance_in_wei = int(response['result'])
        balance_in_eth = balance_in_wei / 10 ** 18
        balance = round(balance_in_eth, 4)
        results = {'balance_in_wei': balance_in_wei, 'balance_in_eth': balance_in_eth,
                   'balance': balance}
        return results
    else:
        raise Exception(f"An error occurred while getting wallet balance: {response['message']}")
