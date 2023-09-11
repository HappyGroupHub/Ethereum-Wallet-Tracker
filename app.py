"""This is the main file of the project."""
import asyncio

from flask import Flask, request, Response, abort
from flask.logging import create_logger
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import json
import etherscan as eth
import line_notify
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


@app.route('/alchemy', methods=['POST'])
def alchemy():
    global wallet_balance, line_notify_token
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
            txn = dict
            if json_received['event']['network'] == 'ETH_MAINNET':
                tracking_wallets = utils.get_tracking_wallets('eth')
                address_list = [key.lower() for key in tracking_wallets.keys()]
                if json_received['event']['activity'][0]['fromAddress'] in address_list:
                    target = json_received['event']['activity'][0]['fromAddress']
                else:
                    target = json_received['event']['activity'][0]['toAddress']
                txn = eth.get_normal_transactions(target,
                                                  start_block=int(json_received['event']
                                                                  ['activity'][0]
                                                                  ['blockNum'], 16))[0]
                txn = eth.format_txn(txn)
                wallet_balance = eth.get_wallet_balance(target).get('balance')
                print('mainnet')
                print(txn)
                line_notify_token = tracking_wallets[target]
            elif json_received['event']['network'] == 'ETH_GOERLI':
                tracking_wallets = utils.get_tracking_wallets('goerli')
                address_list = [key.lower() for key in tracking_wallets.keys()]
                if json_received['event']['activity'][0]['fromAddress'] in address_list:
                    target = json_received['event']['activity'][0]['fromAddress']
                else:
                    target = json_received['event']['activity'][0]['toAddress']
                target = str(target)
                txn = eth.get_normal_transactions(target, goerli=True,
                                                  start_block=int(json_received['event']
                                                                  ['activity'][0]
                                                                  ['blockNum'], 16))[0]
                txn = eth.format_txn(txn, goerli=True)
                wallet_balance = eth.get_wallet_balance(target, goerli=True).get('balance')
                print('goerli')
                line_notify_token = tracking_wallets[target]

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
            Current Balance: {wallet_balance} ETH
            {txn['txn_url']}
            """
            line_notify.send_message(message, line_notify_token)
            return Response(status=200)
        return Response(status=200)

    return Response(status=200)



if __name__ == '__main__':
    app.run()
