"""This is the main file of the project."""
import asyncio
import logging
import os
import time
from threading import Thread

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, \
    MessagingApiBlob, RichMenuRequest, RichMenuSize, RichMenuArea, RichMenuBounds, TextMessage, \
    TemplateMessage, ConfirmTemplate, MessageAction, CarouselTemplate
from linebot.v3.webhooks import MessageEvent, TextMessageContent, FollowEvent

import alchemy as al
import etherscan as eth
import initial_checks
import line_notify
import utilities as utils

os.makedirs('logs', exist_ok=True)
log_filename = time.strftime("./logs/%Y%m%d_%H%M%S.log")
logging.basicConfig(filename=f'{log_filename}', encoding='utf-8', filemode='w',
                    format='[%(levelname)s] - %(asctime)s - %(message)s',
                    datefmt='%d-%b-%Y %H:%M:%S',
                    level=logging.DEBUG, force=True)

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

config = utils.read_config()
configuration = Configuration(access_token=config['line_channel_access_token'])
handler = WebhookHandler(config['line_channel_secret'])

merging_txns = []
eth_mainnet = 'ETH_MAINNET'
eth_goerli = 'ETH_GOERLI'


@app.post("/callback")
async def callback(request: Request):
    """Callback function for line webhook."""

    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = await request.body()

    # handle webhook body
    try:
        handler.handle(body.decode("utf-8"), signature)
    except InvalidSignatureError:
        logging.warning("Invalid signature. Please check your channel access token/channel secret.")
        raise HTTPException(status_code=400, detail="Invalid signature.")

    return 'OK'


@app.post("/notify")
async def notify(request: Request):
    response_form = await request.form()
    auth_code = response_form['code']
    user_id = response_form['state']

    notify_token = line_notify.get_notify_token_by_auth_code(auth_code)
    utils.add_notify_token_by_user_id(user_id, notify_token)
    push_message = f"Successfully connected to Line Notify! " \
                   f"You may now use /add <wallet_address> " \
                   f"to start tracking your Ethereum Wallet.\n" \
                   f"Use /help to see all commands."
    line_notify.send_message(push_message, notify_token)

    show_message = f"Successfully connected to LINE Notify! " \
                   f"You may now close this page."
    return show_message


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        user_id = event.source.user_id
        message_received = event.message.text
        reply_token = event.reply_token
        if message_received == '/wallet_management':
            template_message = TemplateMessage(
                alt_text="Wallet Management",
                template=CarouselTemplate(
                    columns=[
                        {
                            "thumbnail_image_url": "https://cdn.discordapp.com/attachments/930796258258464829/1163457513342124032/1.jpg?ex=653fa53f&is=652d303f&hm=b046b8a0244adf0ca1921eac9e0924907ba46b0754a70ebac39817c815a484b0&",
                            "title": "Add Wallet",
                            "text": "Adding wallet to your tracking list.",
                            "actions": [
                                MessageAction(
                                    label="Add Wallet",
                                    text="/add"
                                )
                            ]
                        },
                        {
                            "thumbnail_image_url": "https://cdn.discordapp.com/attachments/930796258258464829/1163457513048514592/2.jpg?ex=653fa53f&is=652d303f&hm=5b898dfb630a7fd41d1fb822e1df4bd780a0f95f9a1c48bb616632527b76d5c2&",
                            "title": "Remove Wallet",
                            "text": "Removing wallet to your tracking list.",
                            "actions": [
                                MessageAction(
                                    label="Remove Wallet",
                                    text="/remove"
                                )
                            ]
                        },
                        {
                            "thumbnail_image_url": "https://cdn.discordapp.com/attachments/930796258258464829/1164757174828945460/TemplateSendMessage.png?ex=65445fa6&is=6531eaa6&hm=10eb59d0a3acb118eaa3e6fb8e9223e8fdb97b82e1a504dac9aefae09f0e0efa&",
                            "title": "Get Wallet List",
                            "text": "Getting your wallet tracking list.",
                            "actions": [
                                MessageAction(
                                    label="Get Wallet List ",
                                    text="/list"
                                )
                            ]
                        }
                    ]
                )
            )
            line_bot_api.reply_message_with_http_info(ReplyMessageRequest(
                reply_token=reply_token,
                messages=[template_message]
            ))
        if message_received == '/connect':
            if not utils.get_notify_token_by_user_id(user_id):
                auth_link = line_notify.create_auth_link(user_id)
                reply_message = auth_link
            else:
                reply_message = f"You have already connected your Line Notify!"
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[TextMessage(text=reply_message)]
                )
            )
        if message_received.startswith('/add'):
            notify_token = utils.get_notify_token_by_user_id(user_id)
            if notify_token is None:
                reply_message = f"Please connect your Line Notify first!\n" \
                                f"Use /connect to connect it."
            else:
                parts = message_received.split()
                if len(parts) >= 2:
                    command, wallet_address = parts[:2]
                    network = 'ETH_MAINNET'
                    if len(parts) == 3 and parts[2] == 'test':
                        network = 'ETH_GOERLI'
                    wallet_address = wallet_address.lower()
                    tracking_wallets = utils.get_tracking_wallets(network)
                    user_tracked_wallets = utils.get_tracking_addresses_by_user_id(user_id, network)
                    if wallet_address in user_tracked_wallets:
                        reply_message = f"Wallet address has already been added before!\n" \
                                        f"Use /list to see all tracking addresses."
                    else:
                        if wallet_address not in tracking_wallets:
                            al.add_tracking_address(tracking_wallets['webhook_id'], wallet_address)
                        utils.add_tracking_wallet(network, wallet_address, notify_token)
                        utils.add_tracking_address_by_user_id(user_id, network, wallet_address)
                        reply_message = f"Successfully added new tracking address!\n" \
                                        f"Network: {network}\n" \
                                        f"Wallet Address: {wallet_address}"
                        line_notify.send_message(reply_message, notify_token)
                        reply_message = f"Successfully added new tracking address!"
                else:
                    reply_message = f"Invalid input format.\n" \
                                    f"/add <wallet_address>"
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[TextMessage(text=reply_message)]
                )
            )
        if message_received.startswith('/remove'):
            notify_token = utils.get_notify_token_by_user_id(user_id)
            if notify_token is None:
                reply_message = f"Please connect your Line Notify first!\n" \
                                f"Use /connect to connect it."
            else:
                parts = message_received.split()
                if len(parts) >= 2:
                    command, wallet_address = parts[:2]
                    network = 'ETH_MAINNET'
                    if len(parts) == 3 and parts[2] == 'test':
                        network = 'ETH_GOERLI'
                    wallet_address = wallet_address.lower()
                    tracking_wallets = utils.get_tracking_wallets(network)
                    if wallet_address not in tracking_wallets:
                        reply_message = f"Wallet address not found in tracking list!\n" \
                                        f"Use /list to see all tracking addresses."
                    else:
                        if len(tracking_wallets[wallet_address]) == 1:
                            al.remove_tracking_address(tracking_wallets['webhook_id'],
                                                       wallet_address)
                        utils.remove_tracking_wallet(network, wallet_address, notify_token)
                        utils.remove_tracking_address_by_user_id(user_id, network, wallet_address)
                        reply_message = f"Successfully removed one tracking address!\n" \
                                        f"Network: {network}\n" \
                                        f"Wallet Address: {wallet_address}"
                        line_notify.send_message(reply_message, notify_token)
                        reply_message = f"Successfully removed one tracking address!"
                else:
                    reply_message = f"Invalid input format.\n" \
                                    f"/remove <wallet_address>"
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[TextMessage(text=reply_message)]
                )
            )
        if message_received.startswith('/list'):
            parts = message_received.split()
            network = 'ETH_MAINNET'
            if len(parts) == 2:
                network = 'ETH_GOERLI'
            user_tracked_wallets = utils.get_tracking_addresses_by_user_id(user_id, network)
            if not user_tracked_wallets:
                reply_message = f"You have not added any tracking address yet!\n" \
                                f"Use /add <wallet_address> to add one."
            else:
                reply_message = f"Tracking Wallets in {network}:\n"
                for wallet in user_tracked_wallets:
                    reply_message += f"{wallet}\n"
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[TextMessage(text=reply_message)]
                )
            )


@handler.add(FollowEvent)
def handle_follow(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        reply_token = event.reply_token
        auth_link = line_notify.create_auth_link(event.source.user_id)
        reply_message = f"Welcome to the Ethereum Wallet Tracker! " \
                        f"Please connect your Line Notify by the following link first!\n" \
                        f"(1-on-1 chat with Line Notify)\n" \
                        f"\n{auth_link}"
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=reply_message)]
            )
        )


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

        # Analyze the target wallet address
        if json_received['event']['activity'][0]['fromAddress'] in address_list:
            target = str(json_received['event']['activity'][0]['fromAddress'])
        else:
            target = str(json_received['event']['activity'][0]['toAddress'])

        # Determine the transaction type and add to merging_txns list
        if 'asset' in json_received['event']['activity'][0]:
            if json_received['event']['activity'][0]['category'] == 'internal':  # internal txn
                logging.debug('adding internal txn')
                merging_txns.append(
                    {'network': txn_network, 'txn_hash': txn_hash, 'txn_type': 'internal',
                     'target': target, 'block_num': block_num,
                     'line_notify_tokens': tracking_wallets[target]})
            elif json_received['event']['activity'][0]['asset'] == 'ETH':  # normal txn
                logging.debug('adding normal txn')
                merging_txns.append(
                    {'network': txn_network, 'txn_hash': txn_hash, 'txn_type': 'normal',
                     'target': target, 'block_num': block_num,
                     'line_notify_tokens': tracking_wallets[target]})
            else:  # erc20 txn
                logging.debug('adding erc20 txn')
                merging_txns.append(
                    {'network': txn_network, 'txn_hash': txn_hash, 'txn_type': 'erc20',
                     'target': target, 'block_num': block_num,
                     'line_notify_tokens': tracking_wallets[target]})
        elif 'erc721TokenId' in json_received['event']['activity'][0]:  # erc721 txn
            logging.debug('adding erc721 txn')
            merging_txns.append(
                {'network': txn_network, 'txn_hash': txn_hash, 'txn_type': 'erc721',
                 'target': target, 'block_num': block_num,
                 'line_notify_tokens': tracking_wallets[target]})


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
        await asyncio.sleep(5)
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
                logging.info('Sent normal txn notify')
            elif len(txn['txn_type']) == 1 and txn['txn_type'][0] == 'internal':
                line_notify.send_notify(internal_txn, 'internal', txn['line_notify_tokens'])
                logging.info('Sent internal txn notify')
            elif len(txn['txn_type']) == 1 and txn['txn_type'][0] == 'erc20':
                erc20_txn['spend_value'] = 'Transfer'
                line_notify.send_notify(erc20_txn, 'erc20', txn['line_notify_tokens'])
                logging.info('Sent erc20 txn notify')
            elif len(txn['txn_type']) == 1 and txn['txn_type'][0] == 'erc721':
                erc721_txn['spend_value'] = 'Transfer'
                line_notify.send_notify(erc721_txn, 'erc721', txn['line_notify_tokens'])
                logging.info('Sent erc721 txn notify')

            elif len(txn['txn_type']) == 2 and 'normal' in txn['txn_type'] and 'erc20' in txn[
                'txn_type']:
                if normal_txn['value'] == '0':
                    erc20_txn['spend_value'] = 'Transfer'
                else:
                    erc20_txn['spend_value'] = f"{normal_txn['eth_value']} ETH"
                line_notify.send_notify(erc20_txn, 'erc20', txn['line_notify_tokens'])
                logging.info('Sent normal/erc20 txn notify')
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
                logging.info('Sent normal/erc721 txn notify')
            elif len(txn['txn_type']) == 2 and 'erc20' in txn['txn_type'] and 'erc721' in txn[
                'txn_type']:
                new_txn = erc20_txn
                new_txn['token_name'] = erc721_txn['token_name']
                new_txn['token_id'] = erc721_txn['token_id']
                line_notify.send_notify(new_txn, 'erc20_721', txn['line_notify_tokens'])
                logging.info('Sent erc20/erc721 txn notify')
            elif len(txn['txn_type']) == 2 and 'internal' in txn['txn_type'] and 'erc721' in txn[
                'txn_type']:
                erc721_txn['receive_value'] = f"{internal_txn['eth_value']} ETH"
                line_notify.send_notify(erc721_txn, 'internal_721', txn['line_notify_tokens'])
                logging.info('Sent internal/erc721 txn notify')
            elif len(txn['txn_type']) == 2 and 'normal' in txn['txn_type'] and 'internal' in txn[
                'txn_type']:
                erc20_txn['receive_value'] = f"{internal_txn['eth_value']} ETH"
                line_notify.send_notify(erc20_txn, 'normal_internal', txn['line_notify_tokens'])
                logging.info('Sent normal/internal txn notify')

            elif len(txn['txn_type']) == 3 and 'normal' in txn['txn_type'] and 'erc20' in txn[
                'txn_type'] and 'erc721' in txn['txn_type']:
                new_txn = erc721_txn
                new_txn['spend_value'] = f"{normal_txn['value']} ETH"
                new_txn['action'] = normal_txn['action']
                new_txn['value'] = erc20_txn['value']
                new_txn['token_symbol'] = erc20_txn['token_symbol']
                new_txn['token_balance'] = erc20_txn['token_balance']
                line_notify.send_notify(new_txn, 'normal_20_721', txn['line_notify_tokens'])
                logging.info('Sent normal/erc20/erc721 txn notify')
            elif len(txn['txn_type']) == 3 and 'normal' in txn['txn_type'] and 'internal' in txn[
                'txn_type'] and 'erc20' in txn['txn_type']:
                erc20_txn['receive_value'] = f"{internal_txn['eth_value']} ETH"
                line_notify.send_notify(erc20_txn, 'normal_internal_20', txn['line_notify_tokens'])
                logging.info('Sent normal/internal/erc20 txn notify')

            break
        except TypeError:
            continue
        except Exception as e:
            logging.error(f'Error occurred while merging txn: {e}')
            break


def filter_txns():
    """Filter transactions' types then send them to verify_merge_then_send_notify function.

    This function will be run in every 5 seconds.
    By continuously checking the merging_txns list, it combines same hash different types
    transactions into one.

    The merging_txns should be updated while receiving new transactions from Alchemy Webhook.
    And the merging_txns should be a list of dictionary with keys:
    - network: The network of the transaction.
    - block_num: The block number of the transaction.
    - target: The target wallet address of the transaction.
    - txn_hash: The hash of the transaction.
    - txn_type: The type of the transaction.
    - line_notify_tokens(list): The line notify tokens to send.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def _filter_txns():
        while True:
            if merging_txns:
                filtered_txns = []
                data_dict = {}
                for txn in merging_txns:
                    network = txn['network']
                    block_num = txn['block_num']
                    target = txn['target']
                    txn_hash = txn['txn_hash']
                    txn_type = txn['txn_type']
                    txn_line_notify_tokens = txn['line_notify_tokens']
                    if network in data_dict:
                        if txn_hash in data_dict[network]:
                            data_dict[network][txn_hash]['txn_type'].append(txn_type)
                        else:
                            data_dict[network][txn_hash] = {'network': network,
                                                            'block_num': block_num,
                                                            'target': target,
                                                            'txn_type': [txn_type],
                                                            'txn_hash': txn_hash,
                                                            'line_notify_tokens': txn_line_notify_tokens}
                    else:
                        data_dict[network] = {
                            txn_hash: {'network': network, 'block_num': block_num, 'target': target,
                                       'txn_type': [txn_type], 'txn_hash': txn_hash,
                                       'line_notify_tokens': txn_line_notify_tokens}}
                for network, addresses in data_dict.items():
                    for txn_hash, txn_data in addresses.items():
                        filtered_txns.append(txn_data)

                logging.debug(f'Filtered - {filtered_txns}')
                for filtered_txn in filtered_txns:
                    asyncio.create_task(verify_merge_then_send_notify(filtered_txn))
                merging_txns.clear()
                filtered_txns.clear()
            await asyncio.sleep(5)

    try:
        asyncio.run(_filter_txns())
    except KeyboardInterrupt:
        logging.error('KeyboardInterrupt received, exiting.')


def open_rich_menu():
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_blob_api = MessagingApiBlob(api_client)

        rich_menu = RichMenuRequest(
            size=RichMenuSize(width=2500, height=843),
            selected=False,
            name="my-rich-menu",
            chat_bar_text="Tap to open",
            areas=[
                RichMenuArea(
                    bounds=RichMenuBounds(x=0, y=0, width=1250, height=843),
                    action=MessageAction(label="Account Management", text="/account_management")
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=1251, y=0, width=1250, height=843),
                    action=MessageAction(label="Wallet Management", text="/wallet_management")
                ),
            ]
        )

        rich_menu_id = line_bot_api.create_rich_menu(rich_menu_request=rich_menu).rich_menu_id

        # 2. Upload an image to the Rich Menu
        with open('./images/rich_menu.png', 'rb') as image:
            line_bot_blob_api.set_rich_menu_image(
                rich_menu_id=rich_menu_id,
                body=bytearray(image.read()),
                _headers={'Content-Type': 'image/png'}
            )

        # 3. Set the Rich Menu as the default for users
        line_bot_api.set_default_rich_menu(rich_menu_id=rich_menu_id)

        print('Rich Menu created successfully.')


if __name__ == '__main__':
    open_rich_menu()
    initial_checks.check()
    thread = Thread(target=filter_txns)
    thread.start()
    uvicorn.run(app, port=5000)
