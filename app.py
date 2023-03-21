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
    for txns_name, txns_type, last_seen_txn in txns_info:
        if txns_type is not None:
            for txn in txns_type:
                txn['type'] = txns_name
                if not txn['hash'] == last_seen_txn:
                    temp_new_txns.append(txn)
                elif not len(temp_new_txns) == 0:
                    if txn['type'] == 'normal':
                        print('Update last seen normal txn')
                        last_seen_normal_txn = temp_new_txns[0]['hash']
                    elif txn['type'] == 'internal':
                        print('Update last seen internal txn')
                        last_seen_internal_txn = temp_new_txns[0]['hash']
                    elif txn['type'] == 'erc20':
                        last_seen_erc20_txn = temp_new_txns[0]['hash']
                    elif txn['type'] == 'erc721':
                        print('Update last seen erc721 txn')
                        last_seen_erc721_txn = temp_new_txns[0]['hash']
                    elif txn['type'] == 'erc1155':
                        last_seen_erc1155_txn = temp_new_txns[0]['hash']
                    new_txns.extend(temp_new_txns)
                    temp_new_txns.clear()
    if not len(new_txns) == 0:
        new_txns = merge_txns(new_txns, normal_txns, internal_txns, erc20_txns, erc721_txns)
        new_txns = sorted(new_txns, key=lambda txn: txn['timeStamp'])
        last_seen_block = int(new_txns[-1]['blockNumber'])
        print(f'New transactions found: {new_txns}')
        new_txns = analysis_txns(new_txns)
        line_notify.notify_new_txns(new_txns)


def merge_txns(new_txns, normal_txns, internal_txns, erc20_txns, erc721_txns):
    if erc721_txns is None:
        return new_txns
    erc721_txns_dict = {txn['hash']: txn for txn in erc721_txns}
    if normal_txns is not None:
        for txn in normal_txns:
            if txn['hash'] in erc721_txns_dict:
                erc721_txns_dict[txn['hash']]['value'] = txn['value']
                new_txns[:] = [d for d in new_txns if
                               not (d.get('hash') == txn['hash'] and d.get('type') == 'normal')]
    if internal_txns is not None:
        for txn in internal_txns:
            if txn['hash'] in erc721_txns_dict:
                erc721_txns_dict[txn['hash']]['value'] = txn['value']
                new_txns[:] = [d for d in new_txns if
                               not (d.get('hash') == txn['hash'] and d.get('type') == 'internal')]
    if erc20_txns is not None:
        for txn in erc20_txns:
            if txn['hash'] in erc721_txns_dict:
                erc721_txns_dict[txn['hash']]['erc20_token_name'] = txn['tokenName']
                erc721_txns_dict[txn['hash']]['erc20_token_symbol'] = txn['tokenSymbol']
                erc721_txns_dict[txn['hash']]['erc20_token_contract'] = txn['contractAddress']
                erc721_txns_dict[txn['hash']]['value'] = txn['value']
                new_txns[:] = [d for d in new_txns if
                               not (d.get('hash') == txn['hash'] and d.get('type') == 'erc20')]
    return new_txns


def analysis_txns(new_txns):
    for txn in new_txns:
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
        txn['time'] = datetime.fromtimestamp(int(txn['timeStamp'])).strftime(
            '%Y-%m-%d %H:%M:%S')
        txn['gwei'] = utils.wei_to_gwei(int(txn['gasPrice']))

        if txn['type'] == 'normal':
            txn['eth_value'] = utils.wei_to_eth(int(txn['value']))
            if txn['methodId'] == '0x':
                txn['action'] = 'Transfer'
            else:
                txn['action'] = txn['functionName'].split('(')[0]
        elif txn['type'] == 'erc721':
            if 'value' not in txn:
                txn['value'] = 0.0
            txn['eth_value'] = utils.wei_to_eth(int(txn['value']))

    return new_txns


if __name__ == '__main__':
    init_last_seen_txns()
    while True:
        track_latest_txns()
        print(f'Last seen normal txn: {last_seen_normal_txn}')
        print(f'Last seen internal txn: {last_seen_internal_txn}')
        print(f'Last seen erc721 txn: {last_seen_erc721_txn}')
        print('------------------------------------')
        time.sleep(check_interval)
