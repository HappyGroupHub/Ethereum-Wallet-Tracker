"""This is a test file, and it has not been used in the production code.
This file is used to manually send Alchemy Webhook data to the webhook URL.

Before running this file, please MAKE SURE you are running test_app.py in TESTS directory.
Also, make sure you've added the target address in tracking_wallets.json.
"""
import requests

import utilities as utils

webhook_url = utils.read_config()["webhook_url"] + "/alchemy"


# Alchemy Webhook data
# You can find Alchemy Webhook data from the logs directory
# Lists of Alchemy Webhook data dicts
datas = [{dict},
         {dict}, ...]


for data in datas:
    # Send a POST request to the webhook URL
    response = requests.post(webhook_url, json=data)

    # Check the response status
    if response.status_code == 200:
        print("Request sent successfully.")
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")
