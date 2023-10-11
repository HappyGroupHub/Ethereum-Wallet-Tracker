"""This is the main file of the project."""
import asyncio
import time

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, \
    TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent, FollowEvent

import alchemy as al
import etherscan as eth
import initial_checks
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

config = utils.read_config()
configuration = Configuration(access_token=config['line_channel_access_token'])
handler = WebhookHandler(config['line_channel_secret'])


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
        print("Invalid signature. Please check your channel access token/channel secret.")
        raise HTTPException(status_code=400, detail="Invalid signature.")

    return 'OK'


@app.post("/notify")
async def notify(request: Request):
    auth_code = request.form.get('code')
    user_id = request.form.get('state')

    notify_token = line_notify.get_notify_token_by_auth_code(auth_code)
    utils.add_notify_token_by_user_id(user_id, notify_token)

    show_message = f"Successfully connected to LINE Notify!\n" \
                   f"You may now close this page."
    return show_message


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        user_id = event.source.user_id
        message_received = event.message.text
        reply_token = event.reply_token
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
        reply_message = f"Welcome to the Ethereum Wallet Tracker!\n" \
                        f"Please connect your Line Notify by the following link first!\n" \
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
    print(json_received)
    try:
        if json_received['event']['eventDetails'] == '<EVENT_DETAILS>':
            print('You received a test notification!')
    except KeyError:
        pass
    if json_received['type'] == 'ADDRESS_ACTIVITY':
        if json_received['event']['activity'][0]['category'] == 'external':
            if json_received['event']['network'] == 'ETH_MAINNET':
                tracking_wallets = utils.get_tracking_wallets('ETH_MAINNET')
                address_list = [key.lower() for key in tracking_wallets.keys()]
                if json_received['event']['activity'][0]['fromAddress'] in address_list:
                    target = json_received['event']['activity'][0]['fromAddress']
                else:
                    target = json_received['event']['activity'][0]['toAddress']
                target = str(target)
                asyncio.create_task(
                    verify_then_send_notify('ETH_MAINNET', target,
                                            json_received['event']['activity'][0]['hash'],
                                            int(json_received['event']['activity'][0]['blockNum'],
                                                16), tracking_wallets[target]))
            elif json_received['event']['network'] == 'ETH_GOERLI':
                tracking_wallets = utils.get_tracking_wallets('ETH_GOERLI')
                address_list = [key.lower() for key in tracking_wallets.keys()]
                if json_received['event']['activity'][0]['fromAddress'] in address_list:
                    target = json_received['event']['activity'][0]['fromAddress']
                else:
                    target = json_received['event']['activity'][0]['toAddress']
                target = str(target)
                asyncio.create_task(
                    verify_then_send_notify('ETH_GOERLI', target,
                                            json_received['event']['activity'][0]['hash'],
                                            int(json_received['event']['activity'][0]['blockNum'],
                                                16), tracking_wallets[target]))


async def verify_then_send_notify(network, target_address, txn_hash, txn_block_num,
                                  line_notify_tokens):
    while True:
        try:
            time.sleep(10)
            if network == 'ETH_MAINNET':
                txns = eth.get_normal_transactions(target_address, start_block=txn_block_num)
                for txn in txns:
                    if txn['hash'] == txn_hash:
                        txn = eth.format_txn(txn)
                        wallet_balance = eth.get_wallet_balance(target_address).get('balance')
                        message = f"New Transaction Found!\n" \
                                  f"------------------------------------\n" \
                                  f"From: {txn['from']}\n" \
                                  f"To: {txn['to']}\n" \
                                  f"Time: {txn['time']}\n" \
                                  f"Value: {txn['eth_value']} ETH\n" \
                                  f"Action: {txn['action']}\n" \
                                  f"Gas Price: {txn['gas_price']} Gwei ({txn['gas_fee_usd']}) USD\n" \
                                  f"------------------------------------\n" \
                                  f"Current Balance: {wallet_balance} ETH\n" \
                                  f"{txn['txn_url']}"
                        for line_notify_token in line_notify_tokens:
                            line_notify.send_message(message, line_notify_token)
                        break
                break
            elif network == 'ETH_GOERLI':
                txns = eth.get_normal_transactions(target_address, goerli=True,
                                                   start_block=txn_block_num)
                for txn in txns:
                    if txn['hash'] == txn_hash:
                        txn = eth.format_txn(txn, goerli=True)
                        wallet_balance = eth.get_wallet_balance(target_address, goerli=True).get(
                            'balance')
                        message = f"New Transaction Found!\n" \
                                  f"------------------------------------\n" \
                                  f"From: {txn['from']}\n" \
                                  f"To: {txn['to']}\n" \
                                  f"Time: {txn['time']}\n" \
                                  f"Value: {txn['eth_value']} ETH\n" \
                                  f"Action: {txn['action']}\n" \
                                  f"Gas Price: {txn['gas_price']} Gwei ({txn['gas_fee_usd']}) USD\n" \
                                  f"------------------------------------\n" \
                                  f"Current Balance: {wallet_balance} ETH\n" \
                                  f"{txn['txn_url']}"
                        for line_notify_token in line_notify_tokens:
                            line_notify.send_message(message, line_notify_token)
                        break
                break
        except Exception:
            print('New transaction not found, wait for 10 seconds and retry...')
            continue


if __name__ == '__main__':
    initial_checks.check()
    uvicorn.run(app, port=5000)
