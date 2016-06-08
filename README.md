# bankscraper

Script suite to parse financial transactions from brazilian bank and benefit accounts, including support (when applicable) for interest fees and overdraft limits, besides account metadata and account holder information, when available

## Current Supported Banks

The banks below were added in the order they are listed


| Name                                                                                                                                                                                          | Balance | Transaction History | Additional Info                                                                      | Method                               |
| ---                                                                                                                                                                                           | ---     | ---                 | ---                                                                                  | ---                                  |
| [![Itaú](https://raw.githubusercontent.com/kamushadenes/bankscraper/master/logo/icon-itau.png)](https://github.com/kamushadenes/bankscraper/blob/master/itau.py)                              | Yes     | 90 days             | Account Segment, Account Type, Owner Name, Owner Document, Owner Birthday, Overdraft | Reversed Mobile API                  |
| [![Sodexo](https://raw.githubusercontent.com/kamushadenes/bankscraper/master/logo/icon-sodexo.png)](https://github.com/kamushadenes/bankscraper/blob/master/sodexo.py)                        | Yes     | 20 days             | Card Type, Card Status, Company Name, Owner Name                                     | Reversed Mobile API                  |
| [![Banco do Brasil](https://raw.githubusercontent.com/kamushadenes/bankscraper/master/logo/icon-bancodobrasil.png)](https://github.com/kamushadenes/bankscraper/blob/master/bancodobrasil.py) | Yes     | 30 days             | Account Type, Owner Name, Interest                                                   | Reversed Mobile API                  |
| [![Ticket](https://raw.githubusercontent.com/kamushadenes/bankscraper/master/logo/icon-ticket.png)](https://github.com/kamushadenes/bankscraper/blob/master/ticket.py)                        | Yes     | 30 days             | -                                                                                    | Website Scraping with Captcha Bypass |


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
  --branch BRANCH       Banco do Brasil Branch number, in the format 0000-0
  --account ACCOUNT     Banco do Brasil Account number, in the format 0000-0
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
