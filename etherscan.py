"""This python file will call etherscan api to get info's of wallets."""
import time
from datetime import datetime

import requests
from requests import JSONDecodeError

import utilities as utils

config = utils.read_config()
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like '
                  'Gecko) Chrome/50.0.2661.102 Safari/537.36'}


def get_api_url(module, action, api_key=config.get('etherscan_api_key'), goerli=False, address=None,
                start_block=None, end_block=None, sort=None, page=None, offset=None,
                contract_address=None, tag=None):
    if goerli:
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


def get_eth_price(goerli=False):
    """Get ETH price.

    :param bool goerli: If True, use goerli testnet, default is False
    :rtype: float
    """
    url = get_api_url('stats', 'ethprice', goerli=goerli)
    response = get_json_response(url)
    if response['status'] == '1' and response['message'] == 'OK':
        eth_price = float(response['result']['ethusd'])
        return eth_price
    else:
        raise Exception(f"An error occurred while getting ETH price: {response}")


def get_wallet_balance(wallet_address, goerli=False, tag='latest'):
    """Get wallet balance.

    :param str wallet_address: Wallet address
    :param bool goerli: If True, use goerli testnet, default is False
    :param str tag: Pre-defined block parameter, either earliest, pending or latest, default is latest
    :rtype: dict
    """
    url = get_api_url('account', 'balance', goerli=goerli, address=wallet_address, tag=tag)
    response = get_json_response(url)
    if response['status'] == '1' and response['message'] == 'OK':
        balance_in_wei = int(response['result'])
        balance_in_eth = balance_in_wei / 10 ** 18
        balance = round(balance_in_eth, 4)
        results = {'balance_in_wei': balance_in_wei, 'balance_in_eth': balance_in_eth,
                   'balance': balance}
        return results
    else:
        raise Exception(f"An error occurred while getting wallet balance: {response}")


def get_erc20_token_balance(wallet_address, contract_address, goerli=False, tag='latest'):
    """Get ERC20 token balance.

    :param str wallet_address: Wallet address
    :param str contract_address: Contract address
    :param bool goerli: If True, use goerli testnet, default is False
    :param str tag: Pre-defined block parameter, either earliest, pending or latest, default is latest
    :rtype: dict
    """
    url = get_api_url('account', 'tokenbalance', goerli=goerli, address=wallet_address,
                      contract_address=contract_address, tag=tag)
    response = get_json_response(url)
    if response['status'] == '1' and response['message'] == 'OK':
        balance_in_wei = int(response['result'])
        balance_in_eth = balance_in_wei / 10 ** 18
        balance = round(balance_in_eth, 4)
        results = {'balance_in_wei': balance_in_wei, 'balance_in_eth': balance_in_eth,
                   'balance': balance}
        return results
    else:
        raise Exception(f"An error occurred while getting ERC20 token balance: {response}")


def get_normal_transactions(wallet_address, goerli=False, start_block=0, end_block=99999999, page=1,
                            offset=10,
                            sort='desc'):
    """Get normal transactions.

    :param str wallet_address: Wallet address
    :param bool goerli: If True, use goerli testnet, default is False
    :param int start_block: Start block, default is 0
    :param int end_block: End block, default is 99999999
    :param int page: Page, default is 1
    :param int offset: The number of transactions displayed per page, default is 10
    :param str sort: Sorting preference, asc or desc, default is desc
    :rtype: list
    """
    url = get_api_url('account', 'txlist', goerli=goerli, address=wallet_address,
                      start_block=start_block, end_block=end_block, page=page, offset=offset,
                      sort=sort)
    response = get_json_response(url)
    if response['status'] == '1' and response['message'] == 'OK':
        return response['result']
    elif response['message'] == 'No transactions found':
        return None
    else:
        raise Exception(
            f"An error occurred while getting normal transactions: {response}")


def get_internal_transactions(wallet_address, goerli=False, start_block=0, end_block=99999999,
                              page=1, offset=10,
                              sort='desc'):
    """Get internal transactions.

    :param str wallet_address: Wallet address
    :param bool goerli: If True, use goerli testnet, default is False
    :param int start_block: Start block, default is 0
    :param int end_block: End block, default is 99999999
    :param int page: Page, default is 1
    :param int offset: The number of transactions displayed per page, default is 10
    :param str sort: Sorting preference, asc or desc, default is desc
    :rtype: list
    """
    url = get_api_url('account', 'txlistinternal', goerli=goerli, address=wallet_address,
                      start_block=start_block, end_block=end_block, page=page, offset=offset,
                      sort=sort)
    response = get_json_response(url)
    if response['status'] == '1' and response['message'] == 'OK':
        return response['result']
    elif response['message'] == 'No transactions found':
        return None
    else:
        raise Exception(
            f"An error occurred while getting internal transactions: {response}")


def get_erc20_token_transfers(wallet_address, goerli=False, contract_address=None, start_block=0,
                              end_block=99999999, page=1, offset=10, sort='desc'):
    """Get erc20 token transfers.

    :param str wallet_address: Wallet address
    :param bool goerli: If True, use goerli testnet, default is False
    :param str contract_address: Specify token contract address, default is all erc20 tokens
    :param int start_block: Start block, default is 0
    :param int end_block: End block, default is 99999999
    :param int page: Page, default is 1
    :param int offset: The number of transactions displayed per page, default is 10
    :param str sort: Sorting preference, asc or desc, default is desc
    :rtype: list
    """
    url = get_api_url('account', 'tokentx', goerli=goerli, address=wallet_address,
                      contract_address=contract_address, start_block=start_block,
                      end_block=end_block, page=page, offset=offset, sort=sort)
    response = get_json_response(url)
    if response['status'] == '1' and response['message'] == 'OK':
        return response['result']
    elif response['message'] == 'No transactions found':
        return None
    else:
        raise Exception(
            f"An error occurred while getting erc20 token transfers: {response}")


def get_erc721_token_transfers(wallet_address, goerli=False, contract_address=None, start_block=0,
                               end_block=99999999, page=1, offset=10, sort='desc'):
    """Get erc721 token transfers.

    :param str wallet_address: Wallet address
    :param bool goerli: If True, use goerli testnet, default is False
    :param str contract_address: Specify token contract address, default is all erc721 tokens
    :param int start_block: Start block, default is 0
    :param int end_block: End block, default is 99999999
    :param int page: Page, default is 1
    :param int offset: The number of transactions displayed per page, default is 10
    :param str sort: Sorting preference, asc or desc, default is desc
    :rtype: list
    """
    url = get_api_url('account', 'tokennfttx', goerli=goerli, address=wallet_address,
                      contract_address=contract_address, start_block=start_block,
                      end_block=end_block, page=page, offset=offset, sort=sort)
    response = get_json_response(url)
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
        response = get_json_response(url)
        if response['status'] == '1' and response['message'] == 'OK':
            return response['result']
        elif response['message'] == 'No transactions found':
            return None
        else:
            raise Exception(
                f"An error occurred while getting erc1155 token transfers: {response}")
    else:
        return None


def get_json_response(url):
    """Get json response from etherscan

    Using while loop to handle JSONDecodeError, it happens sometimes.

    :param str url: API url to call
    :rtype: dict
    """
    while True:
        try:
            response = requests.get(url, headers=headers).json()
            return response
        except JSONDecodeError:
            time.sleep(1)
            continue


def format_txn(txn, goerli=False):
    """Format transaction

    :param dict txn: Transaction
    :param bool goerli: If True, use goerli testnet, default is False
    :rtype: dict
    """
    if goerli:
        base_url = 'https://goerli.etherscan.io'
    else:
        base_url = 'https://etherscan.io'
    txn['txn_url'] = f'{base_url}/tx/{txn["hash"]}'
    txn['time'] = datetime.fromtimestamp(int(txn['timeStamp'])).strftime('%Y-%m-%d %H:%M:%S')
    txn['gas_price'] = utils.wei_to_gwei(int(txn['gasPrice']))
    txn['gas_used'] = float(txn['gasUsed'])
    txn['gas_fee'] = txn['gas_price'] * txn['gas_used']
    txn['gas_fee_usd'] = txn['gas_fee'] * get_eth_price(goerli=goerli)
    txn['block_number'] = int(txn['blockNumber'])
    txn['block_hash'] = txn['blockHash']
    txn['contract_address'] = txn['contractAddress']
    txn['status'] = txn['txreceipt_status']
    try:
        txn['eth_value'] = utils.wei_to_eth(int(txn['value']))
    except KeyError:
        txn['eth_value'] = 0.0
    if txn['methodId'] == '0x':
        txn['action'] = 'Transfer'
    else:
        txn['action'] = txn['functionName'].split('(')[0]
    return txn