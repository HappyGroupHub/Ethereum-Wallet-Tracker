"""This is the main file of the project."""
from flask import Flask, request, Response, abort
from flask.logging import create_logger
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, \
    TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent

import alchemy as al
import etherscan as eth
import initial_checks
import utilities as utils

config = utils.read_config()
configuration = Configuration(access_token=config['line_channel_access_token'])
handler = WebhookHandler(config['line_channel_secret'])

app = Flask(__name__)
log = create_logger(app)


@app.route("/callback", methods=['POST'])
def callback():
    """Callback function for line webhook."""

    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    log.info("Request body: %s", body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        message_received = event.message.text
        reply_token = event.reply_token
        if message_received == 'test':
            reply_message = 'test'
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[TextMessage(text=reply_message)]
                )
            )
        if message_received.startswith('/add'):
            parts = message_received.split()
            if len(parts) >= 4 and parts[0] == "/add":
                command, network, wallet_address, notify_token = parts[:4]
                tracking_wallets = utils.get_tracking_wallets(network)
                al.add_tracking_addresses(tracking_wallets['webhook_id'], [wallet_address])
                tracking_wallets[wallet_address] = notify_token
                utils.update_json(f'{network}_wallets.json', tracking_wallets)
                reply_message = f"Successfully added new tracking address!\n" \
                                f"Network: {network.upper()}\n" \
                                f"Wallet Address: {wallet_address}\n" \
                                f"Line Notify Token: {notify_token}"
            else:
                reply_message = f"Invalid input format.\n" \
                                f"/add <eth/goerli> <wallet_address> <line_notify_token>'"
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[TextMessage(text=reply_message)]
                )
            )


@app.route('/alchemy', methods=['POST'])
def alchemy():
    json_received = request.json
    print(json_received)
    try:
        if json_received['event']['eventDetails'] == '<EVENT_DETAILS>':
            print('You received a test notification!')
            return Response(status=200)
    except KeyError:
        pass
    if json_received['type'] == 'ADDRESS_ACTIVITY':
        if json_received['event']['activity'][0]['category'] == 'external':
            tracking_wallets = utils.get_tracking_wallets()
            if json_received['event']['activity'][0]['fromAddress'] in tracking_wallets:
                target = json_received['event']['activity'][0]['fromAddress']
            else:
                target = json_received['event']['activity'][0]['toAddress']
            txn = dict
            if json_received['event']['network'] == 'ETH_MAINNET':
                txn = eth.get_normal_transactions(target,
                                                  start_block=int(json_received['event'][
                                                                      'activity'][0][
                                                                      'blockNum'], 16))[0]
                txn = eth.format_txn(txn)
            elif json_received['event']['network'] == 'ETH_GOERLI':
                txn = eth.get_normal_transactions(target, goerli=True,
                                                  start_block=int(json_received['event'][
                                                                      'activity'][0][
                                                                      'blockNum'], 16))[0]
                print(txn)
                txn = eth.format_txn(txn, goerli=True)
            print('out')
            print(txn)
            print('out2')
            message = f"""
            New Transaction Found!
            ------------------------------------
            From: {txn['from']}
            To: {txn['to']}
            Time: {txn['time']}
            Value: {txn['eth_value']} ETH
            Action: {txn['action']}
            Gas Price: {txn['gas_price']} Gwei ({txn['gas_fee_usd']}) USD
            ------------------------------------
            Current Balance: {eth.get_wallet_balance(target).get('balance')} ETH
            {txn['txn_url']}
            """
            print(message)
            return Response(status=200)
        return Response(status=200)

    return Response(status=200)


if __name__ == '__main__':
    initial_checks.check()
    app.run()
