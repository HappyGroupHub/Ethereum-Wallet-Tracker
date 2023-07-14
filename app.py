"""This is the main file of the project."""
from flask import Flask, request, Response

import etherscan
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
        if json_received['event']['network'] == 'ETH_MAINNET' or json_received['event'][
            'network'] == 'ETH_GOERLI':
            if json_received['event']['activity'][0]['category'] == 'external':
                tracking_wallets = utils.get_tracking_wallets()
                if json_received['event']['activity'][0]['fromAddress'] in tracking_wallets:
                    target = json_received['event']['activity'][0]['fromAddress']
                else:
                    target = json_received['event']['activity'][0]['toAddress']
                txn = etherscan.get_normal_transactions(target,
                                                        start_block=int(json_received['event'][
                                                                            'activity'][0][
                                                                            'blockNum'], 16)),
                print('out')
                print(txn)
                return Response(status=200)
    return Response(status=200)


if __name__ == '__main__':
    app.run()
