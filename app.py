"""This is the main file of the project."""
import time

import etherscan as eth
import utilities as utils

config = utils.read_config()
wallet_address = config.get('wallet_address')
check_interval = config.get('check_interval')
latest_seen_block = 0
latest_seen_normal_txn = str
latest_seen_internal_txn = str
latest_seen_erc20_txn = str
latest_seen_erc721_txn = str
latest_seen_erc1155_txn = str


def init_last_seen_txns():
    normal_txn = eth.get_normal_transactions(wallet_address, offset=1)
    internal_txn = eth.get_internal_transactions(wallet_address, offset=1)
    erc20_txn = eth.get_erc20_token_transfers(wallet_address, offset=1)
    erc721_txn = eth.get_erc721_token_transfers(wallet_address, offset=1)
    erc1155_txn = eth.get_erc1155_token_transfers(wallet_address, offset=1)

    global latest_seen_block, latest_seen_normal_txn, latest_seen_internal_txn, \
        latest_seen_erc20_txn, latest_seen_erc721_txn, latest_seen_erc1155_txn
    if normal_txn is not None:
        normal_txn = normal_txn[0]
        latest_seen_normal_txn = normal_txn['hash']
        latest_seen_block = int(normal_txn['blockNumber'])
    if internal_txn is not None:
        internal_txn = internal_txn[0]
        latest_seen_internal_txn = internal_txn['hash']
        if int(internal_txn['blockNumber']) > latest_seen_block:
            latest_seen_block = int(internal_txn['blockNumber'])
    if erc20_txn is not None:
        erc20_txn = erc20_txn[0]
        latest_seen_erc20_txn = erc20_txn['hash']
        if int(erc20_txn['blockNumber']) > latest_seen_block:
            latest_seen_block = int(erc20_txn['blockNumber'])
    if erc721_txn is not None:
        erc721_txn = erc721_txn[0]
        latest_seen_erc721_txn = erc721_txn['hash']
        if int(erc721_txn['blockNumber']) > latest_seen_block:
            latest_seen_block = int(erc721_txn['blockNumber'])
    if erc1155_txn is not None:
        erc1155_txn = erc1155_txn[0]
        latest_seen_erc1155_txn = erc1155_txn['hash']
        if int(erc1155_txn['blockNumber']) > latest_seen_block:
            latest_seen_block = int(erc1155_txn['blockNumber'])
    time.sleep(check_interval)


def track_latest_txns():
    global latest_seen_block, latest_seen_normal_txn, latest_seen_internal_txn, \
        latest_seen_erc20_txn, latest_seen_erc721_txn, latest_seen_erc1155_txn
    normal_txns = eth.get_normal_transactions(wallet_address, start_block=latest_seen_block,
                                              offset=10000)
    internal_txns = eth.get_internal_transactions(wallet_address, start_block=latest_seen_block,
                                                  offset=10000)
    erc20_txns = eth.get_erc20_token_transfers(wallet_address, start_block=latest_seen_block,
                                               offset=10000)
    erc721_txns = eth.get_erc721_token_transfers(wallet_address, start_block=latest_seen_block,
                                                 offset=10000)
    erc1155_txns = eth.get_erc1155_token_transfers(wallet_address, start_block=latest_seen_block,
                                                   offset=10000)

    txns_info = [
        ('normal', normal_txns, latest_seen_normal_txn),
        ('internal', internal_txns, latest_seen_internal_txn),
        ('erc20', erc20_txns, latest_seen_erc20_txn),
        ('erc721', erc721_txns, latest_seen_erc721_txn),
        ('erc1155', erc1155_txns, latest_seen_erc1155_txn)
    ]
    new_txns = []
    temp_new_txns = []
    for txns_name, txns_type, latest_seen_txn in txns_info:
        if txns_type is not None:
            for txn in txns_type:
                if not txn['hash'] == latest_seen_txn:
                    temp_new_txns.append(txn)
                elif not len(temp_new_txns) == 0:
                    if txns_name == 'normal':
                        latest_seen_normal_txn = temp_new_txns[0]['hash']
                    elif txns_name == 'internal':
                        latest_seen_internal_txn = temp_new_txns[0]['hash']
                    elif txns_name == 'erc20':
                        latest_seen_erc20_txn = temp_new_txns[0]['hash']
                    elif txns_name == 'erc721':
                        latest_seen_erc721_txn = temp_new_txns[0]['hash']
                    elif txns_name == 'erc1155':
                        latest_seen_erc1155_txn = temp_new_txns[0]['hash']
                    new_txns.extend(temp_new_txns)
                    temp_new_txns.clear()
    if not len(new_txns) == 0:
        new_txns = sorted(new_txns, key=lambda txn: txn['timeStamp'])
        latest_seen_block = int(new_txns[-1]['blockNumber'])
        print(f'New transactions found: {new_txns}')


if __name__ == '__main__':
    init_last_seen_txns()
    while True:
        track_latest_txns()
        print('finished')
        time.sleep(check_interval)
