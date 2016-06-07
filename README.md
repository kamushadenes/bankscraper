# bankscrapper
Brazilian Bank Scrapping Tool

## Current Supported Banks


| Name   | Balance | Transactions History | Additional Info                                                           |
| ---    | ---     | ---          | ---                                                                       |
| ![Itaú](https://raw.githubusercontent.com/kamushadenes/bankscrapper/master/logo/icon-itau.png) | Yes     | 90 days      | Account Segment, Account Type, Owner Name, Owner Document, Owner Birthday |
| ![Sodexo](https://raw.githubusercontent.com/kamushadenes/bankscrapper/master/logo/icon-sodexo.png) | Yes     | 20 days      | Card Type, Card Status, Company Name, Owner Name                          |
| ![Banco do Brasil](https://raw.githubusercontent.com/kamushadenes/bankscrapper/master/logo/icon-bancodobrasil.png) | Yes     | 30 days      | Accout Type, Owner Name  |


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
