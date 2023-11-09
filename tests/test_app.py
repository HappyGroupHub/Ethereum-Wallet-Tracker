"""This is a test file, and it has not been used in the production code.
By manually sending the Alchemy Webhook data from manual_alchemy.py
We can test the code without a real txn appears.
You can find Alchemy Webhook data from the logs directory.

Before running this file, please fill in your own line notify token at line 40.
"""
import asyncio
import logging
import os
import time

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

import etherscan as eth
import line_notify
import utilities as utils

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

os.makedirs('logs', exist_ok=True)
log_filename = time.strftime("./logs/%Y%m%d_%H%M%S.log")
logging.basicConfig(filename=f'{log_filename}', encoding='utf-8', filemode='w',
                    format='[%(levelname)s] - %(asctime)s - %(message)s',
                    datefmt='%d-%b-%Y %H:%M:%S',
                    level=logging.DEBUG, force=True)

config = utils.read_config()
test_notify_token = ['LSYifU87wZzbcbEX6bSfsEYfNaiaJz99jhNgcJK035H']

eth_mainnet = 'ETH_MAINNET'
eth_goerli = 'ETH_GOERLI'
unfiltered_txns = []
filtering_txns = set()
operation_type = {}


@app.post('/alchemy')
async def alchemy(request: Request):
    json_received = await request.json()
    logging.debug(f'Alchemy - {json_received}')
    try:
        if json_received['event']['eventDetails'] == '<EVENT_DETAILS>':
            logging.debug('You received a test notification!')
    except KeyError:
        pass
    if json_received['type'] == 'ADDRESS_ACTIVITY':
        txn_network = json_received['event']['network']
        txn_hash = json_received['event']['activity'][0]['hash']
        block_num = int(json_received['event']['activity'][0]['blockNum'], 16)
        tracking_wallets = utils.get_tracking_wallets(txn_network)
        address_list = [key.lower() for key in tracking_wallets.keys()]

        # Analyze the target wallet address and line notify tokens
        target = ''
        line_notify_tokens = []
        if json_received['event']['activity'][0]['toAddress'] in address_list:
            target = str(json_received['event']['activity'][0]['toAddress'])
            line_notify_tokens.extend(tracking_wallets[target])
        if json_received['event']['activity'][0]['fromAddress'] in address_list:
            target = str(json_received['event']['activity'][0]['fromAddress'])
            line_notify_tokens.extend(tracking_wallets[target])
        line_notify_tokens = list(set(line_notify_tokens))

        # Determine the transaction type and add to unfiltered_txns list
        if 'asset' in json_received['event']['activity'][0]:
            if json_received['event']['activity'][0]['category'] == 'internal':  # internal txn
                logging.debug('adding internal txn')
                unfiltered_txns.append(
                    {'network': txn_network, 'txn_hash': txn_hash, 'txn_type': 'internal',
                     'target': target, 'block_num': block_num,
                     'line_notify_tokens': test_notify_token})
            elif json_received['event']['activity'][0]['asset'] == 'ETH':  # normal txn
                logging.debug('adding normal txn')
                unfiltered_txns.append(
                    {'network': txn_network, 'txn_hash': txn_hash, 'txn_type': 'normal',
                     'target': target, 'block_num': block_num,
                     'line_notify_tokens': test_notify_token})
            else:  # erc20 txn
                logging.debug('adding erc20 txn')
                unfiltered_txns.append(
                    {'network': txn_network, 'txn_hash': txn_hash, 'txn_type': 'erc20',
                     'target': target, 'block_num': block_num,
                     'line_notify_tokens': test_notify_token})
        elif 'erc721TokenId' in json_received['event']['activity'][0]:  # erc721 txn
            logging.debug('adding erc721 txn')
            unfiltered_txns.append(
                {'network': txn_network, 'txn_hash': txn_hash, 'txn_type': 'erc721',
                 'target': target, 'block_num': block_num,
                 'line_notify_tokens': test_notify_token})
        elif 'erc1155Metadata' in json_received['event']['activity'][0]:  # erc1155 txn
            logging.debug('adding erc1155 txn')
            # TODO(LD): Add support to erc1155 txn
        elif json_received['event']['activity'][0]['category'] == 'token':  # erc20 txn
            logging.debug('adding erc20 txn')
            unfiltered_txns.append(
                {'network': txn_network, 'txn_hash': txn_hash, 'txn_type': 'erc20',
                 'target': target, 'block_num': block_num,
                 'line_notify_tokens': test_notify_token})
            if len(json_received['event']['activity']) >= 2:  # erc20 + erc721 txn
                logging.debug('adding erc721 txn')
                unfiltered_txns.append(
                    {'network': txn_network, 'txn_hash': txn_hash, 'txn_type': 'erc721',
                     'target': target, 'block_num': block_num,
                     'line_notify_tokens': test_notify_token})

        # Call filter_txns function to start filtering same hash transactions
        if txn_hash not in filtering_txns:
            filtering_txns.add(txn_hash)
            asyncio.create_task(filter_txns(txn_hash))


async def verify_merge_then_send_notify(txn: dict):
    """Verify the transaction from etherscan then send notify to users.

    The function will be run in every 5 seconds when get called by filter_txns function.
    While the transaction is found in etherscan, it will be formatted, merged then sent to users.

    The input txn should be a filtered transaction, which should be a dictionary with keys:
    - network: The network of the transaction.
    - block_num: The block number of the transaction.
    - target: The target wallet address of the transaction.
    - txn_hash: The hash of the transaction.
    - txn_type(list): The types of the transaction.
    - line_notify_tokens(list): The line notify tokens to send.

    :param dict txn: The filtered transaction.
    """
    while True:
        try:
            normal_txn = {}
            internal_txn = {}
            erc721_txn = {}
            erc20_txn = {}
            use_goerli = False
            if txn['network'] == eth_goerli:
                use_goerli = True

            # Check if the transaction is found in etherscan
            for txn_type in txn['txn_type']:
                if txn_type == 'normal':
                    normal_txns = eth.get_normal_transactions(txn['target'],
                                                              start_block=txn['block_num'],
                                                              goerli=use_goerli)
                    for normal_txn in normal_txns:
                        if normal_txn['hash'] == txn['txn_hash']:
                            normal_txn = eth.format_txn(normal_txn, txn_type, txn['target'],
                                                        goerli=use_goerli)
                            logging.debug(f'Formatted normal txn - {normal_txn}')
                            break
                if txn_type == 'internal':
                    internal_txns = eth.get_internal_transactions(txn['target'],
                                                                  start_block=txn['block_num'],
                                                                  goerli=use_goerli)
                    for internal_txn in internal_txns:
                        if internal_txn['hash'] == txn['txn_hash']:
                            internal_txn = eth.format_txn(internal_txn, txn_type, txn['target'],
                                                          goerli=use_goerli)
                            logging.debug(f'Formatted internal txn - {internal_txn}')
                            break
                if txn_type == 'erc20':
                    erc20_txns = eth.get_erc20_token_transfers(txn['target'],
                                                               start_block=txn['block_num'],
                                                               goerli=use_goerli)
                    for erc20_txn in erc20_txns:
                        if erc20_txn['hash'] == txn['txn_hash']:
                            erc20_txn = eth.format_txn(erc20_txn, txn_type, txn['target'],
                                                       goerli=use_goerli)
                            logging.debug(f'Formatted erc20 txn - {erc20_txn}')
                            break
                if txn_type == 'erc721':
                    erc721_txns = eth.get_erc721_token_transfers(txn['target'],
                                                                 start_block=txn['block_num'],
                                                                 goerli=use_goerli)
                    for erc721_txn in erc721_txns:
                        if erc721_txn['hash'] == txn['txn_hash']:
                            erc721_txn = eth.format_txn(erc721_txn, txn_type, txn['target'],
                                                        goerli=use_goerli)
                            logging.debug(f'Formatted erc721 txn - {erc721_txn}')
                            break

            # Merge the transactions and send notify
            if len(txn['txn_type']) == 1 and txn['txn_type'][0] == 'normal':
                line_notify.send_notify(normal_txn, 'normal', txn['line_notify_tokens'])
                logging.info(f'Sent normal txn notify - {txn["txn_hash"]}')
            elif len(txn['txn_type']) == 1 and txn['txn_type'][0] == 'internal':
                line_notify.send_notify(internal_txn, 'internal', txn['line_notify_tokens'])
                logging.info(f'Sent internal txn notify - {txn["txn_hash"]}')
            elif len(txn['txn_type']) == 1 and txn['txn_type'][0] == 'erc20':
                erc20_txn['spend_value'] = 'Transfer'
                line_notify.send_notify(erc20_txn, 'erc20', txn['line_notify_tokens'])
                logging.info(f'Sent erc20 txn notify - {txn["txn_hash"]}')
            elif len(txn['txn_type']) == 1 and txn['txn_type'][0] == 'erc721':
                erc721_txn['spend_value'] = 'Transfer'
                line_notify.send_notify(erc721_txn, 'erc721', txn['line_notify_tokens'])
                logging.info(f'Sent erc721 txn notify - {txn["txn_hash"]}')

            elif len(txn['txn_type']) == 2 and 'normal' in txn['txn_type'] and 'erc20' in txn[
                'txn_type']:
                if normal_txn['value'] == '0':
                    erc20_txn['spend_value'] = 'Transfer'
                else:
                    erc20_txn['spend_value'] = f"{normal_txn['eth_value']} ETH"
                line_notify.send_notify(erc20_txn, 'erc20', txn['line_notify_tokens'])
                logging.info(f'Sent normal/erc20 txn notify - {txn["txn_hash"]}')
            elif len(txn['txn_type']) == 2 and 'normal' in txn['txn_type'] and 'erc721' in txn[
                'txn_type']:
                new_txn = normal_txn
                if normal_txn['value'] == '0':
                    new_txn['spend_value'] = 'Transfer'
                else:
                    new_txn['spend_value'] = f"{normal_txn['eth_value']} ETH"
                new_txn['to'] = erc721_txn['to']
                new_txn['token_name'] = erc721_txn['token_name']
                new_txn['token_id'] = erc721_txn['token_id']
                line_notify.send_notify(new_txn, 'erc721', txn['line_notify_tokens'])
                logging.info(f'Sent normal/erc721 txn notify - {txn["txn_hash"]}')
            elif len(txn['txn_type']) == 2 and 'erc20' in txn['txn_type'] and 'erc721' in txn[
                'txn_type']:
                new_txn = erc20_txn
                new_txn['token_name'] = erc721_txn['token_name']
                new_txn['token_id'] = erc721_txn['token_id']
                line_notify.send_notify(new_txn, 'erc20_721', txn['line_notify_tokens'])
                logging.info(f'Sent erc20/erc721 txn notify - {txn["txn_hash"]}')
            elif len(txn['txn_type']) == 2 and 'internal' in txn['txn_type'] and 'erc721' in txn[
                'txn_type']:
                erc721_txn['receive_value'] = f"{internal_txn['eth_value']} ETH"
                line_notify.send_notify(erc721_txn, 'internal_721', txn['line_notify_tokens'])
                logging.info(f'Sent internal/erc721 txn notify - {txn["txn_hash"]}')
            elif len(txn['txn_type']) == 2 and 'normal' in txn['txn_type'] and 'internal' in txn[
                'txn_type']:
                normal_txn['receive_value'] = f"{internal_txn['eth_value']} ETH"
                line_notify.send_notify(normal_txn, 'normal_internal', txn['line_notify_tokens'])
                logging.info(f'Sent normal/internal txn notify - {txn["txn_hash"]}')

            elif len(txn['txn_type']) == 3 and 'normal' in txn['txn_type'] and 'erc20' in txn[
                'txn_type'] and 'erc721' in txn['txn_type']:
                new_txn = erc721_txn
                new_txn['spend_value'] = f"{normal_txn['value']} ETH"
                new_txn['action'] = normal_txn['action']
                new_txn['erc20_value'] = erc20_txn['value']
                new_txn['token_symbol'] = erc20_txn['token_symbol']
                new_txn['token_balance'] = erc20_txn['token_balance']
                line_notify.send_notify(new_txn, 'normal_20_721', txn['line_notify_tokens'])
                logging.info(f'Sent normal/erc20/erc721 txn notify - {txn["txn_hash"]}')
            elif len(txn['txn_type']) == 3 and 'normal' in txn['txn_type'] and 'internal' in txn[
                'txn_type'] and 'erc20' in txn['txn_type']:
                erc20_txn['receive_value'] = f"{internal_txn['eth_value']} ETH"
                line_notify.send_notify(erc20_txn, 'normal_internal_20', txn['line_notify_tokens'])
                logging.info(f'Sent normal/internal/erc20 txn notify - {txn["txn_hash"]}')

            break
        except TypeError:
            # Transaction not found in etherscan, wait 5 seconds and try again
            await asyncio.sleep(5)
            continue
        except Exception as e:
            logging.error(f'Error occurred while merging txn: {e}')
            break


async def filter_txns(txn_hash: str):
    """Filter transactions' types then send them to verify_merge_then_send_notify function.

    This function will be called only one time per transaction hash.
    By waiting 2 seconds, the function will be expected to receive are all types of transactions from
    Alchemy Webhook, then it will filter the transactions' types and send them to
    verify_merge_then_send_notify function.

    The unfiltered_txns should be updated while receiving new transactions from Alchemy Webhook.
    And the unfiltered_txns should be a list of dictionary with keys:
    - network: The network of the transaction.
    - block_num: The block number of the transaction.
    - target: The target wallet address of the transaction.
    - txn_hash: The hash of the transaction.
    - txn_type: The type of the transaction.
    - line_notify_tokens(list): The line notify tokens to send.

    :param str txn_hash: The hash of the transaction.
    """
    # Waiting Alchemy Webhook to send all types of transactions
    await asyncio.sleep(2)

    # Filter the transactions' types, combine them into one
    global unfiltered_txns
    filtered_txn = {}
    for txn in unfiltered_txns:
        if txn['txn_hash'] == txn_hash:
            if not filtered_txn:
                filtered_txn = {
                    'txn_hash': txn['txn_hash'],
                    'network': txn['network'],
                    'block_num': txn['block_num'],
                    'target': txn['target'],
                    'txn_type': [txn['txn_type']],
                    'line_notify_tokens': txn['line_notify_tokens']
                }
            else:
                filtered_txn['txn_type'].append(txn['txn_type'])

    # Finish filtering, call verify_merge_then_send_notify function
    logging.debug(f'Filtered - {filtered_txn}')
    asyncio.create_task(verify_merge_then_send_notify(filtered_txn))
    unfiltered_txns = [d for d in unfiltered_txns if d.get('txn_hash') != txn_hash]
    filtering_txns.remove(txn_hash)


if __name__ == '__main__':
    utils.initial_checks()
    uvicorn.run(app, port=config['webhook_port'])
