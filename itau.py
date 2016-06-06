from bankscraper import BankScraper, AnotherActiveSessionException, MaintenanceException, GeneralException
import uuid

from time import sleep

import requests
from requests.adapters import HTTPAdapter 
from datetime import datetime

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

    def __init__(self, branch, account, password, days=15, omit_sensitive_data=False, balance=False, quiet=False):
        if not quiet:
            print('[*] Itaú Parser is starting...')

        self.branch = str(branch)
        self.account = str(account).split('-')[0]
        self.dac = str(account).split('-')[1]
        self.password = str(password)
        self.session = requests.Session()

        self.omit_sensitive_data = omit_sensitive_data
        self.balance = balance
        self.quiet = quiet

        self.encoding = ''
        self.account_owner = ''
        self.account_segment = ''
        self.account_type = ''
        self.account_document = ''
        self.account_owner_birthday = ''
        self.ticket = ''


        self.transaction_days = days


        self.holder_code = ''


        self.eula_url = ''

        self.android_last_build = ''
        self.android_url = ''

        self.ios_last_build = ''
        self.ios_url = ''

        self.windowsphone_last_build = ''
        self.windowsphone_url = ''

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
            print('[*] Logging in to {} {}-{}'.format(self.branch,self.account,self.dac))

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


        self.eula_url = obj['Dados']['home_config']['link_termos_uso']


        for o in obj['Dados']['app_config']['plataforma']:
            if o['nome'] == 'android':
                self.android_last_build = o['build_number_atual']
                self.android_url = o['url_loja:']
            elif o['nome'] == 'iphone':
                self.ios_last_build = o['build_number_atual']
                self.ios_url = o['url_loja:']
            elif o['nome'] == 'windowsphone':
                self.windowsphone_last_build = o['build_number_8']
                self.windowsphone_url = o['url_loja:']


        if not self.quiet:
            print()
            print('[*] EULA Url: {}'.format(self.eula_url))
            print()
            print('[*] Android Last Version: {}'.format(self.android_last_build))
            print('[*] iOS Last Version: {}'.format(self.ios_last_build))
            print('[*] Windows Phone Last Version: {}'.format(self.windowsphone_last_build))
            print()

        now = datetime.now()

        if not self.quiet:
            print('[*] Getting account information...')

        payload = {
            'DeviceId': self.device_id,
            'UserId': self.user_id,
            'UA': 'AppItauSmartPF:R1;{version};{platform};{platform_version};{platform_model};{{F001;}}'.format(version=self.app_version, platform=self.platform, platform_version=self.platform_version,platform_model=self.platform_model),
            'Agencia': self.branch,
            'Dac':  self.dac,
            'platform': self.platform,
            'Tecnologia': 4,
            'Sv': '',
            'appID': self.app_id,
            'appver': self.app_version,
            'ListaMenu': '',
            'Conta': self.account,
            'channel': 'rc',
            'serviceID': 'srvJLogin',
            'cacheid': '',
            'Senha': self.password,
            'platformver': self.platform_extra_version,
            'DadosSessaoDevice': self.build_device_session('root:X|PD:{dt1},{dt2}H'.format(dt1=self.format_date_pd(now), dt2=self.format_date_pd(datetime.now())))
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

        self.account_owner = obj['Dados']['RESPOSTA']['DADOS']['NOME_CORRENTISTA'].strip().title()
        self.account_segment = obj['Dados']['RESPOSTA']['DADOS']['SEGMENTO']
        self.account_type = 'Física' if obj['Dados']['RESPOSTA']['DADOS']['PESSOA'] == 'F' else 'Jurídica'
        self.account_document = obj['Dados']['RESPOSTA']['DADOS']['CPF_CNPJ_CLIENTE']
        self.account_owner_birthday = datetime.strptime(obj['Dados']['RESPOSTA']['DADOS']['DT8_GB07'], '%d%m%Y')
        self.holder_code = obj['Dados']['RESPOSTA']['DADOS']['TITULARIDADE']
        self.ticket = obj['Ticket']
        

        if not self.quiet:
            print('[*] Account Branch: {}'.format(self.branch))
            print('[*] Account Number: {}-{}'.format(self.account, self.dac))
            print('[*] Account Segment: {}'.format(self.account_segment))
            print('[*] Account Type: {}'.format(self.account_type))
            print('[*] Account Owner: {}'.format(self.account_owner))
            print('[*] Account Owner Document: {}'.format(self.account_document if not self.omit_sensitive_data else 'OMITED'))
            print('[*] Account Owner Birthday: {}'.format(self.account_owner_birthday.strftime('%Y-%m-%d')))
            print()


    def logout(self):

        if not self.quiet:
            print('[*] Logging out...')

        now1 = self.format_date_pd(datetime.now())
        sleep(0.5)
        now2 = self.format_date_pd(datetime.now())
        sleep(0.5)
        now3 = self.format_date_pd(datetime.now())
        sleep(0.5)
        now4 = self.format_date_pd(datetime.now())
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
            'DadosSessaoDevice': 'PD:{d1},{d2},{d3},{d4}|AGC_SAIR:{ag}{ac}{dac}'.format(d1=now1,d2=now2,d3=now3,d4=now4,ag=self.branch,ac=self.account,dac=self.dac),
            'Lista': ''

        }

        r = self.post(payload)

        obj = self.json_recursive_loads(r.content.decode())

        if obj['opstatus'] == 0:
            if not self.quiet:
                print('[+] Logged out succesfully!')
        else:
            raise GeneralException('Something went wrong...', request=r)


    def warmup(self):
        if not self.quiet:
            print('[*] Warming up...')
        now1 = self.format_date_pd(datetime.now())
        sleep(0.5)
        now2 = self.format_date_pd(datetime.now())
        sleep(0.5)
        now3 = self.format_date_pd(datetime.now())
        sleep(0.5)
        now4 = self.format_date_pd(datetime.now())
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
            'DadosSessaoDevice': 'PD:{d1},{d2},{d3},{d4}|AGC_CSTA_PORT_TIPO:{ag}{ac}{dac}'.format(d1=now1,d2=now2,d3=now3,d4=now4,ag=self.branch,ac=self.account,dac=self.dac),
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
            'AccountNumber': self.account,
            'Dac': self.dac,
            'Type': 0,
            'BranchNumber': self.branch,
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


    def get_transactions(self):
        if not self.quiet:
            print('[*] Getting transactions...')
        now1 = self.format_date_pd(datetime.now())
        sleep(0.5)
        now2 = self.format_date_pd(datetime.now())
        sleep(0.5)
        now3 = self.format_date_pd(datetime.now())
        sleep(0.5)
        now4 = self.format_date_pd(datetime.now())
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
            'DadosSessaoDevice': 'PD:{d1},{d2},{d3},{d4}|AGC_EXTRATO:{ag}{ac}{dac}'.format(d1=now1,d2=now2,d3=now3,d4=now4,ag=self.branch,ac=self.account,dac=self.dac),
            'Lista': '{}|V|CC|E|1'.format(self.transaction_days)

        }


        r = self.post(payload)

        obj = self.json_recursive_loads(r.content.decode())

        if obj['opstatus'] == 0:
            pass
        else:
            raise GeneralException('Something went wrong...', request=r)

        trans = self.parse_transactions(obj['Dados']['RESPOSTA']['DADOS']['DADOSEXTRATO']['EXTRATO']['MOVIMENT'])


        bl = []

        if self.balance:
            for t in trans:
                if 'S A L D O' in t:
                    bl.append(t)
            print('{}{}'.format('-' if bl[-1].split()[0] == 'D' else '', bl[-1].split()[-1]))
            return '{}{}'.format('-' if bl[-1].split()[0] == 'D' else '', bl[-1].split()[-1])

        else:
            bl = []
            for t in trans:
                bl.append(t)
                print(t)
            return bl


    def parse_transactions(self, transactions):
        tlist = []

        for trans in transactions:
            try:
                if self.omit_sensitive_data:
                    if trans['HISTOR'] not in ['SALDO', 'S A L D O'] and 'REMUNERACAO' not in trans['HISTOR'] and 'SALDO' not in trans['HISTOR']:
                        msg = '{} - {} - {} - {}'.format(trans['DC2'], trans['DT8'], trans['HISTOR'], trans['VAL2'])
                        tlist.append(msg)
                else:
                    msg = '{} - {} - {} - {}'.format(trans['DC2'], trans['DT8'], trans['HISTOR'], trans['VAL2'])
                    tlist.append(msg)
            except:
                pass

        return tlist


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


    itau = Itau(args.branch, args.account, args.password, args.days, args.omit, args.balance, args.quiet)
    try:
        itau.login()
        itau.warmup()
        itau.get_transactions()
    except Exception as e:
        traceback.print_exc()
        exit(1)
    finally:
        itau.logout()

