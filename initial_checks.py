from os.path import exists

import alchemy
import utilities as utils

if not exists('./eth_wallets.json'):
    print("Ethereum wallet tracking list not found, creating one by default.")
    with open('eth_wallets.json', 'w', encoding="utf8") as f:
        f.write("""{
  "webhook_id": ""
}""")
if not exists('./goerli_wallets.json'):
    print("Ethereum wallet tracking list not found, creating one by default.")
    with open('goerli_wallets.json', 'w', encoding="utf8") as f:
        f.write("""{
  "webhook_id": ""
}""")


eth_wallets = utils.get_tracking_wallets('eth')
goerli_wallets = utils.get_tracking_wallets('goerli')

if eth_wallets['webhook_id'] == '':
    alchemy.create_address_activity_webhook()
