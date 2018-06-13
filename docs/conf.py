import os
import sys
import datetime as dt

sys.path.insert(0, os.path.abspath('..'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
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

html_theme_options = {
    'description': 'Build and document REST APIs with aiohttp and apispec',
    'show_powered_by': False,
}
html_title = 'aiohttp-apispec Documentation'
html_short_title = 'aiohttp-apispec'
