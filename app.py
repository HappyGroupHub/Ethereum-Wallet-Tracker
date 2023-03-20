"""This is the main file of the project."""
import time
from datetime import datetime

import etherscan as eth
import line_notify
import utilities as utils

config = utils.read_config()
wallet_address = config.get('wallet_address')
check_interval = config.get('check_interval')
last_seen_block = 0
last_seen_normal_txn = str
last_seen_internal_txn = str
last_seen_erc20_txn = str
last_seen_erc721_txn = str
last_seen_erc1155_txn = str


def init_last_seen_txns():
    normal_txn = eth.get_normal_transactions(wallet_address, offset=1)
    internal_txn = eth.get_internal_transactions(wallet_address, offset=1)
    erc20_txn = eth.get_erc20_token_transfers(wallet_address, offset=1)
    erc721_txn = eth.get_erc721_token_transfers(wallet_address, offset=1)
    erc1155_txn = eth.get_erc1155_token_transfers(wallet_address, offset=1)

    global last_seen_block, last_seen_normal_txn, last_seen_internal_txn, \
        last_seen_erc20_txn, last_seen_erc721_txn, last_seen_erc1155_txn
    if normal_txn is not None:
        normal_txn = normal_txn[0]
        last_seen_normal_txn = normal_txn['hash']
        last_seen_block = int(normal_txn['blockNumber'])
    if internal_txn is not None:
        internal_txn = internal_txn[0]
        last_seen_internal_txn = internal_txn['hash']
        if int(internal_txn['blockNumber']) > last_seen_block:
            last_seen_block = int(internal_txn['blockNumber'])
    if erc20_txn is not None:
        erc20_txn = erc20_txn[0]
        last_seen_erc20_txn = erc20_txn['hash']
        if int(erc20_txn['blockNumber']) > last_seen_block:
            last_seen_block = int(erc20_txn['blockNumber'])
    if erc721_txn is not None:
        erc721_txn = erc721_txn[0]
        last_seen_erc721_txn = erc721_txn['hash']
        if int(erc721_txn['blockNumber']) > last_seen_block:
            last_seen_block = int(erc721_txn['blockNumber'])
    if erc1155_txn is not None:
        erc1155_txn = erc1155_txn[0]
        last_seen_erc1155_txn = erc1155_txn['hash']
        if int(erc1155_txn['blockNumber']) > last_seen_block:
            last_seen_block = int(erc1155_txn['blockNumber'])
    time.sleep(check_interval)


def track_latest_txns():
    global last_seen_block, last_seen_normal_txn, last_seen_internal_txn, \
        last_seen_erc20_txn, last_seen_erc721_txn, last_seen_erc1155_txn
    normal_txns = eth.get_normal_transactions(wallet_address, start_block=last_seen_block,
                                              offset=10000)
    internal_txns = eth.get_internal_transactions(wallet_address, start_block=last_seen_block,
                                                  offset=10000)
    erc20_txns = eth.get_erc20_token_transfers(wallet_address, start_block=last_seen_block,
                                               offset=10000)
    erc721_txns = eth.get_erc721_token_transfers(wallet_address, start_block=last_seen_block,
                                                 offset=10000)
    erc1155_txns = eth.get_erc1155_token_transfers(wallet_address, start_block=last_seen_block,
                                                   offset=10000)

    txns_info = [
        ('normal', normal_txns, last_seen_normal_txn),
        ('internal', internal_txns, last_seen_internal_txn),
        ('erc20', erc20_txns, last_seen_erc20_txn),
        ('erc721', erc721_txns, last_seen_erc721_txn),
        ('erc1155', erc1155_txns, last_seen_erc1155_txn)
    ]
    new_txns = []
    temp_new_txns = []
    for txns_name, txns_type, latest_seen_txn in txns_info:
        if txns_type is not None:
            for txn in txns_type:
                if not txn['hash'] == latest_seen_txn:
                    txn['type'] = txns_name
                    temp_new_txns.append(txn)
                elif not len(temp_new_txns) == 0:
                    if txns_name == 'normal':
                        last_seen_normal_txn = temp_new_txns[0]['hash']
                    elif txns_name == 'internal':
                        last_seen_internal_txn = temp_new_txns[0]['hash']
                    elif txns_name == 'erc20':
                        last_seen_erc20_txn = temp_new_txns[0]['hash']
                    elif txns_name == 'erc721':
                        last_seen_erc721_txn = temp_new_txns[0]['hash']
                    elif txns_name == 'erc1155':
                        last_seen_erc1155_txn = temp_new_txns[0]['hash']
                    new_txns.extend(temp_new_txns)
                    temp_new_txns.clear()
    if not len(new_txns) == 0:
        new_txns = sorted(new_txns, key=lambda txn: txn['timeStamp'])
        last_seen_block = int(new_txns[-1]['blockNumber'])
        print(f'New transactions found: {new_txns}')
        new_txns = analysis_txns(new_txns)
        notify_by_line(new_txns)


def analysis_txns(new_txns):
    for txn in new_txns:
        if txn['type'] == 'normal':
            if config.get('use_goerli_testnet'):
                base_url = 'https://goerli.etherscan.io'
            else:
                base_url = 'https://etherscan.io'
            txn['txn_url'] = f'{base_url}/tx/{txn["hash"]}'
            txn['from_url'] = f'{base_url}/address/{txn["from"]}'
            txn['to_url'] = f'{base_url}/address/{txn["to"]}'
            if txn['from'] == wallet_address.lower():
                txn['from'] = 'You'
            if txn['to'] == wallet_address.lower():
                txn['to'] = 'You'
            txn['eth_value'] = utils.wei_to_eth(int(txn['value']))
            txn['gwei'] = utils.wei_to_gwei(int(txn['gasPrice']))
            txn['time'] = datetime.fromtimestamp(int(txn['timeStamp'])).strftime(
                '%Y-%m-%d %H:%M:%S')
            if txn['methodId'] == '0x':
                txn['action'] = 'Transfer'
            else:
                txn['action'] = txn['functionName'].split('(')[0]
    return new_txns


def notify_by_line(new_txns):
    for txn in new_txns:
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
        line_notify.send_message(message)
        print(message)


if __name__ == '__main__':
    init_last_seen_txns()
    while True:
        track_latest_txns()
        print('finished')
        time.sleep(check_interval)
