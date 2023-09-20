from os.path import exists

import alchemy
import utilities as utils

config = utils.read_config()


def check():
    if not exists('./tracking_wallets.json'):
        print("Wallet tracking list not found, creating one by default.")
        eth_id = alchemy.create_address_activity_webhook('ETH_MAINNET')
        eth_goerli_id = alchemy.create_address_activity_webhook('ETH_GOERLI')
        with open('tracking_wallets.json', 'w', encoding="utf8") as file:
            file.write("""{
        "ETH_MAINNET": {
            "webhook_id": "%s"
            },
        "ETH_GOERLI": {
            "webhook_id": "%s"
            }
        }""" % (eth_id, eth_goerli_id))
        file.close()
    if not exists('./notify_token_pairs.json'):
        print("Line user_id to notify_token pairs file not found, creating one by default.")
        with open('notify_token_pairs.json', 'w', encoding="utf8") as file:
            file.write("{}")
        file.close()
    if not exists('./user_tracking_list.json'):
        print("User tracking list not found, creating one by default.")
        with open('user_tracking_list.json', 'w', encoding="utf8") as file:
            file.write("""{
      "ETH_MAINNET": {},
      "ETH_GOERLI": {}
    }""")
        file.close()
