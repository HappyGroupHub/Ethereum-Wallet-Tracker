"""This is the main file of the project."""

import etherscan as eth
import utilities as utils

config = utils.read_config()
wallet_address = config.get('wallet_address')
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
    global latest_seen_block, latest_seen_normal_txn, latest_seen_internal_txn,\
        latest_seen_erc20_txn, latest_seen_erc721_txn, latest_seen_erc1155_txn
    latest_seen_normal_txn = normal_txn['hash']
    latest_seen_internal_txn = internal_txn['hash']
    latest_seen_erc20_txn = erc20_txn['hash']
    latest_seen_erc721_txn = erc721_txn['hash']
    # latest_seen_erc1155_txn = erc1155_txn['hash']
    for txn in [normal_txn, internal_txn, erc20_txn, erc721_txn]:
        if int(txn['blockNumber']) > latest_seen_block:
            latest_seen_block = int(txn['blockNumber'])


if __name__ == '__main__':
    init_latest_seen_txns()
    print(f'Latest seen normal txn hash: {latest_seen_normal_txn}')
    print(f'Latest seen internal txn hash: {latest_seen_internal_txn}')
    print(f'Latest seen erc20 txn hash: {latest_seen_erc20_txn}')
    print(f'Latest seen erc721 txn hash: {latest_seen_erc721_txn}')
    # print(f'Latest seen erc1155 txn hash: {latest_seen_erc1155_txn}')
    print(f'Latest seen block number: {latest_seen_block}')
