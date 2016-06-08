from bankscraper import BankScraper, AnotherActiveSessionException, MaintenanceException, GeneralException, Account, Transaction, App, Owner
from decimal import Decimal
import uuid

from time import sleep

import requests
from requests.adapters import HTTPAdapter 
from datetime import datetime

import json

import traceback


import argparse


class Nubank(object):

    api_endpoint = 'https://prod-auth.nubank.com.br/'
    login_url = 'https://prod-auth.nubank.com.br/api/token'

    pre_login_url = 'https://conta.nubank.com.br/#/login'


    serialVersionUID = '3896265166680750087L'

    def __init__(self, document, password, omit_sensitive_data=False, quiet=False):
        if not quiet:
            print('[*] Nubank Parser is starting...')


        self.account = Account(document, None, password, account_type='card')

        self.omit_sensitive_data = omit_sensitive_data
        self.quiet = quiet
        self.account.currency = 'R$'
        self.account.bank = 'Nubank'


        self.session = requests.Session()
        self.session.mount(self.api_endpoint, HTTPAdapter(max_retries=32,pool_connections=50, pool_maxsize=50))
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36'})
        self.session.headers.update({'Content-Type': 'application/json'})
        self.session.headers.update({'Referer': 'https://conta.nubank.com.br/'})

    def login(self):
        r = self.session.get(self.pre_login_url)
        

        payload = {
            'client_id': 'other.legacy',
            'client_secret': '1iHY2WHAXj25GFSHTx9lyaTYnb4uB',
            'nonce': 'NOT-RANDOM-YET',
            'grant_type': 'password',
            'login': self.account.document,
            'password': self.account.password
        }


        r = self.session.post(self.login_url, data=payload)

        body = r.json()

        if body.get('error'):
            print(body)
            print('[-] Login failed: {}'.format(body['error']))
            exit(1)

    
    def get_balance(self):
        raise NotImplementedError

    def get_transactions(self):
        raise NotImplementedError

    def parse_transactions(self, transactions):
        raise NotImplementedError


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Program to parse financial transactions from Nubank benefit')
    parser.add_argument('--document', help='Nubank Card Owner Document', required=True)
    parser.add_argument('--password', help='Nubank App Password', required=True)
    parser.add_argument('--omit-sensitive-data', dest='omit', action='store_true', help='Omit sensitive data, like documents, paychecks and current balance')
    parser.add_argument('--balance', dest='balance', action='store_true', help='Get only account balance')
    parser.add_argument('--quiet', dest='quiet', action='store_true', help='Be quiet')


    args = parser.parse_args()


    nubank = Nubank(args.document, args.password, args.omit, args.quiet)
    try:
        nubank.login()
        if args.balance:
            nubank.get_balance()
        else:
            nubank.get_transactions()
    except Exception as e:
        traceback.print_exc()
        exit(1)
    finally:
        pass
        

