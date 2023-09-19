from os.path import exists

import alchemy
import utilities as utils

config = utils.read_config()


def check():
    if not exists('./eth_wallets.json'):
        print("Ethereum wallet tracking list not found, creating one by default.")
        with open('eth_wallets.json', 'w', encoding="utf8") as file:
            file.write("""{
      "webhook_id": ""
    }""")
        file.close()
        results = alchemy.create_address_activity_webhook('ETH_MAINNET',
                                                          config['webhook_url'] + '/alchemy')
        webhook_id = results['data']['id']
        new_dict = {'webhook_id': webhook_id}
        utils.update_json('eth_wallets.json', new_dict)
    if not exists('./goerli_wallets.json'):
        print("Goerli wallet tracking list not found, creating one by default.")
        with open('goerli_wallets.json', 'w', encoding="utf8") as file:
            file.write("""{
      "webhook_id": ""
    }""")
        file.close()
        results = alchemy.create_address_activity_webhook('ETH_GOERLI',
                                                          config['webhook_url'] + '/alchemy')
        webhook_id = results['data']['id']
        new_dict = {'webhook_id': webhook_id}
        utils.update_json('goerli_wallets.json', new_dict)
    if not exists('./notify_token_pairs.json'):
        print("Line user_id to notify_token pairs file not found, creating one by default.")
        with open('notify_token_pairs.json', 'w', encoding="utf8") as file:
            file.write("{}")
        file.close()
    if not exists('./user_tracking_list.json'):
        print("User tracking list not found, creating one by default.")
        with open('user_tracking_list.json', 'w', encoding="utf8") as file:
            file.write("""{
      "eth": {},
      "goerli": {}
    }""")
        file.close()
