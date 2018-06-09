import os
import sys
import datetime as dt

sys.path.insert(0, os.path.abspath('..'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx_issues',
]

project = 'aiohttp-apispec'
author = 'Maksim Danilchenko'
copyright = 'Maksim Danilchenko and contributors {0:%Y}'.format(dt.datetime.utcnow())
version = '0.3.2'
source_suffix = '.rst'
master_doc = 'index'
pygments_style = 'sphinx'
html_theme = 'alabaster'
html_static_path = ['_static']
issues_github_path = 'maximdanilchenko/aiohttp-apispec'
