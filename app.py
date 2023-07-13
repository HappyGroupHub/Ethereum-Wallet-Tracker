"""This is the main file of the project."""
from flask import Flask, request, Response

import line_notify as line
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
        message = ''
        if json_received['event']['activity'][0]['category'] == 'external':
            message = f"""New Transaction Found on {json_received['event']['network']}!
------------------------------------
From: {json_received['event']['activity'][0]['fromAddress']}
To: {json_received['event']['activity'][0]['toAddress']}
Time: {utils.to_localtime(json_received['createdAt'])}
Value: {json_received['event']['activity'][0]['value']} {json_received['event']['activity'][0]['asset']}
Action: Transfer
Gas Price: Not supported yet
------------------------------------
Current Balance: Not supported yet
https://etherscan.io/tx/{json_received['event']['activity'][0]['hash']}
"""
        line.send_message(message)
        return Response(status=200)
    return Response(status=200)


if __name__ == '__main__':
    app.run()
