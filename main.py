import requests
from traceback import format_exc
from time import sleep, time
from web3_account import Web3Account, Web3
from datetime import datetime
from eth_account.messages import encode_defunct
from random import choice
from os import path, getcwd
from Modules.Decrypt import decrypt_files

URL = "https://api.tokensoft.io/auth/api/v1/"
headers = {
    'authority': 'api.tokensoft.io',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,uk;q=0.6,pl;q=0.5,cy;q=0.4,fr;q=0.3',
    'content-type': 'application/json',
    'origin': 'https://airdrop.connext.network',
    'referer': 'https://airdrop.connext.network/',
    'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
}

def make_request(session: requests.Session, method: str, url: str, custom_response: bool = True, **kwargs) -> dict or requests.Response:
    response = session.request(
        method=method.upper(),
        url=url,
        **kwargs
    )
    if custom_response:
        return response.json()
    else:
        return response

def retry(
        infinity: bool = False, max_retries: int = 5,
        timing: float = 5,
        custom_message: str = "Requests error:",
        catch_exception: bool = False,
        info_message: bool = False
):
    if infinity: max_retries = 9**1000
    def retry_decorator(func):
        def _wrapper(*args, **kwargs):
            for _ in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as error:
                    self = args[0]
                    if catch_exception:
                        print(format_exc())
                    
                    if info_message:
                        self.account.logger.info(f'{custom_message} {error}')
                    else: self.account.logger.error(f'{custom_message} {error}')
                    sleep(timing)

        return _wrapper
    return retry_decorator


class Connext:
    def __init__(self, account: Web3Account, proxies: dict = {}) -> None:
        self.account = account
        self.token = None
        self.session = requests.Session()

        self.session.proxies.update(proxies)


    @retry(timing=10, custom_message="Cant get nonce from connext")
    def get_nonce(self) -> str:
        kwargs = {
            "json": {
                "walletAddress": Web3.to_checksum_address(self.account.address)
            },
            "headers": headers
        }
        response = make_request(
            self.session, 'post', URL + "wallets/nonce", **kwargs
        )

        nonce = response.get("nonce")
        if nonce: 
            self.account.logger.success(f'Got nonce for account: {self.account.address}')
            return nonce
        else:
            raise Exception(
                "Bad response"
            )
    
    def get_signature(self, nonce: str):
        timing = datetime.utcfromtimestamp(int(time())).strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-4] + "Z" # Z - ZkSync 
        with open("message.txt", encoding="utf-8") as file:
            message = file.read().replace("ADDRESS", Web3.to_checksum_address(self.account.address))
        
        message = message.replace("NONCE_1", nonce).replace("TIMING", timing)
        encoded_message = encode_defunct(text=message)
        signed_message =  self.account.eth_account.sign_message(encoded_message)

        return Web3.to_hex(signed_message.signature), timing

    @retry(timing=15, custom_message="Failed to make login")
    def push_login(self) -> None:
        nonce = self.get_nonce()
        signature, timing = self.get_signature(nonce)

        kwargs = {
            "json": {
                'walletAddress': Web3.to_checksum_address(self.account.address),
                'signature': signature,
                'message': {
                    'domain': 'airdrop.connext.network',
                    'address': Web3.to_checksum_address(self.account.address),
                    'statement': 'This site is powered by Tokensoft. Sign this message to prove ownership of this wallet and accept our Terms of Service, Privacy Policy, and Cookie Policy: https://tokensoft.io/legal',
                    'uri': 'https://airdrop.connext.network',
                    'version': '1',
                    'chainId': 1,
                    'nonce': nonce,
                    'issuedAt': timing,
                },
                'nonce': nonce,
            },
            "headers": headers
        }

        response = make_request(
            self.session, "post", URL + "wallets/connect", **kwargs
        )

        if response["token"]:

            self.token = response["token"]
            self.account.logger.success(f'Made login to connext')
        else: raise Exception(
                "Bad response from login req"
        )
    
    @retry(timing=10, custom_message="Failed to fetch account eligibility")
    def check_eligible(self) -> list:
        result = []
        if self.token:
            headers = {
                "authorization": "Bearer " + self.token,
                "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            }
            response = make_request(
                self.session, "get", "https://api.tokensoft.io/payment/api/v1/events/52/eligibility", headers=headers
            )
            
            if "eligibility" in response:
                for item in response["eligibility"]:
                    if item.get("value"):
                        result.append(
                            item.get("message")
                        )
                
                if len(result) == 0:
                    return ["NOT ELIGIBLE"]
                return result

            else: raise Exception(
                    "Bad response"
            )

        else:
            self.account.logger.info(f'You must to do login, wait...')
            self.push_login()
            return self.check_eligible()


if __name__ == "__main__":
    if path.exists("results.txt") is False:
        open("results.txt", "w")

    SECRETS_TYPE = "AUTOSOFT" # encrypting 
    DECRYPT_TYPE = "Flash"
    DISK = "E:"

    proxies = [
        {}, {}, {} # optinal
    ]

    with open("secrets.txt", encoding="utf-8") as file:
        secrets_data = [key.replace("\n", "").replace(" ", "") for key in file.readlines()]

    if SECRETS_TYPE == "AUTOSOFT":
        data = decrypt_files(DECRYPT_TYPE, DISK, getcwd() + "\\")
        runner_secrets = [
            data[i] for i in data.keys()
        ]
        
    else: runner_secrets = secrets_data
    

    for secret_key in runner_secrets:
        account = Web3Account(secret_key, "zksync")
        elig_response = Connext(account, proxies=choice(proxies)).check_eligible()

        with open("results.txt", "a", encoding="utf-8") as file:
            file.write(f'{account.address} | {"".join(i + " " for i in elig_response)}\n')