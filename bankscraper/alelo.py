from bankscraper import BankScraper, Account, Transaction, Owner
from decimal import Decimal
from validators import AleloValidator
from datetime import datetime, date, timedelta

import traceback

import argparse

from time import sleep

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

from bs4 import BeautifulSoup as bs


class Alelo(BankScraper):

    api_endpoint = 'https://www.meualelo.com.br/'

    login_url = 'https://www.meualelo.com.br/'

    def __init__(self, document, password, card, days=15, omit_sensitive_data=False, quiet=False, validator=AleloValidator):
        if not quiet:
            print('[*] Alelo Parser is starting...')

        self.validator = validator()

        self.account = Account(document=document, password=password, card=card, account_type='card')

        self.validate()

        self.account.bank = 'Alelo'
        self.account.currency = 'R$'

        self.omit_sensitive_data = omit_sensitive_data
        self.quiet = quiet

        self.balance = False

        self.transaction_days = days

        self.first_date = (date.today() - timedelta(days=self.transaction_days)).strftime('%d/%m/%Y')

        webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.settings.userAgent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36'
        webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.Accept-Language'] = 'pt-BR'
        webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.Connection'] = 'keep-alive'

        self.session = webdriver.PhantomJS()
        self.session.implicitly_wait(10)
        self.session.set_window_size(1920, 1080)

        self.wait = WebDriverWait(self.session, 10)

    def login(self):
        if not self.quiet:
            print('[*] Logging in as {}'.format(self.account.document))

        try:
            self.session.get(self.login_url)

            elem = self.wait.until(EC.visibility_of_element_located((By.ID, 'cpf')))
            elem.send_keys(self.account.document)
            elem.send_keys(Keys.ENTER)

            elem = self.wait.until(EC.visibility_of_element_located((By.ID, 'password')))
            elem.send_keys(self.account.password)

            for b in self.session.find_elements_by_class_name('botao'):
                if b.get_attribute('data-bind'):
                    if 'userAuthentication' in b.get_attribute('data-bind'):
                        b.click()
                        break
        except Exception:
            traceback.print_exc()
            exit(1)

    def logout(self):

        self.session.find_element_by_class_name('usuario-logado__sair').click()

    def get_balance(self):
        # All on the same page
        self.balance = True
        self.get_transactions()

    def get_transactions(self):
        if not self.quiet:
            print('[*] Getting transactions...')

        while True:
            try:
                elem = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'container')))

                self.account.owner = Owner(self.session.find_element_by_class_name('usuario-logado__cumprimento').find_element_by_tag_name('span').get_attribute('innerHTML').strip())

                elem = elem.find_element_by_class_name('menu')
                elem = elem.find_element_by_class_name('menu__container')
                elem = elem.find_element_by_class_name('menu__lista')
                elem = elem.find_element_by_class_name('lista__item')

                hover = ActionChains(self.session).move_to_element(elem)
                hover.perform()

                sleep(0.5)

                for a in elem.find_elements_by_tag_name('a'):
                    if self.account.card[-4:] in a.get_attribute('innerHTML'):
                        a.click()
                        break
                break
            except StaleElementReferenceException:
                continue

        elem = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'saldo__info')))

        self.account.balance = Decimal(elem.find_element_by_class_name('info__valor').get_attribute('innerHTML').split()[-1].replace('.', '').replace(',', '.'))
        elem = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'mob__botao_1')))

        if not self.balance:

            elem.click()

            while True:
                try:
                    elem = self.session.find_element_by_id('extratoFilterPeriod')
                    elem.click()

                    elem = self.session.find_element_by_id('filtroDataInicial')
                    elem.send_keys(self.first_date)

                    elem = self.session.find_element_by_id('filtroDataFinal')
                    elem.send_keys(date.today().strftime('%d/%m/%Y'))

                    elem = self.session.find_element_by_id('modalFiltroData')
                    elem = elem.find_element_by_tag_name('button')
                    elem.click()

                    break

                except StaleElementReferenceException:
                    continue

            max_retry = 5
            retries = 0

            sleep(5)
            while retries <= max_retry:
                elem = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'movimentacao__extrato')))

                soup = bs(elem.get_attribute('innerHTML'))

                transactions = self.parse_transactions(soup.find_all('li'))

                if len(transactions) == 0:
                    retries += 1
                    sleep(1)
                    continue
                else:
                    if not self.quiet:
                        for trans in transactions:
                            trans.print_info()
                    break

            if retries == max_retry:
                print('[-] Could not get transactions')
                return

    def parse_transactions(self, transactions):

        for li in transactions:
            try:
                t = Transaction(li.find('div', {'class': 'item__cell--descricao'}).text.strip())
                t.date = datetime.strptime(li.find('div', {'class': 'item__cell--data'}).text.strip(), '%d/%m/%Y')
                t.value = Decimal(li.find('div', {'class': 'item__cell--valor'}).text.split()[-1].replace('.', '').replace(',', '.'))
                t.sign = '+' if '+' in li.find('div', {'class': 'item__cell--valor'}).text else '-'

                self.account.transactions.append(t)
            except:
                traceback.print_exc()
                continue

        return self.account.transactions

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Program to parse financial transactions from Alelo')
    parser.add_argument('--document', help='Alelo Account Owner Document', required=True)
    parser.add_argument('--password', help='Alelo Account password', required=True)
    parser.add_argument('--card', help='Alelo Card Number password', required=True)
    parser.add_argument('--days', help='Transaction log days', default=60, type=int)
    parser.add_argument('--omit-sensitive-data', dest='omit', action='store_true', help='Omit sensitive data, like documents, paychecks and current balance')
    parser.add_argument('--balance', dest='balance', action='store_true', help='Get only account balance')
    parser.add_argument('--quiet', dest='quiet', action='store_true', help='Be quiet')

    args = parser.parse_args()

    alelo = Alelo(args.document, args.password, args.card, args.days, args.omit, args.quiet)
    try:
        alelo.login()
        if args.balance:
            alelo.get_balance()
        else:
            alelo.get_transactions()
    except Exception as e:
        traceback.print_exc()
        exit(1)
    finally:
        alelo.logout()
        alelo.session.close()
