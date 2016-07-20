from distutils.core import setup
setup(
  name = 'bankscraper',
  packages = ['bankscraper'], # this must be the same as the name above
  version = '0.1',
  description = 'Script suite to parse financial transactions from brazilian bank and benefit accounts, including support (when applicable) for interest fees and overdraft limits, besides account metadata and account holder information, when available',
  author = 'Kamus Hadenes',
  author_email = 'kamushadenes@hyadesinc.com',
  url = 'https://github.com/kamushadenes/bankscraper', # use the URL to the github repo
  download_url = 'https://github.com/kamushadenes/bankscraper/tarball/0.1', # I'll explain this in a second
  keywords = ['bank', 'scraper', 'financial', 'automation', 'itau', 'santander', 'banco do brasil', 'sodexo', 'alelo'], # arbitrary keywords
  classifiers = [],
)
