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


class Sodexo(object):

    api_endpoint = 'https://www.app.sodexo.com.br/PMobileServer/Primeth'


    def __init__(self, card, document, omit_sensitive_data=False, quiet=False):
        if not quiet:
            print('[*] Sodexo Parser is starting...')


        self.account = Account(document=document, card=card, account_type='card')

        self.omit_sensitive_data = omit_sensitive_data
        self.quiet = quiet
        self.account.currency = 'R$'
        self.account.bank = 'Sodexo'


        self.session = requests.Session()
        self.session.mount(self.api_endpoint, HTTPAdapter(max_retries=32,pool_connections=50, pool_maxsize=50))
        self.session.headers.update({'User-Agent': 'Apache-HttpClient/android/Nexus 5'})
        self.session.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})

    
    def get_balance(self):
        payload = {
            'th': 'thsaldo',
            'cardNumber': self.account.card,
            'document': self.account.document
        }


        r = self.session.post(self.api_endpoint, data=payload)

        body = r.json()

        self.account.service_name = body['serviceName']
        self.account.status = body['cardStatus']
        self.account.company = body['companyName']
        self.account.owner = Owner(body['name'])


        self.account.balance = Decimal(body['balanceAmount'].split()[-1].replace('.', '').replace(',', '.'))



        if not self.quiet:
            print()
            self.account.print_info()
            print()

        print(self.account.get_balance())

        return self.account.get_balance()

    def get_transactions(self):
        if not self.quiet:
            print('[*] Getting transactions...')

        payload = {
            'th': 'thsaldo',
            'cardNumber': self.account.card,
            'document': self.account.document
        }


        r = self.session.post(self.api_endpoint, data=payload)

        body = r.json()

        self.account.service_name = body['serviceName']
        self.account.status = body['cardStatus']
        self.account.company = body['companyName']
        self.account.owner = Owner(body['name'])


        self.account.balance = body['balanceAmount']



        if not self.quiet:
            print()
            self.account.print_info()
            print()


        self.parse_transactions(body['transactions'])
        for trans in self.account.transactions:
            trans.print_info()

        return self.account.transactions


    def parse_transactions(self, transactions):
        tlist = []

        for trans in transactions:
            try:
                t = Transaction(trans['history'])
                t.id = trans['authorizationNumber']
                t.currency = 'R$'
                t.date = datetime.strptime(trans['date'], '%d/%m/%Y').date()
                t.value = Decimal(trans['value'].split()[-1].replace('.', '').replace(',', '.'))
                t.sign = '-' if trans['type'].endswith('bito') else '+'
                t.raw = trans
                self.account.transactions.append(t)
            except:
                traceback.print_exc()
                continue

        return self.account.transactions


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Program to parse financial transactions from Sodexo benefit')
    parser.add_argument('--card', help='Sodexo Card Number', required=True)
    parser.add_argument('--document', help='Sodexo Card Owner Document', required=True)
    parser.add_argument('--omit-sensitive-data', dest='omit', action='store_true', help='Omit sensitive data, like documents, paychecks and current balance')
    parser.add_argument('--balance', dest='balance', action='store_true', help='Get only account balance')
    parser.add_argument('--quiet', dest='quiet', action='store_true', help='Be quiet')


    args = parser.parse_args()


    sodexo = Sodexo(args.card, args.document, args.omit, args.quiet)
    try:
        if args.balance:
            sodexo.get_balance()
        else:
            sodexo.get_transactions()
    except Exception as e:
        traceback.print_exc()
        exit(1)
    finally:
        pass
        

