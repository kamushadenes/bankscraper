import requests
from requests.adapters import HTTPAdapter
from bankscraper import BankScraper, AnotherActiveSessionException, MaintenanceException, GeneralException, Account, Transaction, Owner, App
from random import randint

from datetime import datetime, date


import traceback
import argparse




class BB(BankScraper):

    api_endpoint = 'https://mobi.bb.com.br/mov-centralizador/'
    idDispositivo = '000000000000000'
    ida = '00000000000000000000000000000000'

    hash_url = 'https://mobi.bb.com.br/mov-centralizador/hash'
    login_url = 'https://mobi.bb.com.br/mov-centralizador/servico/ServicoLogin/login'
    balance_url = 'https://mobi.bb.com.br/mov-centralizador/servico/ServicoSaldo/saldo'
    transactions_url = 'https://mobi.bb.com.br/mov-centralizador/tela/ExtratoDeContaCorrente/extrato'


    post_login_warmup_url1 = 'https://mobi.bb.com.br/mov-centralizador/servico/ServicoVersionamento/servicosVersionados'
    post_login_warmup_url2 = 'https://mobi.bb.com.br/mov-centralizador/servico/ServicoVersaoCentralizador/versaoDaAplicacaoWeb'
    post_login_warmup_url3 = 'https://mobi.bb.com.br/mov-centralizador/servico/ServicoMenuPersonalizado/menuPersonalizado'
    post_login_warmup_url4 = 'https://mobi.bb.com.br/mov-centralizador/servico/ServicoMenuTransacoesFavoritas/menuTransacoesFavoritas'





    def __init__(self, branch, account, password, days, omit_sensitive_info=False, quiet=False):
        if not quiet:
            print('[*] Banco do Brasil Parser is starting...')

        self.account = Account(branch, account, password)

        self.account.bank = 'Banco do Brasil'
        self.account.currency = 'R$'

        self.days = days

        self.omit_sensitive_info = omit_sensitive_info
        self.quiet = quiet

        self.nick = 'NickRandom.{}'.format(randint(1000,99999))

        self.idh = ''

        self.mci = ''
        self.segmento = ''

        self.session = requests.Session()
        self.session.mount(self.api_endpoint, HTTPAdapter(max_retries=32,pool_connections=50, pool_maxsize=50))
        self.session.headers.update({'User-Agent': 'Android;Google Nexus 5 - 6.0.0 - API 23 - 1080x1920;Android;6.0;vbox86p-userdebug 6.0 MRA58K eng.buildbot.20160110.195928 test-keys;mov-android-app;6.14.0.1;en_US;cpu=0|clock=|ram=2052484 kB|espacoSDInterno=12.46 GB|isSmartphone=true|nfc=false|camera=true|cameraFrontal=true|root=true|reconhecimentoVoz=false|resolucao=1080_1776|densidade=3.0|'})
        self.session.headers.update({'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'})





    def login(self):
        payload = {
            'hash': '',
            'idh': '',
            'id': self.ida,
            'idDispositivo': self.idDispositivo,
            'apelido': self.nick
        }


        r = self.session.post(self.hash_url, data=payload)

        self.idh = r.content


        payload = {
            'idh': self.idh,
            'senhaConta': self.account.password,
            'apelido': self.nick,
            'dependenciaOrigem': self.account.branch,
            'numeroContratoOrigem': self.account.number,
            'idRegistroNotificacao': '',
            'idDispositivo': self.idDispositivo,
            'titularidade': 1
        }


        r = self.session.post(self.login_url, data=payload)

        j = r.json()

        self.mci = j['login']['mci']
        self.account.type = j['login']['segmento']
        self.account.owner = Owner(j['login']['nomeCliente'])

        if not self.quiet:
            print()
            self.account.print_info()
            print()



    def post_login_warmup(self):
        payload = {
            'servico/ServicoVersionamento/servicosVersionados:': '',
            'idh': self.idh,
            'idDispositivo': self.idDispositivo,
            'apelido': self.nick
        }

        for url in [post_login_warmup_url1, post_login_warmup_url2, post_login_warmup_url3, post_login_warmup_url4]:
            self.session.post(url, data=payload)


    def get_balance(self):
        payload = {
            'servico/ServicoSaldo/saldo': '',
            'idh': self.idh, 
            'idDispositivo': self.idDispositivo,
            'apelido': self.nick
        }


        r = self.session.post(self.balance_url, data=payload)

        j = r.json()

        jr = j['servicoSaldo']['saldo']

        self.account.balance = float(jr.split()[0].replace(',', '.')) * -1 if jr.split()[-1] == 'D' else float(jr.split()[0].replace(',', '.'))

        print(self.account.get_balance())


    def get_transactions(self):
        payload = {
            'abrangencia': 8,
            'idh': self.idh, 
            'idDispositivo': self.idDispositivo,
            'apelido': self.nick
        }


        r = self.session.post(self.transactions_url, data=payload)

        j = r.json()

        jr = j['conteiner']['telas'][0]['sessoes']

        for s in jr:
            if s['TIPO'] == 'sessao' and s.get('cabecalho'):
                if s['cabecalho'].startswith('M') and 'ncia:' in s['cabecalho']:
                    month = s['cabecalho'].split()[-3:]

                    for tt in s['celulas']:
                        if tt['TIPO'] == 'celula':
                            if len(tt['componentes']) == 3 and tt['componentes'][0]['componentes'][0]['texto'] != 'Dia':
                                t = Transaction(tt['componentes'][1]['componentes'][0]['texto'])
                                t.date = self.parse_date(tt['componentes'][0]['componentes'][0]['texto'], month[0], month[2]).date()
                                t.value = float(tt['componentes'][2]['componentes'][0]['texto'].split()[0].replace(',', '.'))
                                t.sign = '-' if tt['componentes'][2]['componentes'][0]['texto'].split()[-1] == 'D' else '+'
                                t.currency = 'R$'
                                t.raw = tt['componentes']
                                self.account.transactions.append(t)
                            else:
                                continue


        for trans in self.account.transactions:
            trans.print_info()

        return self.account.transactions

    def parse_date(self, day, month, year):

        m2n = {
            'Janeiro': 1,
            'Fevereiro': 2,
            'Marco': 3,
            'Março': 3,
            'Abril': 4,
            'Maio': 5,
            'Junho': 6,
            'Julho': 7,
            'Agosto': 8,
            'Setembro': 9,
            'Outubro': 10,
            'Novembro': 11,
            'Dezembro': 12
        }


        return datetime.strptime('{}/{}/{}'.format(day, m2n[month], year), '%d/%m/%Y')



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Program to parse financial transactions from Banco do Brasil')
    parser.add_argument('--branch', help='Banco do Brasil Branch number, in the format 0000-0', required=True)
    parser.add_argument('--account', help='Banco do Brasil Account number, in the format 0000-0', required=True)
    parser.add_argument('--password', help='Banco do Brasil Account password', required=True)
    parser.add_argument('--days', help='Transaction log days', default=15, type=int)
    parser.add_argument('--omit-sensitive-data', dest='omit', action='store_true', help='Omit sensitive data, like documents, paychecks and current balance')
    parser.add_argument('--balance', dest='balance', action='store_true', help='Get only account balance')
    parser.add_argument('--quiet', dest='quiet', action='store_true', help='Be quiet')

    args = parser.parse_args()

    bb = BB(args.branch, args.account, args.password, args.days, args.omit, args.quiet)

    try:
        bb.login()
        if args.balance:
            bb.get_balance()
        else:
            bb.get_transactions()
    except Exception as e:
        traceback.print_exc()
        exit(1)
    finally:
        bb.logout()

