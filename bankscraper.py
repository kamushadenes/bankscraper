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


class BankScraper(object):

    def login(self):
        pass

    def logout(self):
        pass

    def get_transacations(self):
        pass

    def get_balance(self):
        pass

    def scrap(self):
        pass
