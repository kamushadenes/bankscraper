from bankscraper import BankScraper, AnotherActiveSessionException, MaintenanceException, GeneralException
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


    def __init__(self, card, document, omit_sensitive_data=False, balance=False, quiet=False):
        if not quiet:
            print('[*] Sodexo Parser is starting...')

        self.card = card
        self.document = document
        self.omit_sensitive_data = omit_sensitive_data
        self.balance = balance
        self.quiet = quiet


        self.session = requests.Session()
        self.session.mount(self.api_endpoint, HTTPAdapter(max_retries=32,pool_connections=50, pool_maxsize=50))
        self.session.headers.update({'User-Agent': 'Apache-HttpClient/android/Nexus 5'})
        self.session.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})


    def get_transactions(self):
        if not self.quiet:
            print('[*] Getting transactions...')

        payload = {
            'th': 'thsaldo',
            'cardNumber': self.card,
            'document': self.document
        }


        r = self.session.post(self.api_endpoint, data=payload)

        body = r.json()

        if not self.quiet:
            print()
            print('[*] Service Name: {}'.format(body['serviceName']))
            print('[*] Card Status: {}'.format(body['cardStatus']))
            print('[*] Company: {}'.format(body['companyName']))
            print('[*] Owner: {}'.format(body['name']))
            print('[*] Card Number: {}'.format(body['cardNumber']))
            print('[*] Document: {}'.format(body['document']))
            if not self.balance:
                print()
                print('[*] Balance: {}'.format(body['balanceAmount']))
            print()


        if self.balance:
            print(body['balanceAmount'])
            return body['balanceAmount']
        else:
            transactions = self.parse_transactions(body['transactions'])
            for trans in transactions:
                print(trans)
            return transactions


    def parse_transactions(self, transactions):
        tlist = []

        for trans in transactions:
            try:
                msg = '{} - {} - {} - {}'.format(trans['type'], trans['date'], trans['history'], trans['value'])
                tlist.append(msg)
            except:
                pass

        return tlist


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Program to parse financial transactions from Sodexo')
    parser.add_argument('--card', help='Sodexo Card Number', required=True)
    parser.add_argument('--document', help='Sodexo Card Owner Document', required=True)
    parser.add_argument('--omit-sensitive-data', dest='omit', action='store_true', help='Omit sensitive data, like documents, paychecks and current balance')
    parser.add_argument('--balance', dest='balance', action='store_true', help='Get only account balance')
    parser.add_argument('--quiet', dest='quiet', action='store_true', help='Be quiet')


    args = parser.parse_args()


    sodexo = Sodexo(args.card, args.document, args.omit, args.balance, args.quiet)
    try:
        sodexo.get_transactions()
    except Exception as e:
        traceback.print_exc()
        exit(1)
    finally:
        pass
        

