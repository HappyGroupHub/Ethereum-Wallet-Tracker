"""This python file will call etherscan api to get info's of wallets."""
import time

import requests
from requests import JSONDecodeError

import utilities as utils

config = utils.read_config()
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like '
                  'Gecko) Chrome/50.0.2661.102 Safari/537.36'}


def get_api_url(module, action, api_key=config.get('etherscan_api_key'), address=None,
                start_block=None, end_block=None, sort=None, page=None, offset=None,
                contract_address=None, tag=None,
                use_goerli_testnet=config.get('use_goerli_testnet')):
    if use_goerli_testnet:
        url = f'https://api-goerli.etherscan.io/api?module={module}&action={action}&apikey={api_key}'
    else:
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


def get_wallet_balance(wallet_address, tag='latest'):
    """Get wallet balance.

    :param str wallet_address: Wallet address
    :param str tag: Pre-defined block parameter, either earliest, pending or latest, default is latest
    :rtype: dict
    """
    url = get_api_url('account', 'balance', address=wallet_address, tag=tag)
    while True:
        response = {}
        try:
            response = requests.get(url, headers=headers).json()
            break
        except JSONDecodeError:
            time.sleep(1)
            continue

    if response['status'] == '1' and response['message'] == 'OK':
        balance_in_wei = int(response['result'])
        balance_in_eth = balance_in_wei / 10 ** 18
        balance = round(balance_in_eth, 4)
        results = {'balance_in_wei': balance_in_wei, 'balance_in_eth': balance_in_eth,
                   'balance': balance}
        return results
    else:
        raise Exception(f"An error occurred while getting wallet balance: {response}")


def get_erc20_token_balance(wallet_address, contract_address, tag='latest'):
    """Get ERC20 token balance.

    :param str wallet_address: Wallet address
    :param str contract_address: Contract address
    :param str tag: Pre-defined block parameter, either earliest, pending or latest, default is latest
    :rtype: dict
    """
    url = get_api_url('account', 'tokenbalance', address=wallet_address,
                      contract_address=contract_address, tag=tag)
    while True:
        response = {}
        try:
            response = requests.get(url, headers=headers).json()
            break
        except JSONDecodeError:
            time.sleep(1)
            continue

    if response['status'] == '1' and response['message'] == 'OK':
        balance_in_wei = int(response['result'])
        balance_in_eth = balance_in_wei / 10 ** 18
        balance = round(balance_in_eth, 4)
        results = {'balance_in_wei': balance_in_wei, 'balance_in_eth': balance_in_eth,
                   'balance': balance}
        return results
    else:
        raise Exception(f"An error occurred while getting ERC20 token balance: {response}")


def get_normal_transactions(wallet_address, start_block=0, end_block=99999999, page=1, offset=10,
                            sort='desc'):
    """Get normal transactions.

    :param str wallet_address: Wallet address
    :param int start_block: Start block, default is 0
    :param int end_block: End block, default is 99999999
    :param int page: Page, default is 1
    :param int offset: The number of transactions displayed per page, default is 10
    :param str sort: Sorting preference, asc or desc, default is desc
    :rtype: list
    """
    url = get_api_url('account', 'txlist', address=wallet_address, start_block=start_block,
                      end_block=end_block, page=page, offset=offset, sort=sort)
    while True:
        response = {}
        try:
            response = requests.get(url, headers=headers).json()
            break
        except JSONDecodeError:
            time.sleep(1)
            continue
    print(f'Normal Txn: {response}')

    if response['status'] == '1' and response['message'] == 'OK':
        return response['result']
    elif response['message'] == 'No transactions found':
        return None
    else:
        raise Exception(
            f"An error occurred while getting normal transactions: {response}")


def get_internal_transactions(wallet_address, start_block=0, end_block=99999999, page=1, offset=10,
                              sort='desc'):
    """Get internal transactions.

    :param str wallet_address: Wallet address
    :param int start_block: Start block, default is 0
    :param int end_block: End block, default is 99999999
    :param int page: Page, default is 1
    :param int offset: The number of transactions displayed per page, default is 10
    :param str sort: Sorting preference, asc or desc, default is desc
    :rtype: list
    """
    url = get_api_url('account', 'txlistinternal', address=wallet_address, start_block=start_block,
                      end_block=end_block, page=page, offset=offset, sort=sort)
    while True:
        response = {}
        try:
            response = requests.get(url, headers=headers).json()
            break
        except JSONDecodeError:
            time.sleep(1)
            continue
    print(f'Internal Txn: {response}')

    if response['status'] == '1' and response['message'] == 'OK':
        return response['result']
    elif response['message'] == 'No transactions found':
        return None
    else:
        raise Exception(
            f"An error occurred while getting internal transactions: {response}")


def get_erc20_token_transfers(wallet_address, contract_address=None, start_block=0,
                              end_block=99999999, page=1, offset=10, sort='desc'):
    """Get erc20 token transfers.

    :param str wallet_address: Wallet address
    :param str contract_address: Specify token contract address, default is all erc20 tokens
    :param int start_block: Start block, default is 0
    :param int end_block: End block, default is 99999999
    :param int page: Page, default is 1
    :param int offset: The number of transactions displayed per page, default is 10
    :param str sort: Sorting preference, asc or desc, default is desc
    :rtype: list
    """
    url = get_api_url('account', 'tokentx', address=wallet_address,
                      contract_address=contract_address, start_block=start_block,
                      end_block=end_block, page=page, offset=offset, sort=sort)
    while True:
        response = {}
        try:
            response = requests.get(url, headers=headers).json()
            break
        except JSONDecodeError:
            time.sleep(1)
            continue
    # print(f'ERC20 Txn: {response}')

    if response['status'] == '1' and response['message'] == 'OK':
        return response['result']
    elif response['message'] == 'No transactions found':
        return None
    else:
        raise Exception(
            f"An error occurred while getting erc20 token transfers: {response}")


def get_erc721_token_transfers(wallet_address, contract_address=None, start_block=0,
                               end_block=99999999, page=1, offset=10, sort='desc'):
    """Get erc721 token transfers.

    :param str wallet_address: Wallet address
    :param str contract_address: Specify token contract address, default is all erc721 tokens
    :param int start_block: Start block, default is 0
    :param int end_block: End block, default is 99999999
    :param int page: Page, default is 1
    :param int offset: The number of transactions displayed per page, default is 10
    :param str sort: Sorting preference, asc or desc, default is desc
    :rtype: list
    """
    url = get_api_url('account', 'tokennfttx', address=wallet_address,
                      contract_address=contract_address, start_block=start_block,
                      end_block=end_block, page=page, offset=offset, sort=sort)
    while True:
        response = {}
        try:
            response = requests.get(url, headers=headers).json()
            break
        except JSONDecodeError:
            time.sleep(1)
            continue
    print(f'ERC721 Txn: {response}')

    if response['status'] == '1' and response['message'] == 'OK':
        return response['result']
    elif response['message'] == 'No transactions found':
        return None
    else:
        raise Exception(
            f"An error occurred while getting erc721 token transfers: {response}")


def get_erc1155_token_transfers(wallet_address, contract_address=None, start_block=0,
                                end_block=99999999, page=1, offset=10, sort='desc'):
    """Get erc1155 token transfers.

    Does NOT support Goerli testnet.

    :param str wallet_address: Wallet address
    :param str contract_address: Specify token contract address, default is all erc1155 tokens
    :param int start_block: Start block, default is 0
    :param int end_block: End block, default is 99999999
    :param int page: Page, default is 1
    :param int offset: The number of transactions displayed per page, default is 10
    :param str sort: Sorting preference, asc or desc, default is desc
    :rtype: list
    """
    if not config.get('use_goerli_testnet'):
        url = get_api_url('account', 'token1155tx', address=wallet_address,
                          contract_address=contract_address, start_block=start_block,
                          end_block=end_block, page=page, offset=offset, sort=sort)
        while True:
            response = {}
            try:
                response = requests.get(url, headers=headers).json()
                break
            except JSONDecodeError:
                time.sleep(1)
                continue
        # print(f'ERC1155 Txn: {response}')

        if response['status'] == '1' and response['message'] == 'OK':
            return response['result']
        elif response['message'] == 'No transactions found':
            return None
        else:
            raise Exception(
                f"An error occurred while getting erc1155 token transfers: {response}")
    else:
        return None
