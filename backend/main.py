import os
from typing import List
from dotenv import load_dotenv
import plaid
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.products import Products
from plaid.api import plaid_api
from fastapi import FastAPI
from datetime import datetime, timedelta

from models import AccessToken, TokenExchangeRequest, Transaction

load_dotenv()

PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')
PLAID_PRODUCTS = os.getenv('PLAID_PRODUCTS', 'transactions').split(',')

host = plaid.Environment.Sandbox

configuration = plaid.Configuration(
    host=host,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
        'plaidVersion': '2020-09-14'
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

app = FastAPI()


@app.get('/')
def main():
    return {"test": True}


@app.post('/create_sandbox_public_token')
def create_sandbox_public_token():
    INSTITUTION_ID = "ins_109508"

    request = SandboxPublicTokenCreateRequest(
        institution_id=INSTITUTION_ID,
        initial_products=[Products('transactions')]
    )

    try:
        response = client.sandbox_public_token_create(request)
        return response.to_dict()
    except plaid.ApiException as e:
        return {"error": e}


@app.post('/exchange_public_token')
def exchange_public_token(request: TokenExchangeRequest):
    exchange_request = ItemPublicTokenExchangeRequest(
        public_token=request.public_token)

    try:
        # Exchanging the public token for an access token
        exchange_response = client.item_public_token_exchange(exchange_request)
        access_token = exchange_response['access_token']
        item_id = exchange_response['item_id']

        # You should securely store the access token and item ID for future use
        # ...

        return {'access_token': access_token, 'item_id': item_id}
    except plaid.ApiException as e:
        return {"error": str(e)}


def filter_transaction_data(transaction):
    keys_to_remove = ['authorized_date', 'authorized_datetime', 'category_id', 'check_number', 'datetime',
                      'payment_meta', 'pending', 'pending_transaction_id', 'transaction_code',
                      'transaction_id', 'transaction_type', 'personal_finance_category',
                      'unofficial_currency_code', 'merchant_name']
    transaction['date'] = str(transaction['date'])
    for key in keys_to_remove:
        transaction.pop(key, None)
    return transaction


@app.get('/transactions', response_model=List[Transaction])
def get_transactions(request: AccessToken):

    # Change this later to request a specific time range
    request = TransactionsGetRequest(
        access_token=request.access_token,
        start_date=datetime.strptime('2022-01-01', '%Y-%m-%d').date(),
        end_date=datetime.strptime('2022-01-02', '%Y-%m-%d').date(),
    )

    response = client.transactions_get(request)
    transactions = response['transactions']
    return [Transaction(**filter_transaction_data(
        transaction.to_dict())) for transaction in transactions]
