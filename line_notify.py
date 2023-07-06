import requests

import utilities as utils

config = utils.read_config()
wallet_address = config.get('wallet_address')
token = config.get('line_notify_token')


def send_message(message):
    """Send message to LINE Notify.
    :param str message: Message to send.
    """
    headers = {"Authorization": "Bearer " + token}
    data = {'message': '\n' + message}
    requests.post("https://notify-api.line.me/api/notify",
                  headers=headers, data=data, timeout=5)
