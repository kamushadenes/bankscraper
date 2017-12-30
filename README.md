# bankscraper

Script suite to parse financial transactions from brazilian bank and benefit accounts, including support (when applicable) for interest fees and overdraft limits, besides account metadata and account holder information, when available

**WARNING:** Using this tool without care may lead to your bank account being blocked. Use at your own risk!

## Current Supported Banks

The banks below were added in the order they are listed


| Name                                                                                                                                                                                          | Balance | Transaction Backlog in Days           | Additional Info                                                                                       | Method                               | Status |
| ---                                                                                                                                                                                           | ---     | ---                                   | ---                                                                                                   | ---                                  | ---    |
| [![Itaú](https://raw.githubusercontent.com/kamushadenes/bankscraper/master/bankscraper/logo/icon-itau.png)](https://github.com/kamushadenes/bankscraper/blob/master/itau.py)                              | Yes     | 7, 15, 30, 60, 90                     | Account Segment, Account Type, Owner Name, Owner Document, Owner Birthday, Overdraft                  | Reversed Mobile API                  | OK     |
| [![Sodexo](https://raw.githubusercontent.com/kamushadenes/bankscraper/master/bankscraper/logo/icon-sodexo.png)](https://github.com/kamushadenes/bankscraper/blob/master/sodexo.py)                        | Yes     | 30                                    | Card Type, Card Status, Company Name, Owner Name                                                      | Reversed Mobile API                  | OK     |
| [![Banco do Brasil](https://raw.githubusercontent.com/kamushadenes/bankscraper/master/bankscraper/logo/icon-bancodobrasil.png)](https://github.com/kamushadenes/bankscraper/blob/master/bancodobrasil.py) | Yes     | 30                                    | Account Type, Owner Name, Interest                                                                    | Reversed Mobile API                  | OK     |
| [![Ticket](https://raw.githubusercontent.com/kamushadenes/bankscraper/master/bankscraper/logo/icon-ticket.png)](https://github.com/kamushadenes/bankscraper/blob/master/ticket.py)                        | Yes     | 30                                    | -                                                                                                     | Web Scraping with Captcha Bypass     | OK     |
| [![Nubank](https://raw.githubusercontent.com/kamushadenes/bankscraper/master/bankscraper/logo/icon-nubank.png)](https://github.com/kamushadenes/bankscraper/blob/master/nubank.py)                        | No      | -                                     | Incomplete - Not working at all                                                                       | -                                    | NOK    |
| [![Santander](https://raw.githubusercontent.com/kamushadenes/bankscraper/master/bankscraper/logo/icon-santander.png)](https://github.com/kamushadenes/bankscraper/blob/master/santander.py)               | Yes     | 60                                    | Account Branch, Account Number, Account Dac, Owner Name, Owner Document, Overdraft, Personal Credit   | Selenium                             | OK     |
| [![Alelo](https://raw.githubusercontent.com/kamushadenes/bankscraper/master/bankscraper/logo/icon-alelo.png)](https://github.com/kamushadenes/bankscraper/blob/master/alelo.py)                           | Yes     | 1-180                                 | Owner First Name                                                                                      | Selenium                             | OK     |



## Usage

### Itaú
<pre><code>
usage: itau.py [-h] --branch BRANCH --account ACCOUNT --password PASSWORD
               [--days DAYS] [--omit-sensitive-data] [--balance] [--quiet]

Program to parse financial transactions from Itaú

optional arguments:
  -h, --help            show this help message and exit
  --branch BRANCH       Itaú Branch number, in the format 0000
  --account ACCOUNT     Itaú Account number, in the format 00000-0
  --password PASSWORD   Itaú Account password
  --days DAYS           Transaction log days
  --omit-sensitive-data
                        Omit sensitive data, like documents, paychecks and
                        current balance
  --balance             Get only account balance
  --quiet               Be quiet
</code></pre>

### Sodexo
<pre><code>
usage: sodexo.py [-h] --card CARD --document DOCUMENT [--omit-sensitive-data]
                 [--balance] [--quiet]

Program to parse financial transactions from Sodexo benefit

optional arguments:
  -h, --help            show this help message and exit
  --card CARD           Sodexo Card Number
  --document DOCUMENT   Sodexo Card Owner Document
  --omit-sensitive-data
                        Omit sensitive data, like documents, paychecks and
                        current balance
  --balance             Get only account balance
  --quiet               Be quiet
</code></pre>

### Banco do Brasil
<pre><code>
usage: bancodobrasil.py [-h] --branch BRANCH --account ACCOUNT --password
                        PASSWORD [--days DAYS] [--omit-sensitive-data]
                        [--balance] [--quiet]

Program to parse financial transactions from Banco do Brasil

optional arguments:
  -h, --help            show this help message and exit
  --branch BRANCH       Banco do Brasil Branch number, in the format 00000
  --account ACCOUNT     Banco do Brasil Account number, in the format 000000
  --password PASSWORD   Banco do Brasil Account password
  --days DAYS           Transaction log days
  --omit-sensitive-data
                        Omit sensitive data, like documents, paychecks and
                        current balance
  --balance             Get only account balance
  --quiet               Be quiet
</code></pre>

### Ticket
<pre><code>
usage: ticket.py [-h] --card CARD [--omit-sensitive-data] [--balance]
                 [--quiet]

Program to parse financial transactions from Ticket benefit

optional arguments:
  -h, --help            show this help message and exit
  --card CARD           Ticket Card Number
  --omit-sensitive-data
                        Omit sensitive data, like documents, paychecks and
                        current balance
  --balance             Get only account balance
  --quiet               Be quiet
</code></pre>

### Santander
<pre><code>
usage: santander.py [-h] --document DOCUMENT --password PASSWORD [--days DAYS]
                    [--omit-sensitive-data] [--balance] [--quiet]

Program to parse financial transactions from Santander

optional arguments:
  -h, --help            show this help message and exit
  --document DOCUMENT   Santander Account Owner Document
  --password PASSWORD   Santander Account password
  --days DAYS           Transaction log days
  --omit-sensitive-data
                        Omit sensitive data, like documents, paychecks and
                        current balance
  --balance             Get only account balance
  --quiet               Be quiet
</code></pre>

### Alelo
<pre><code>
usage: alelo.py [-h] --document DOCUMENT --password PASSWORD --card CARD
                [--days DAYS] [--omit-sensitive-data] [--balance] [--quiet]

Program to parse financial transactions from Alelo

optional arguments:
  -h, --help            show this help message and exit
  --document DOCUMENT   Alelo Account Owner Document
  --password PASSWORD   Alelo Account password
  --card CARD           Alelo Card Number password
  --days DAYS           Transaction log days
  --omit-sensitive-data
                        Omit sensitive data, like documents, paychecks and
                        current balance
  --balance             Get only account balance
  --quiet               Be quiet
</code></pre>
