# Ethereum Wallet Tracker

📖 [繁體中文版README.md](#以太坊錢包交易通知機器人) 📖

## A bot notifies you when new transaction appears

![image](./readme_imgs/banner.png)

This bot is designed to notify you when there is a new transaction on the tracked wallet addresses happened. It supports
both Ethereum mainnet and Goerli testnet in case you are a developer. Notifications can be sent by Line Notify or
Discord bot.

![image](./readme_imgs/line_notify.png)

Project progress:

| TODO LIST           | Support |
|:--------------------|:-------:|
| Line-Notify support |   ☑️    |
| Discord bot support |   🛠️   |
| Normal txns         |   ☑️    |
| Internal txns       |   ☑️    |
| ERC20 token txns    |   🛠️   |
| ERC721 token txns   |   ☑️    |
| ERC1155 token txns  |   ❌️    |

☑️ Supported | 🛠️ In progress | ❌️ Not supported yet

---

## Getting started to use the bot

### How to use

1. Download the latest release from [here](https://github.com/HappyGroupHub/Ethereum-Wallet-Tracker/releases)
2. Unzip the file then open up `config.yml`, [Notepad++](https://notepad-plus-plus.org/downloads/) is recommended
3. Fill in the following required information, see [here](#About-configyml) for more details
4. Now run `WalletTracker.exe` to start the bot
5. Make sure you've invited the bot to your Discord server and added Line Notify as friend
6. Enjoy!

### About config.yml

```yaml
# ++--------------------------------++
# | Ethereum Wallet Tracker          |
# | Made by LD                       |
# ++--------------------------------++

# Paste your etherscan api key here.
# You can get the api key from here: https://etherscan.io/myapikey
etherscan_api_key: ''

# Paste the wallet address you want to track here.
# Simply leave goerli_test_net as false if you want to track Ethereum mainnet wallet.
wallet_address: ''
use_goerli_testnet: false

# Time interval (in seconds) at which the program checks for new transactions on the tracked wallet addresses.
# Noted that Etherscan API has a rate limit per second and day!
# The default value is 60 seconds.
check_interval: 60

# Line Notify Service
# Get notified by Line while there is a new transaction on the tracked wallet addresses.
# You can get the token from here: https://notify-bot.line.me/my/
line_notify_token: ''
```

---

## Contribute to this project

### How to contribute

1. Fork this repository
2. Clone your forked repository
3. Create a new branch
4. Make your changes
5. Commit and push your changes
6. Create a pull request
7. Wait for review

### Libraries used

* [PyYAML](https://github.com/yaml/pyyaml) for reading config file
* [requests](https://github.com/psf/requests) for sending HTTP requests

### Code style and commits

* 100 characters per line
* Use `snake_case` for variables and functions
* Add a blank line at the end of the file
* Optimize imports, remove the redundant ones
* [Google style](https://google.github.io/styleguide/pyguide.html) TODO comments
* Use [Sphinx Docstring](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html) style for docstrings
* Use these headers for commits
  - Update - your commit messages here
  - Fix bug - your commit messages here
  - Optimize - your commit messages here
  - Standardize - your commit messages here

### Find bugs or having suggestions?

If you have any suggestions or found any bugs, please open an
issue [here](https://github.com/HappyGroupHub/Discord-Line-Message-Sync/issues), will try to fix it as soon as possible.

### Support this project

If you find this project useful, consider **starring** this repository to show your support! or donating any
cryptocurrencies to the following addresses

Ethereum address: `hot.happygroup.eth`

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

---

# 以太坊錢包交易通知機器人

📖 [English README.md](#Ethereum-Wallet-Tracker) 📖

## 以太坊錢包交易通知機器人

![image](./readme_imgs/banner.png)

此專案的機器人可以讓你追蹤一個以太坊錢包的交易活動，並在有新的交易發生時，透過Line Notify或Discord bot來通知您! 同時支援開法者使用
Goerli 測試網路。

![image](./readme_imgs/line_notify.png)

專案進度:

| 完成列表              | 進度  |
|:------------------|:---:|
| 支援 Line-Notify 通知 | ☑️  |
| 支援 Discord 機器人通知  | 🛠️ |
| 一般的交易活動           | ☑️  |
| 內部交易活動            | ☑️  |
| ERC20 代幣活動        | 🛠️ |
| ERC721 代幣活動       | ☑️  |
| ERC1155 代幣活動      | ❌️  |

☑️ 已支援 | 🛠️ 開發中... | ❌️ 尚未開發

---

## 開始使用

### 如何下載及運行

1. 從 [這裡](https://github.com/HappyGroupHub/Ethereum-Wallet-Tracker/releases) 下載最新的版本
2. 解壓縮檔案後，於資料夾內開啟 `config.yml`, 建議使用[Notepad++](https://notepad-plus-plus.org/downloads/)來編輯檔案
3. 遵照內文完成填寫 `config.yml`，請參考 [這裡](#關於-configyml)
4. 運行 `WalletTracker.exe`
5. 確認你已邀請Discord bot至你的伺服器及將Line Notify加為好友
6. 盡情使用!

### 關於 config.yml

```yaml
# ++--------------------------------++
# | Ethereum Wallet Tracker          |
# | Made by LD                       |
# ++--------------------------------++

# Paste your etherscan api key here.
# You can get the api key from here: https://etherscan.io/myapikey
etherscan_api_key: ''

# Paste the wallet address you want to track here.
# Simply leave goerli_test_net as false if you want to track Ethereum mainnet wallet.
wallet_address: ''
use_goerli_testnet: false

# Time interval (in seconds) at which the program checks for new transactions on the tracked wallet addresses.
# Noted that Etherscan API has a rate limit per second and day!
# The default value is 60 seconds.
check_interval: 60

# Line Notify Service
# Get notified by Line while there is a new transaction on the tracked wallet addresses.
# You can get the token from here: https://notify-bot.line.me/my/
line_notify_token: ''
```

---

## 協助這個專案開發

### 如何貢獻

1. Fork 這個專案
2. 複製你剛剛 Fork 的專案至本地
3. 建立新的分支
4. 盡情發揮你的能力
5. Commit / Push 你的程式碼
6. 建立新的 Pull Request
7. 等待回覆

### 使用的函式庫

* [PyYAML](https://github.com/yaml/pyyaml) 用來讀取config.yml檔案
* [requests](https://github.com/psf/requests) 用來傳送HTTP請求

### 程式碼撰寫/提交規範

* 每行不超過100個字元
* 使用 `snake_case` 命名變數及函式
* 在檔案尾處加上一個空行
* 最佳化程式碼並移除不必要的import
* [Google style](https://google.github.io/styleguide/pyguide.html) TODO註解
* 使用 [Sphinx Docstring](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html) 進行函式註解
* 提交請求時請使用以下格式，並全英文撰寫
  - Update - your commit messages here
  - Fix bug - your commit messages here
  - Optimize - your commit messages here
  - Standardize - your commit messages here

### 建議/問題回報

如果你有任何建議或是發現了任何問題，請在 [Issues](https://github.com/HappyGroupHub/Ethereum-Wallet-Tracker/issues)
提交你的意見，我會盡快回覆你!

### 支持我做出更多開源內容

如果你覺得這個專案對你有幫助，歡迎按下右上角的 **Star** 來追蹤此專案! 也可以透過加密貨幣捐款來支持我做出更多開源內容

以太坊錢包地址: `hot.happygroup.eth`

### 版權

此專案的版權規範採用 **MIT License** - 至 [LICENSE](LICENSE) 查看更多相關聲明
