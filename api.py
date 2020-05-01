from datetime import timedelta, datetime
import json
import requests

endpoints = {
    "get_addr_info": "getAddressInfo"
}

WEI = 1e+18

API_KEY = "freekey"
API_URL = "https://api.ethplorer.io/"

CACHE_PERIOD = 60 * 5 # 5 min

class Wallet:
    def __init__(self):

        self.wallets = {}
        self.total_eth_balance = 0
        self.total_eth_balance_fiat = 0
        self.total_token_balance = 0 # balance of all tokens combined in fiat
        self.total_balance = 0  # balance of eth + tokens in fiat
        self.request_sent = False


    def _make_request(self, endpoint):
        url = f"{API_URL}{endpoint}?apiKey={API_KEY}"
        # print(url)

        response = requests.get(url)
        return response


    def get_wallets(self, wallets: list):
        assert isinstance(wallets, list)

        time_now = datetime.now()

        # if request was sent earlier than cache period or not sent yet then start new request
        if not self.request_sent or (time_now - self.request_sent).total_seconds() > CACHE_PERIOD:
            for addr in wallets:
                print(f"Starting new request for: {addr}")
                res = self._get_addr_info(addr)

                if res == None:
                    self.wallets[addr] = {"status": False}


            # set request sent time to now
            self.request_sent = time_now
        print((time_now - self.request_sent).total_seconds())
        print("Getting cached data")

        return self._to_json()


    def _get_addr_info(self, addr):
        endpoint = f"{endpoints['get_addr_info']}/{addr}"

        print(f"Getting data for addr: {addr} ...")

        response = self._make_request(endpoint)

        if not response.ok:
            print(response.text)
            return None

        try:
            data = response.json()
        except Exception:
            print("Failed converting data to json")
            print(response.text)
            return None

        # extract relevant data from response, and append to wallets
        self.wallets[addr] = self._get_wallet_data(data)

        # set new balances
        self._get_wallet_balances()

        return True


    def _get_wallet_data(self, data):
        template = {
            "status": "OK",
            "address": "",
            "eth_balance": 0,
            "eth_balance_fiat": 0,
            "tokens": []
        }

        # print(data)

        template["address"] = data["address"]
        template["eth_balance"] = data["ETH"]["balance"]
        template["eth_balance_fiat"] = data["ETH"]["balance"] * data["ETH"]["price"]["rate"]

        for token in data["tokens"]:

            token_balance = token["balance"] / WEI

            token_template = {
                "token_name": token["tokenInfo"]["name"],
                "token_symbol": token["tokenInfo"]["symbol"],
                "balance": token_balance,
                "balance_fiat": False,   # default
                "rate": False,           # default
            }

            if token["tokenInfo"]["price"]:
                token_template["balance_fiat"] = token_balance * token["tokenInfo"]["price"]["rate"]
                token_template["rate"] = token["tokenInfo"]["price"]["rate"]

            template["tokens"].append(token_template)

        return template


    def _get_wallet_balances(self):

        # reset balances
        self.total_eth_balance = 0
        self.total_eth_balance_fiat = 0
        self.total_token_balance = 0
        self.total_balance = 0

        # calculate balance for each wallet and add together
        for _, wallet in self.wallets.items():
            # eth balance
            self.total_eth_balance += wallet["eth_balance"]
            self.total_eth_balance_fiat = wallet["eth_balance_fiat"]

            # total token balance
            total_tokens = 0
            for token in wallet["tokens"]:
                # if we have valid price
                if token["balance_fiat"]:
                    total_tokens += token["balance_fiat"]


            self.total_token_balance += total_tokens
            self.total_balance += self.total_eth_balance_fiat + self.total_token_balance

    def _to_json(self):
        # response Object:
        response = {
            "request_time": self.request_sent.timestamp(),
            "total_balance_fiat": self.total_balance,
            "total_balance_eth": self.total_eth_balance,
            "total_balance_eth_fiat": self.total_eth_balance_fiat,
            "wallets": self.wallets
        }

        return response


if __name__ == "__main__":
    wallet = Wallet()