import requests
import cloudscraper
import logging
import json
import proxie
import time
from eth_account import Account
from eth_account.messages import encode_defunct
from datetime import datetime, timezone

with open("apis.json", "r") as f:
    keys = json.load(f)
    twocaptcha, proxymarket = keys['twocaptcha'], keys['proxymarket']

proxy = proxie.getProxy(proxymarket)

logging.basicConfig(
    filename="log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    encoding="utf-8"
)

while True:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",
            "Referer": "https://whale.io/",
            "Origin": "https://whale.io/"
        }

        while True:
            try:
                response = requests.post("https://api-ms.crashgame247.io/auth/walletConnect", proxies=proxy[0], headers=headers)
                nonce = response.json()['nonce']
                logging.info(f"Nonce: {nonce}")
                break
            except Exception as e:
                continue

        Account.enable_unaudited_hdwallet_features()
        account, mnemonic = Account.create_with_mnemonic()
        wallet_address = account.address
        private_key = account.key.hex()
        
        logging.info(f"Mnemonic: {mnemonic}")
        logging.info(f"Wallet Address: {wallet_address}")
        logging.info(f"Private Key: {private_key}")

        scraper = cloudscraper.create_scraper()
        scraper.headers.update(headers)

        url = "https://api.2captcha.com/createTask"

        payload = {
            "clientKey": twocaptcha, 
            "task": {
                "type": "HCaptchaTask",
                "websiteURL": "https://whale.io",
                "websiteKey": "a696f716-644c-4034-b4fa-56dc4f64766e",
                "proxyType": "http", 
                "proxyAddress": "pool.proxy.market",
                "proxyPort": f"{proxy[1]['http_port']}",
                "proxyLogin": f"{proxy[1]['login']}",  
                "proxyPassword": f"{proxy[1]['password']}"  
            }
        }
        
        response = requests.post(url=url, json=payload)
        
        if response.json()['errorId'] == 0:
            taskId = response.json()['taskId']
            while True:
                try:
                    url = "https://api.2captcha.com/getTaskResult"
                    payload = {
                        "clientKey": twocaptcha,
                        "taskId": taskId
                    }
                    response = requests.post(url=url, json=payload)
                    captcha_token = response.json()['solution']['token']    
                    logging.info(f"Captcha Token: {captcha_token}")
                    break
                except:
                    time.sleep(3)
                    continue

        auth_url = "https://api-ms.crashgame247.io/auth/walletConnect"

        headers = {
            "Host": "api-ms.crashgame247.io",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Referer": "https://whale.io/",
            "Origin": "https://whale.io"
        }

        message = f"whale.io wants you to sign in with your Ethereum account:\n{wallet_address}\n\nPlease sign with your account\n\nURI: https://whale.io\nVersion: 1\nChain ID: 1\nNonce: {nonce}\nIssued At: {datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"}"
        message_encoded = encode_defunct(text=message)
        signed_message = account.sign_message(message_encoded)
        signature = signed_message.signature.hex()
        logging.info(f"Signature: {signature}")

        auth_payload = {
            "affiliatedByCode": None,
            "captchaToken": captcha_token,
            "message": message,
            "clickId": "",
            "signature": f"{signature}",
            "trafficManagerClickId": ""
        }
        
        try:
            response = scraper.patch(url=auth_url, json=auth_payload, proxies=proxy[0], timeout=60)
            jwt_token = response.json()['token']
            logging.info(f"JWT-Token: {jwt_token}")
        except Exception as e:
            logging.error(f"Ошибка при получении JWT-токена: {str(e)}", exc_info=True)
            continue

        headers.update({
            "Authorization": f"Bearer {jwt_token}",
            "X-Device": "WEB",
            "X-Lang": "en"
        })

        reward_url = "https://api-ms.crashgame247.io/rewards/claimable"
        response = requests.get(reward_url, headers=headers, proxies=proxy[0])
        rewards_data = response.json()
        try: 
            time.sleep(1)
            reawrdId = rewards_data['rewards'][0]['userRewardId']
        except:
            logging.error("Бокс не был получен, запускаем по новой...")
            continue

        logging.info(f"Rewards Data: {rewards_data}")

        claim_url = "https://api-ms.crashgame247.io/rewards/claim"

        claim_payload = {
            "rewardId": reawrdId
        }

        response = requests.post(url=claim_url, headers=headers, json=claim_payload, proxies=proxy[0])
        logging.info(f"Claim: {response.text}")

        open_url = "https://api-ms.crashgame247.io/lootbox/5/open"

        open_params = {
            "amountToOpen": 1,
            "currency": "TON"
        }

        response = requests.get(url=open_url, headers=headers, params=open_params, proxies=proxy[0])
        logging.info(f"Open: {response.text}")

        inventory_url = "https://api-ms.crashgame247.io/lootbox/inventory?page=1&pageSize=16&sort=DESC&sortField=createdAt"

        response = requests.get(url=inventory_url, headers=headers, proxies=proxy[0])
        response.raise_for_status()
        inventory_data = response.json()
        logging.info(f"Inventory: {inventory_data}")

        with open("accounts.txt", "a") as f:
            f.write(f"{inventory_data['data'][0]['item']['name']} - {mnemonic}\n")
    except:
        continue