"""This is the main file of the project."""
import time

import etherscan as eth
import utilities as utils

config = utils.read_config()
wallet_address = config.get('wallet_address')
check_interval = config.get('check_interval')
offset = config.get('offset')
latest_seen_block = 0
latest_seen_normal_txn = str
latest_seen_internal_txn = str
latest_seen_erc20_txn = str
latest_seen_erc721_txn = str
latest_seen_erc1155_txn = str


def init_latest_seen_txns():
    normal_txn = eth.get_normal_transactions(wallet_address, offset=1)[0]
    internal_txn = eth.get_internal_transactions(wallet_address, offset=1)[0]
    erc20_txn = eth.get_erc20_token_transfers(wallet_address, offset=1)[0]
    erc721_txn = eth.get_erc721_token_transfers(wallet_address, offset=1)[0]
    # erc1155_txn = eth.get_erc1155_token_transfers(wallet_address, offset=1)[0]
    global latest_seen_block, latest_seen_normal_txn, latest_seen_internal_txn, \
        latest_seen_erc20_txn, latest_seen_erc721_txn, latest_seen_erc1155_txn
    latest_seen_normal_txn = normal_txn['hash']
    latest_seen_internal_txn = internal_txn['hash']
    latest_seen_erc20_txn = erc20_txn['hash']
    latest_seen_erc721_txn = erc721_txn['hash']
    # latest_seen_erc1155_txn = erc1155_txn['hash']
    for txn in [normal_txn, internal_txn, erc20_txn, erc721_txn]:
        if int(txn['blockNumber']) > latest_seen_block:
            latest_seen_block = int(txn['blockNumber'])
    time.sleep(check_interval)


def track_latest_txns():
    global latest_seen_block, latest_seen_normal_txn, latest_seen_internal_txn, \
        latest_seen_erc20_txn, latest_seen_erc721_txn, latest_seen_erc1155_txn
    normal_txns = eth.get_normal_transactions(wallet_address, start_block=latest_seen_block,
                                              offset=offset)
    internal_txns = eth.get_internal_transactions(wallet_address, start_block=latest_seen_block,
                                                  offset=offset)
    erc20_txns = eth.get_erc20_token_transfers(wallet_address, start_block=latest_seen_block,
                                               offset=offset)
    erc721_txns = eth.get_erc721_token_transfers(wallet_address, start_block=latest_seen_block,
                                                 offset=offset)
    # erc1155_txns = eth.get_erc1155_token_transfers(wallet_address, start_block=latest_seen_block,
    #                                                offset=offset)

    txns_info = [
        ("normal", normal_txns, latest_seen_normal_txn),
        ("internal", internal_txns, latest_seen_internal_txn),
        ("erc20", erc20_txns, latest_seen_erc20_txn),
        ("erc721", erc721_txns, latest_seen_erc721_txn)
        # ("erc1155", erc1155_txns, latest_seen_erc1155_txn)
    ]
    new_txns = []
    for txns_name, txns_type, latest_seen_txn in txns_info:
        for txn in txns_type:
            if not txn['hash'] == latest_seen_txn:
                new_txns.append(txn)
            else:
                break
    new_txns = sorted(new_txns, key=lambda txn: txn['timeStamp'])
    latest_seen_block = int(new_txns[-1]['blockNumber'])


if __name__ == '__main__':
    init_latest_seen_txns()
    track_latest_txns()
