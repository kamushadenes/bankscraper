from bankscraper import BankScraper, AnotherActiveSessionException, MaintenanceException, GeneralException, Account, Transaction, Owner, App
import uuid
from decimal import Decimal

from time import sleep

import requests
from requests.adapters import HTTPAdapter 
from datetime import datetime, date

import json

import traceback


import argparse


class Itau(object):

    app_id = 'kspf'
    app_version = '4.1.19'
    platform = 'android'
    platform_version = '6.0.1'
    platform_extra_version = '5.6.GA_v201508271451_r3'
    platform_model = 'Nexus 5'

    device_id = 12345678
    user_id = 1234

    api_endpoint = 'https://kms.itau.com.br/middleware/MWServlet'


    device_session_template = 'Modelo: {platform_model}|Operadora:|VersaoSO:{platform_version}|appIdCore:'

    def __init__(self, branch, account, password, days=15, omit_sensitive_data=False, quiet=False):
        if not quiet:
            print('[*] Itaú Parser is starting...')

        self.account = Account(branch=str(branch), number=str(account).split('-')[0], password=str(password), dac=str(account).split('-')[1])
        self.account.bank = 'Itaú'
        self.account.currency = 'R$'

        self.session = requests.Session()

        self.omit_sensitive_data = omit_sensitive_data
        self.quiet = quiet

        self.encoding = ''
        self.ticket = ''


        self.transaction_days = days


        self.holder_code = ''

        self.session.mount(self.api_endpoint, HTTPAdapter(max_retries=32,pool_connections=50, pool_maxsize=50))
        self.session.headers.update({'User-Agent': 'Apache-HttpClient/android/Nexus 5'})
        self.session.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
        self.session.headers.update({'Cookie2': '$Version=1'})


    def json_recursive_loads(self, obj):
        obj = json.loads(obj)

        for k in obj.keys():       
            if type(obj[k]) == type(''):
                try:
                    obj[k] = json.loads(obj[k])
                except:
                    pass
        
        for k in obj.keys():       
            if type(obj[k]) == type({}):
                for kk in obj[k].keys():
                    if type(obj[k][kk]) == type(''):
                        try:
                            obj[k][kk] = json.loads(obj[k][kk])
                        except:
                            pass

        return obj


    def generate_timestamps(self):
        now1 = self.format_date_pd(datetime.now())
        sleep(0.2)
        now2 = self.format_date_pd(datetime.now())
        sleep(0.2)
        now3 = self.format_date_pd(datetime.now())
        sleep(0.2)
        now4 = self.format_date_pd(datetime.now())

        return {'d1': now1, 'd2': now2, 'd3': now3, 'd4': now4}



    def build_device_session(self, extra):

        msg = self.device_session_template.format(platform_model=self.platform_model, platform_version=self.platform_version)

        msg = msg + '|' + extra

        return msg


    def format_date_pd(self, dtobj):

        return dtobj.strftime('%-m/%-d/%Y %-H-%-M-%-S-%f')[:-3]

    def post(self, payload):
        return self.session.post(self.api_endpoint, data=payload)



    def login(self):
        if not self.quiet:
            print('[*] Logging in to {} {}-{}'.format(self.account.branch,self.account.number,self.account.dac))

        payload = {
            'Guid': '7C9C0508-6EFD-47B6-9DBA-5E4B1205D560',
            'DeviceId': self.device_id,
            'UserId': self.user_id,
            'Params': 'MOBILECORE_JSON_SMART_ITAUPF',
            'platform': 'android',
            'appID': self.app_id,
            'appver': self.app_version,
            'IPCliente': '',
            'Ticket': '',
            'channel': 'rc',
            'serviceID': 'srvJCoreRuntime',
            'cacheid': '',
            'platformver': self.platform_extra_version,
            'DadosSessaoDevice': 'Modelo:Nexus 5|Operadora:|VersaoSO:6.0.1|appIdCore:'
        }


        r = self.post(payload)


        obj = self.json_recursive_loads(r.content.decode())


        if obj['opstatus'] == 0:
            if not self.quiet:
                print('[+] Login successful!')
        else:
            raise GeneralException('Something went wrong...', request=r)


        self.account.app = App('Itaú')

        self.account.app.eula_url = obj['Dados']['home_config']['link_termos_uso']


        for o in obj['Dados']['app_config']['plataforma']:
            if o['nome'] == 'android':
                self.account.app.platform['android']['version'] = o['build_number_atual']
                self.account.app.platform['android']['url'] = o['url_loja:']
            elif o['nome'] == 'iphone':
                self.account.app.platform['ios']['version'] = o['build_number_atual']
                self.account.app.platform['ios']['url'] = o['url_loja:']
            elif o['nome'] == 'windowsphone':
                self.account.app.platform['windowsphone']['version'] = o['build_number_8']
                self.account.app.platform['windowsphone']['url']= o['url_loja:']


        if not self.quiet:
            print()
            self.account.app.print_info()
            print()

        now = datetime.now()

        if not self.quiet:
            print('[*] Getting account information...')

        t = self.generate_timestamps()
        payload = {
            'DeviceId': self.device_id,
            'UserId': self.user_id,
            'UA': 'AppItauSmartPF:R1;{version};{platform};{platform_version};{platform_model};{{F001;}}'.format(version=self.app_version, platform=self.platform, platform_version=self.platform_version,platform_model=self.platform_model),
            'Agencia': self.account.branch,
            'Dac':  self.account.dac,
            'platform': self.platform,
            'Tecnologia': 4,
            'Sv': '',
            'appID': self.app_id,
            'appver': self.app_version,
            'ListaMenu': '',
            'Conta': self.account.number,
            'channel': 'rc',
            'serviceID': 'srvJLogin',
            'cacheid': '',
            'Senha': self.account.password,
            'platformver': self.platform_extra_version,
            'DadosSessaoDevice': self.build_device_session('root:X|PD:{d1},{d2}H'.format(**t))
        }

        r = self.post(payload)

        obj = self.json_recursive_loads(r.content.decode())

        if obj['opstatus'] == 0:
            pass
        else:
            raise GeneralException('Something went wrong...', request=r)

        try:

            if int(obj['Dados']['RESPOSTA']['DADOS']['CODIGO']) == 31 :
                raise AnotherActiveSessionException(obj['Dados']['RESPOSTA']['DADOS']['MENSAGEM'])
            elif int(obj['Dados']['RESPOSTA']['DADOS']['CODIGO']) == 30:
                raise MaintenanceException(obj['Dados']['RESPOSTA']['DADOS']['MENSAGEM'])
        except KeyError:
            pass


        self.encoding = obj['Dados']['?xml']['@encoding']

        self.account.owner = Owner(obj['Dados']['RESPOSTA']['DADOS']['NOME_CORRENTISTA'].strip().title())
        self.account.segment = obj['Dados']['RESPOSTA']['DADOS']['SEGMENTO'].strip()
        self.account.type = 'Física' if obj['Dados']['RESPOSTA']['DADOS']['PESSOA'] == 'F' else 'Jurídica'
        self.account.owner.document = obj['Dados']['RESPOSTA']['DADOS']['CPF_CNPJ_CLIENTE'].strip()
        self.account.owner.birthday = datetime.strptime(obj['Dados']['RESPOSTA']['DADOS']['DT8_GB07'], '%d%m%Y')

        self.holder_code = obj['Dados']['RESPOSTA']['DADOS']['TITULARIDADE']
        self.ticket = obj['Ticket']
        

        if not self.quiet:
            print()
            self.account.print_info()
            print()
            self.account.owner.print_info()
            print()


    def logout(self):

        if not self.quiet:
            print('[*] Logging out...')

        t = self.generate_timestamps()
        payload = {
            'DeviceId': self.device_id,
            'UserId': self.user_id,
            'UA': 'AppItauSmartPF:R1;{version};{platform};{platform_version};{platform_model};{{F001;}}'.format(version=self.app_version, platform=self.platform, platform_version=self.platform_version,platform_model=self.platform_model),
            'ServiceName': 'SAIR',
            'Sv': '', 
            'appID': self.app_id,
            'appver': self.app_version,
            'IPCliente': '',
            'Ticket': self.ticket,
            'channel': 'rc',
            'serviceID': 'srvJGenerico',
            'platformver': self.platform_extra_version,
            'DadosSessaoDevice': 'PD:{d1},{d2},{d3},{d4}|AGC_SAIR:{ag}{ac}{dac}'.format(ag=self.account.branch,ac=self.account.number,dac=self.account.dac,**t),
            'Lista': ''

        }

        r = self.post(payload)

        obj = self.json_recursive_loads(r.content.decode())

        if obj['opstatus'] == 0:
            if not self.quiet:
                print('[+] Logged out succesfully!')
        else:
            raise GeneralException('Something went wrong...', request=r)


    def post_login_warmup(self):
        if not self.quiet:
            print('[*] Warming up...')
        t = self.generate_timestamps()
        payload = {
            'DeviceId': self.device_id,
            'UserId': self.user_id,
            'UA': 'AppItauSmartPF:R1;{version};{platform};{platform_version};{platform_model};{{F001;}}'.format(version=self.app_version, platform=self.platform, platform_version=self.platform_version,platform_model=self.platform_model),
            'ServiceName': 'CSTA_POR_TIPO',
            'Sv': '', 
            'appID': self.app_id,
            'appver': self.app_version,
            'IPCliente': '',
            'Ticket': self.ticket,
            'channel': 'rc',
            'serviceID': 'srvJGenerico',
            'platformver': self.platform_extra_version,
            'DadosSessaoDevice': 'PD:{d1},{d2},{d3},{d4}|AGC_CSTA_PORT_TIPO:{ag}{ac}{dac}'.format(ag=self.account.branch,ac=self.account.number,dac=self.account.dac,**t),
            'Lista': 'EMHUOYKIRBVPRCMNEWZ60XJPRNY|PF |352136067883617|00012'

        }

        r = self.post(payload)

        obj = self.json_recursive_loads(r.content.decode())

        if obj['opstatus'] == 0:
            pass
        else:
            raise GeneralException('Something went wrong...')


        payload = {
            'appID': self.app_id,
            'appver': self.app_version,
            'Ticket': self.ticket,
            'channel': 'rc',
            'serviceID': 'srvJMenu',
            'platformver': self.platform_extra_version,

        }

        r = self.post(payload)

        obj = self.json_recursive_loads(r.content.decode())

        if obj['opstatus'] == 0:
            pass
        else:
            raise GeneralException('Something went wrong...', request=r)



        payload = {
            'Guid': '7C9C0508-6EFD-47B6-9DBA-5E4B1205D560',
            'DeviceId': self.device_id,
            'UserId': self.user_id,
            'Params': self.ticket,
            'appID': self.app_id,
            'appver': self.app_version,
            'IPCliente': '',
            'Ticket': self.ticket,
            'channel': 'rc',
            'serviceID': 'srvJCoreRuntime',
            'platformver': self.platform_extra_version,
            'DadosSessaoDevice': self.build_device_session('root:X')

        }

        r = self.post(payload)

        obj = self.json_recursive_loads(r.content.decode())

        if obj['opstatus'] == 0:
            pass
        else:
            raise GeneralException('Something went wrong...', request=r)

        payload = {
            'Guid': '7C9C0508-6EFD-47B6-9DBA-5E4B1205D560',
            'DeviceId': self.device_id,
            'UserId': self.user_id,
            'Params': 'SMARTPHONE_PF_TOKEN_WEBVIEW',
            'appID': self.app_id,
            'appver': self.app_version,
            'IPCliente': '',
            'Ticket': self.ticket,
            'channel': 'rc',
            'serviceID': 'srvJGenerico',
            'platformver': self.platform_extra_version,
            'DadosSessaoDevice': self.build_device_session('root:X')

        }

        r = self.post(payload)

        obj = self.json_recursive_loads(r.content.decode())

        if obj['opstatus'] == 0:
            pass
        else:
            raise GeneralException('Something went wrong...', request=r)



        payload = {
            'HolderCodeType': 1,
            'AccountNumber': self.account.number,
            'Dac': self.account.dac,
            'Type': 0,
            'BranchNumber': self.account.branch,
            'HolderCode': self.holder_code,
            'appID': self.app_id,
            'appver': self.app_version,
            'IPCliente': '',
            'Ticket': self.ticket,
            'channel': 'rc',
            'serviceID': 'srvJGetUserInfo',
            'platformver': self.platform_extra_version,

        }

        r = self.post(payload)

        obj = self.json_recursive_loads(r.content.decode())

        if obj['opstatus'] == 0:
            pass
        else:
            raise GeneralException('Something went wrong...', request=r)


    def get_balance(self):
        if not self.quiet:
            print('[*] Getting transactions...')
        t = self.generate_timestamps()
        payload = {
            'DeviceId': self.device_id,
            'UserId': self.user_id,
            'UA': 'AppItauSmartPF:R1;{version};{platform};{platform_version};{platform_model};{{F001;}}'.format(version=self.app_version, platform=self.platform, platform_version=self.platform_version,platform_model=self.platform_model),
            'ServiceName': 'EXTRATO',
            'Sv': '', 
            'appID': self.app_id,
            'appver': self.app_version,
            'IPCliente': '',
            'Ticket': self.ticket,
            'channel': 'rc',
            'cacheid': '',
            'platform': self.platform,
            'serviceID': 'srvJGenerico',
            'platformver': self.platform_extra_version,
            'DadosSessaoDevice': 'PD:{d1},{d2},{d3},{d4}|AGC_EXTRATO:{ag}{ac}{dac}'.format(ag=self.account.branch,ac=self.account.number,dac=self.account.dac,**t),
            'Lista': '{}|V|CC|E|1'.format(self.transaction_days)

        }


        r = self.post(payload)

        obj = self.json_recursive_loads(r.content.decode())

        if obj['opstatus'] == 0:
            pass
        else:
            raise GeneralException('Something went wrong...', request=r)


        for o in obj['Dados']['RESPOSTA']['DADOS']['DADOSEXTRATO']['SALDORESUMIDO']['ITEM']:
            if o['NOME'] == 'SALDODISPSAQUERESUMO':
                self.account.balance = Decimal(o['VALOR'].replace('.', '').replace(',', '.'))
                self.account.sign = '-' if o['SINAL'] == 'D' else '+'
            elif o['NOME'] == 'LIMITELISRESUMO':
                self.account.overdraft = Decimal(o['VALOR'].replace('.', '').replace(',', '.'))

        print(self.account.get_balance())

        return self.account.get_balance()


    def get_transactions(self):
        if not self.quiet:
            print('[*] Getting transactions...')

        t = self.generate_timestamps()
        payload = {
            'DeviceId': self.device_id,
            'UserId': self.user_id,
            'UA': 'AppItauSmartPF:R1;{version};{platform};{platform_version};{platform_model};{{F001;}}'.format(version=self.app_version, platform=self.platform, platform_version=self.platform_version,platform_model=self.platform_model),
            'ServiceName': 'EXTRATO',
            'Sv': '', 
            'appID': self.app_id,
            'appver': self.app_version,
            'IPCliente': '',
            'Ticket': self.ticket,
            'channel': 'rc',
            'cacheid': '',
            'platform': self.platform,
            'serviceID': 'srvJGenerico',
            'platformver': self.platform_extra_version,
            'DadosSessaoDevice': 'PD:{d1},{d2},{d3},{d4}|AGC_EXTRATO:{ag}{ac}{dac}'.format(ag=self.account.branch,ac=self.account.number,dac=self.account.dac, **t),
            'Lista': '{}|V|CC|E|1'.format(self.transaction_days)

        }


        r = self.post(payload)

        obj = self.json_recursive_loads(r.content.decode())

        if obj['opstatus'] == 0:
            pass
        else:
            raise GeneralException('Something went wrong...', request=r)

        self.parse_transactions(obj['Dados']['RESPOSTA']['DADOS']['DADOSEXTRATO']['EXTRATO']['MOVIMENT'])

        
        for transaction in self.account.transactions:
            transaction.print_info()

        return self.account.transactions


    def parse_transactions(self, transactions):
        tlist = []

        for trans in transactions:
            try:
                if self.omit_sensitive_data:
                    if trans['HISTOR'] not in ['SALDO', 'S A L D O'] and 'REMUNERACAO' not in trans['HISTOR'] and 'SALDO' not in trans['HISTOR'] and 'SDO CTA' not in trans['HISTOR']:
                        t = Transaction(trans['HISTOR'])
                        t.value = Decimal(trans['VAL2'].replace('.', '').replace(',', '.'))
                        t.sign = '-' if trans['DC2'] == 'D' else '+'
                        t.date = self.parse_date(trans['DT8']).date()
                        t.currency = 'R$'
                        t.raw = trans

                        self.account.transactions.append(t)
                else:
                    t = Transaction(trans['HISTOR'])
                    t.value = Decimal(trans['VAL2'].replace('.', '').replace(',', '.'))
                    t.sign = '-' if trans['DC2'] == 'D' else '+'
                    t.date = self.parse_date(trans['DT8']).date()
                    t.currency = 'R$'
                    t.raw = trans
                    self.account.transactions.append(t)
            except:
                traceback.print_exc()
                pass

        return self.account.transactions


    def parse_date(self, d):
        day = d.split('/')[0]
        month = d.split('/')[1]
        year = date.today().year

        if int(month) > date.today().month:
            year = date.today().year - 1

        d = '{}/{}/{}'.format(day, month, year)

        return datetime.strptime(d, '%d/%m/%Y')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Program to parse financial transactions from Itaú')
    parser.add_argument('--branch', help='Itaú Branch number, in the format 0000', required=True)
    parser.add_argument('--account', help='Itaú Account number, in the format 00000-0', required=True)
    parser.add_argument('--password', help='Itaú Account password', required=True)
    parser.add_argument('--days', help='Transaction log days', default=15, type=int)
    parser.add_argument('--omit-sensitive-data', dest='omit', action='store_true', help='Omit sensitive data, like documents, paychecks and current balance')
    parser.add_argument('--balance', dest='balance', action='store_true', help='Get only account balance')
    parser.add_argument('--quiet', dest='quiet', action='store_true', help='Be quiet')


    args = parser.parse_args()


    itau = Itau(args.branch, args.account, args.password, args.days, args.omit, args.quiet)
    try:
        itau.login()
        #itau.warmup()
        if args.balance:
            itau.get_balance()
        else:
            itau.get_transactions()
    except Exception as e:
        traceback.print_exc()
        exit(1)
    finally:
        itau.logout()

