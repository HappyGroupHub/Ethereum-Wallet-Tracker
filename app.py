"""This is the main file of the project."""
from flask import Flask, request, Response

import etherscan as eth
import utilities as utils

config = utils.read_config()

app = Flask(__name__)


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
    app.run()
