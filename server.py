import json

from flask import Flask, request

from db import User, Address
from api import Wallet

app = Flask(__name__)

@app.route('/portfolio', methods=['GET'])
def portfolio():
    if len(request.args) == 0:
        print("hello")
        return {"error": "No params supplied"}, 404
    
    # get user id from params
    user_id = request.args.get('user_id', None)

    # if user_id params did not come, return error
    if not user_id:
        return {"error": "Wrong params"}, 500 

    # list all addresses stored for this user
    addrs_in_portfolio = db.list({"user_id": 1})
    addrs_in_portfolio = [i.get("address") for i in addrs_in_portfolio]

    # get fresh data from API

    # wallet = Wallet()
    # portfolio_data = wallet.get_wallets(addrs_in_portfolio)

    ## mock data
    portfolio_data = json.load(open('data.json'))

    print(1)

    return portfolio_data, 200

if __name__ == '__main__':
    db = Address()
    app.run()