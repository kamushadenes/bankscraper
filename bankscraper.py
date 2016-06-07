from datetime import date

class AnotherActiveSessionException(Exception):
    def __init__(self, message, errors=None, request=None):
        super(RuntimeError, self).__init__(message)

        self.errors = errors
        print('[D] Request ({}): {}'.format(request.status_code, request.content.decode()))

class MaintenanceException(Exception):
    def __init__(self, message, errors=None, request=None):
        super(EnviromentError, self).__init__(message)

        self.errors = errors
        print('[D] Request ({}): {}'.format(request.status_code, request.content.decode()))


class GeneralException(Exception):
    def __init__(self, message, errors=None, request=None):
        super(SystemError, self).__init__(message)

        self.errors = errors

        print('[D] Request ({}): {}'.format(request.status_code, request.content.decode()))


class Transaction(object):
    
    def __init__(self, description):
        self.id = 0
        self.value = 0
        self.sign = '+'
        self.description = description
        self.date = date.today()
        self.currency = '$'

        self.raw = {}


    def get_value(self):
        return '{} {}'.format(self.currency, self.value if self.sign != '-' else self.value * -1)


    def __repr__(self):
        return 'Transaction #{} - {} on {}, value {}'.format(self.id, self.description, self.date, self.get_value())

    def print_info(self):
        print('[{}] {} {}'.format(self.date, self.description, self.get_value()))


class App(object):

    def __init__(self, name):
    
        self.name = ''
        self.platform = {}
        self.platform['android'] = {'version': 0, 'url': ''}
        self.platform['ios'] = {'version': 0, 'url': ''}
        self.platform['windowsphone'] = {'version': 0, 'url': ''}

        self.eula_url = ''


    def __repr__(self):
        return 'App {}, with versions {} (Android), {} (iOS) and {} (Windows Phone)'.format(self.name, self.platform['android']['version'], self.platform['ios']['version'], self.platform['windowsphone']['version'])

    def print_info(self):
        print('[*] EULA Url: {}'.format(self.eula_url))                      
        print()                                                              
        print('[*] Android Last Version: {}'.format(self.platform['android']['version']))
        print('[*] iOS Last Version: {}'.format(self.platform['ios']['version']))        
        print('[*] Windows Phone Last Version: {}'.format(self.platform['windowsphone']['version']))


class Account(object):


    def __init__(self, branch, number, password=None, dac=None, account_type='bank'):
        self.bank = 'Generic'
        self.transactions = []
        self.currency = '$'

        self.account_type = account_type
        if self.account_type == 'card':
            self.card = number
            self.document = branch
            self.company = ''
            self.status = ''
            self.service_name = ''
        elif self.account_type == 'bank':
            self.branch = branch
            self.number = number
            self.password = password
            self.dac = dac


        self.balance = 0
        self.sign = '+'
        self.segment = ''

        self.type = ''

        self.owner = None

        self.app = App('Generic')

    def get_balance(self):
        return '{} {}'.format(self.currency, self.balance if self.sign != '-' else self.balance * -1)

    def __repr__(self):
        if self.account_type == 'bank':
            return 'Bank Account at {}, Branch {}, Number {}, Segment {} {}, with balance of {}'.format(self.bank, self.branch, self.number, self.type, self.segment, self.get_balance())
        elif self.account_type == 'card':
            return 'Card Account at {}, Number {}, Document {}, with balance of {}'.format(self.bank, self.card, self.document, self.get_balance())

    def print_info(self):
        if self.account_type == 'bank':
            print('[*] Account Branch: {}'.format(self.branch))
            print('[*] Account Number: {}{}'.format(self.number, self.dac))
            print('[*] Account Segment: {}'.format(self.segment))
            print('[*] Account Type: {}'.format(self.type))
        elif self.account_type == 'card':
            print('[*] Service Name: {}'.format(self.service_name))                                                                                                                                                                                                    
            print('[*] Card Status: {}'.format(self.status))              
            print('[*] Company: {}'.format(self.company))                 
            print('[*] Owner: {}'.format(self.owner.name))                          
            print('[*] Card Number: {}'.format(self.card))              
            print('[*] Document: {}'.format(self.document))    


class Owner(object):

    def __init__(self, name):
        self.name = name
        self.document = ''
        self.birthday = None

    def __repr__(self):
        if not self.birthday:
            return 'Owner {}, with document {}'.format(self.name, self.document)
        else:
            return 'Owner {}, with document {}, born on {}'.format(self.name, self.document, self.birthday)

    def print_info(self):
        print('[*] Account Owner: {}'.format(self.name))
        print('[*] Account Owner Document: {}'.format(self.document))
        print('[*] Account Owner Birthday: {}'.format(self.birthday.strftime('%Y-%m-%d')))


class BankScraper(object):

    def login(self):
        pass

    def logout(self):
        pass

    def get_transacations(self):
        pass

    def get_balance(self):
        pass

    def pre_login_warmup(self):
        pass

    def post_login_warmup(self):
        pass

    def pre_transactions_warmup(self):
        pass

    def post_transactions_warmup(self):
        pass

    def pre_logout_warmup(self):
        pass

    def post_logout_warmup(self):
        pass
