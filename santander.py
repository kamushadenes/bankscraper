from bankscraper import BankScraper, AnotherActiveSessionException, MaintenanceException, GeneralException, Account, Transaction, Owner, App
from decimal import Decimal

from datetime import datetime

import traceback

import argparse

from time import sleep

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


from bs4 import BeautifulSoup as bs


class Santander(object):

    api_endpoint = 'https://www.santandernet.com.br/'

    first_page_url = 'https://www.santander.com.br/'

    logout_url_1 = 'https://www.santandernet.com.br/IBPF_Logout.asp'
    logout_url_2 = 'https://www.santandernet.com.br/logout.asp'
    login_url1 = 'https://www.santandernet.com.br/'
    login_url2 = 'https://www.santandernet.com.br/IBPF/NMSDLoginAsIs.asp'

    def __init__(self, document, password, days=15, omit_sensitive_data=False, quiet=False):
        if not quiet:
            print('[*] Santander Parser is starting...')

        self.account = Account(document=str(document), password=str(password))
        self.account.bank = 'Santander'
        self.account.currency = 'R$'

        self.omit_sensitive_data = omit_sensitive_data
        self.quiet = quiet

        self.balance = False

        self.transaction_days = days

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
            self.session.get(self.first_page_url)

            #elem = self.session.find_element_by_name('txtCPF')
            elem = self.wait.until(EC.visibility_of_element_located((By.NAME, 'txtCPF')))
            elem.send_keys(self.account.document)
            elem.send_keys(Keys.ENTER)

            sleep(3)


            self.session.switch_to.frame(self.wait.until(EC.visibility_of_element_located((By.NAME, 'Principal'))))
            self.session.switch_to.frame(self.wait.until(EC.visibility_of_element_located((By.NAME, 'MainFrame'))))

            if 'iframeContrato' in self.session.page_source:
                print('[-] You need to manually accept an usage agreement')
                exit(1)

            #elem = self.session.find_element_by_id('txtSenha')
            elem = self.wait.until(EC.visibility_of_element_located((By.ID, 'txtSenha')))
            elem.send_keys(self.account.password)
            elem.send_keys(Keys.ENTER)

            self.session.switch_to.default_content()
            self.session.switch_to.frame(self.wait.until(EC.visibility_of_element_located((By.NAME, 'Principal'))))
            self.session.switch_to.frame(self.wait.until(EC.visibility_of_element_located((By.NAME, 'Corpo'))))

            ola = self.session.find_element_by_id('ola')

            soup = bs(ola.get_attribute('innerHTML'))

            table = soup.find('table')

            self.account.owner = Owner(table.find_all('td')[0].find('strong').text.strip())
            self.account.owner.document = self.account.document

            self.account.branch = table.find_all('td')[1].text.split()[1]
            self.account.number = ''.join(table.find_all('td')[1].text.split()[3].split('.')[:2])
            self.account.dac = table.find_all('td')[1].text.split()[3].split('.')[-1]

            self.account.print_info()
            self.account.owner.print_info()
        except UnexpectedAlertPresentException:
            print('[-] Login failed, invalid credentials')
            exit(1)
        except Exception:
            traceback.print_exc()
            self.session.save_screenshot('/tmp/screenie.png')
            exit(1)

    def logout(self):

        self.session.switch_to.default_content()

        self.session.get(self.logout_url_1)
        self.session.get(self.logout_url_2)

    def get_balance(self):
        # All on the same page
        self.balance = True
        self.get_transactions()

    def get_transactions(self):
        if not self.quiet:
            print('[*] Getting transactions...')

        self.session.switch_to.frame(self.session.find_element_by_name('iframePainel'))

        elem = self.session.find_element_by_id('extrato')

        select = Select(elem.find_element_by_name('cboSelectPeriodoExtrato'))

        select.select_by_value(self.transaction_days)

        elem.find_element_by_class_name('botao').click()

        self.session.switch_to.default_content()
        self.session.switch_to.frame(self.wait.until(EC.visibility_of_element_located((By.NAME, 'Principal'))))
        self.session.switch_to.frame(self.wait.until(EC.visibility_of_element_located((By.NAME, 'Corpo'))))
        self.session.switch_to.frame(self.wait.until(EC.visibility_of_element_located((By.NAME, 'iframePrinc'))))
        self.session.switch_to.frame(self.wait.until(EC.visibility_of_element_located((By.ID, 'extrato'))))

        elem = self.session.find_elements_by_class_name('lista')

        soup = bs(elem[0].get_attribute('innerHTML'))

        if not self.balance:
            transactions = self.parse_transactions(soup.find_all('tr'))

            if not self.quiet:
                for trans in transactions:
                    trans.print_info()

        soup = bs(elem[1].get_attribute('innerHTML'))

        for tr in soup.find_all('tr'):
            if tr.find_all('td')[0].text.strip() == 'A - Saldo de ContaMax':
                self.account.balance = Decimal(tr.find_all('td')[1].text.strip().replace('-', '').replace('.', '').replace(',', '.'))
                self.account.sign = '-' if '-' in tr.find_all('td')[1].text.strip() else '+'
            elif tr.find_all('td')[0].text.strip().startswith('D -'):
                self.account.overdraft = Decimal(tr.find_all('td')[1].text.strip().replace('-', '').replace('.', '').replace(',', '.'))

        self.session.switch_to.default_content()
        self.session.switch_to.frame(self.wait.until(EC.visibility_of_element_located((By.NAME, 'Principal'))))
        self.session.switch_to.frame(self.wait.until(EC.visibility_of_element_located((By.NAME, 'Corpo'))))
        self.session.switch_to.frame(self.wait.until(EC.visibility_of_element_located((By.ID, 'ifr_sal'))))

        elem = self.session.find_element_by_id('tblSaldos')

        soup = bs(elem.get_attribute('innerHTML'))

        t = soup.find('div', {'id': 'CPVendedora'})

        self.account.personal_credit = Decimal(t.find_all('td')[1].text.strip().replace('-', '').replace('.', '').replace(',', '.'))

    def parse_transactions(self, transactions):

        for tr in transactions:
            if tr.find('th'):
                continue
            description = tr.find_all('td')[2].text.strip()
            if description.startswith('SALDO'):
                continue
            t = Transaction(description)
            t.date = datetime.strptime(tr.find_all('td')[0].text.strip(), '%d/%m/%Y')
            t.id = tr.find_all('td')[3].text.strip()

            v = tr.find_all('td')[5].text.strip()

            t.sign = '-' if '-' in v else '+'
            t.value = Decimal(v.replace('-', '').replace('.', '').replace(',', '.'))

            self.account.transactions.append(t)

        return self.account.transactions

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Program to parse financial transactions from Santander')
    parser.add_argument('--document', help='Santander Account Owner Document', required=True)
    parser.add_argument('--password', help='Santander Account password', required=True)
    parser.add_argument('--days', help='Transaction log days', default=60, type=int)
    parser.add_argument('--omit-sensitive-data', dest='omit', action='store_true', help='Omit sensitive data, like documents, paychecks and current balance')
    parser.add_argument('--balance', dest='balance', action='store_true', help='Get only account balance')
    parser.add_argument('--quiet', dest='quiet', action='store_true', help='Be quiet')

    args = parser.parse_args()

    santander = Santander(args.document, args.password, args.days, args.omit, args.quiet)
    try:
        santander.login()
        if args.balance:
            santander.get_balance()
        else:
            santander.get_transactions()
    except Exception as e:
        traceback.print_exc()
        exit(1)
    finally:
        santander.logout()
        santander.session.close()
