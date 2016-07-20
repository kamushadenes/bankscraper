class BaseValidator(object):

    allowed_days = []

    def transaction_days(self, days):
        if int(days) in self.allowed_days:
            return True
        else:
            False

    def validate(self, method, value):
        return getattr(self, method)(value)


class DocumentValidator(BaseValidator):

    DIVISOR = 11

    def first_check_digit(self, number, weighs):
        """ This function calculates the first check digit to
            verify a cpf or cnpj vality.
            :param number: cpf or cnpj number to check the first
                           digit.  Only numbers.
            :type number: string
            :param weighs: weighs related to first check digit
                           calculation
            :type weighs: list of integers
            :returns: string -- the first digit
        """

        sum = 0
        for i in range(len(weighs)):
            sum = sum + int(number[i]) * weighs[i]
        rest_division = sum % self.DIVISOR
        if rest_division < 2:
            return '0'
        return str(11 - rest_division)

    def second_check_digit(self, updated_number, weighs):
        """ This function calculates the second check digit to
            verify a cpf or cnpj vality.
            **This function must be called after the above.**
            :param updated_number: cpf or cnpj number with the
                                   first digit.  Only numbers.
            :type number: string
            :param weighs: weighs related to second check digit calculation
            :type weighs: list of integers
            :returns: string -- the second digit
        """

        sum = 0
        for i in range(len(weighs)):
            sum = sum + int(updated_number[i]) * weighs[i]
        rest_division = sum % self.DIVISOR
        if rest_division < 2:
            return '0'
        return str(11 - rest_division)

    def cpf(self, cpf):
        if (len(cpf) != 11 or len(set(cpf)) == 1):
            return False

        first_cpf_weighs = [10, 9, 8, 7, 6, 5, 4, 3, 2]
        second_cpf_weighs = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
        first_part = cpf[:9]
        first_digit = cpf[9]
        second_digit = cpf[10]

        if (first_digit == self.first_check_digit(first_part, first_cpf_weighs) and second_digit == self.second_check_digit(cpf[:10], second_cpf_weighs)):
            return True

        return False


class CardValidator(BaseValidator):

    bin_list = []

    def bin_check(self, card):
        card_bin = card[:6]

        if len(self.bin_list) > 0:
            if card_bin in self.bin_list:
                return True
            else:
                return False
        else:
            return True

    def card(self, card, card_size):
        try:
            int(card)
        except ValueError:
            return False

        if len(card) != card_size:
            return False

        return True


class BankValidator(BaseValidator):

    branch_size = 0
    account_size = 0
    dac_size = 0
    password_size = 0

    def branch(self, branch):
        try:
            int(branch)
        except ValueError:
            return False

        if len(branch) != self.branch_size:
            return False

        return True

    def account(self, account):

        if '-' not in account:
            try:
                int(account)
            except ValueError:
                return False
        else:
            return False

        if len(account) != self.account_size:
            return False

        return True

    def number(self, account):
        return self.account(account)

    def dac(self, dac):

        try:
            int(dac)
        except ValueError:
            return False

        if len(dac) != self.dac_size:
            return False

        return True

    def password(self, pwd):
        try:
            int(pwd)
        except ValueError:
            return False

        if len(pwd) != self.password_size:
            return False

        return True


class BancoDoBrasilValidator(BankValidator):

    branch_size = 5
    account_size = 5
    password_size = 8

    allowed_days = [30]

    fields = ['branch', 'number', 'password']


class ItauValidator(BankValidator):

    branch_size = 4
    account_size = 5
    dac_size = 1
    password_size = 6

    allowed_days = [7, 15, 30, 60, 90]

    fields = ['branch', 'number', 'dac', 'password']


class SantanderValidator(DocumentValidator):

    fields = ['cpf:document', 'password']

    allowed_days = [60]

    def password(self, pwd):
        return True


class TicketValidator(CardValidator):

    # TODO: Determine Ticket BINs
    bin_list = []
    allowed_days = [30]

    fields = ['restaurante:card', 'bin_check:card']

    def restaurante(self, card):
        return self.card(card, 16)


class AleloValidator(CardValidator, DocumentValidator):

    # TODO: Determine Alelo BINs
    bin_list = []

    allowed_days = range(1, 181)

    fields = ['cpf:document', 'password', 'refeicao:card', 'bin_check:card']

    def refeicao(self, card):
        if self.card(card, 16):
            return True
        elif self.card(card, 4):
            return True
        else:
            return False

    def password(self, pwd):
        return True


class SodexoValidator(CardValidator, DocumentValidator):

    # TODO: Determine Sodexo BINs
    bin_list = []

    allowed_days = [30]

    fields = ['cpf:document', 'refeicao:card', 'bin_check:card']

    def refeicao(self, card):
        return self.card(card, 16)
