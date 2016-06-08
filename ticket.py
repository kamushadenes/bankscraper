from bankscraper import BankScraper, AnotherActiveSessionException, MaintenanceException, GeneralException, Account, Transaction, App, Owner
from decimal import Decimal
import uuid

from time import sleep

import requests
from requests.adapters import HTTPAdapter 
from datetime import datetime, timezone, timedelta

import json

import traceback

import os

import argparse


class Ticket(object):

    api_endpoint = 'https://www.app.ticket.com.br/PMobileServer/Primeth'

    captcha_url = 'http://www.ticket.com.br/portal/stickyImg'
    login_url = 'http://www.ticket.com.br/portal/portalticket/dpages/service/captcha/getConsultCard.jsp'
    transactions_url = 'http://www.ticket.com.br/portal-web/consult-card/release/json'


    def __init__(self, card, omit_sensitive_data=False, quiet=False, dbc_username=None, dbc_password=None):
        if not quiet:
            print('[*] Ticket Parser is starting...')


        self.account = Account(card=card, account_type='card')

        self.account.currency = 'R$'

        self.omit_sensitive_data = omit_sensitive_data
        self.quiet = quiet
        self.account.currency = 'R$'
        self.account.bank = 'Ticket'

        #self.dbc_username = dbc_username
        #self.dbc_password = dbc_password

        #self.dbc_client = deathbycaptcha.SocketClient(self.dbc_username, self.dbc_password)

        self.captcha = ''
        self.token = ''



        self.session = requests.Session()
        self.session.mount(self.api_endpoint, HTTPAdapter(max_retries=32,pool_connections=50, pool_maxsize=50))
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36'})
        self.session.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
        self.session.headers.update({'Referer': 'http://www.ticket.com.br/portal/consulta-de-saldo/'})


    def get_unix_timestamp(self):
        return int((datetime.now(timezone.utc) + timedelta(days=3)).timestamp() * 1e3)

    def login(self):

        # We can just pretend to solve the captcha
        unixtm = self.get_unix_timestamp()
        path = '/tmp/.bankscraper_captcha_{}'.format(os.getpid())
        r = self.session.get('{}?{}'.format(self.captcha_url, unixtm, stream=True))
        if r.status_code == 200:
            with open(path, 'wb') as f:
                for chunk in r:
                    f.write(chunk)

        captcha = '123456'

        if captcha:
            self.captcha = captcha

            r = self.session.post('{}?answer={}&card={}&d={}'.format(self.login_url, self.captcha, self.account.card, unixtm))

            self.token = r.json()['token']

            return self.token



    def get_balance(self):
        payload = {
            'card': self.account.card,
            'answer': self.captcha,
            'token': self.token,
        }


        r = self.session.post(self.transactions_url, data=payload)

        body = r.json()

        self.account.balance = Decimal(body['card']['balance']['value'].replace(',', '.'))

        print(self.account.get_balance())

        return self.account.get_balance()

    def get_transactions(self):
        if not self.quiet:
            print('[*] Getting transactions...')
            print()

        payload = {
            'card': self.account.card,
            'answer': self.captcha,
            'token': self.token,
        }


        r = self.session.post(self.transactions_url, data=payload)

        body = r.json()

        if not body['status']:
            print('[-] Failed to get card: {}'.format(body['messageError']))
            exit(1)


        self.account.balance = Decimal(body['card']['balance']['value'].replace(',', '.'))


        self.parse_transactions(body['card']['release'])
        for trans in self.account.transactions:
            trans.print_info()

        return self.account.transactions


    def parse_transactions(self, transactions):
        tlist = []

        for trans in transactions:
            try:
                t = Transaction(trans['description'])
                t.currency = 'R$'
                t.date = datetime.strptime(trans['date'], '%d/%m/%Y').date()
                t.value = Decimal(trans['value'].split()[-1].replace('.', '').replace(',', '.'))
                t.sign = '-' if trans['description'] != 'DISPONIB. DE CREDITO' else '+'
                t.raw = trans
                self.account.transactions.append(t)
            except:
                traceback.print_exc()
                continue

        return self.account.transactions


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Program to parse financial transactions from Ticket benefit')
    parser.add_argument('--card', help='Ticket Card Number', required=True)
    parser.add_argument('--omit-sensitive-data', dest='omit', action='store_true', help='Omit sensitive data, like documents, paychecks and current balance')
    parser.add_argument('--balance', dest='balance', action='store_true', help='Get only account balance')
    parser.add_argument('--quiet', dest='quiet', action='store_true', help='Be quiet')

    args = parser.parse_args()


    ticket = Ticket(args.card, args.omit, args.quiet)
    try:
        ticket.login()
        if args.balance:
            ticket.get_balance()
        else:
            ticket.get_transactions()
    except Exception as e:
        traceback.print_exc()
        exit(1)
    finally:
        pass
        

