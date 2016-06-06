# bankscrapper
Brazilian Bank Scrapping Tool

## Current Supported Banks


| Name   | Balance | Transactions | Additional Info                                                           |
| ---    | ---     | ---          | ---                                                                       |
| ![Itaú](https://raw.githubusercontent.com/kamushadenes/bankscrapper/master/logo/icon-itau.png) | Yes     | 90 days      | Account Segment, Account Type, Owner Name, Owner Document, Owner Birthday |
| ![Sodexo](https://raw.githubusercontent.com/kamushadenes/bankscrapper/master/logo/icon-sodexo.png) | Yes     | 20 days      | Card Type, Card Status, Company Name, Owner Name                          |


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
