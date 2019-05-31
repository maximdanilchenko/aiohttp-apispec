import datetime as dt
import os
import sys

sys.path.insert(0, os.path.abspath('..'))

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx', 'sphinx.ext.viewcode']

project = 'aiohttp-apispec'
author = 'Maksim Danilchenko'
copyright = 'Maksim Danilchenko and contributors {0:%Y}'.format(dt.datetime.utcnow())
version = '0.3.2'
source_suffix = '.rst'
master_doc = 'index'
pygments_style = 'default'
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

html_theme_options = {
    'description': 'Build and document REST APIs with aiohttp and apispec',
    'show_powered_by': False,
    'display_version': True,
}
html_title = 'aiohttp-apispec Documentation'
html_short_title = 'aiohttp-apispec'
