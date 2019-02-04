from setuptools import find_packages
from setuptools import setup

REQUIRES = ['aiohttp>=3.0.1', 'apispec', 'webargs']


def readme(fname):
    with open(fname) as fp:
        content = fp.read()
    return content


setup(
    name='aiohttp-apispec',
    version='0.8.0',
    description='Build and document REST APIs with aiohttp and apispec',
    long_description=readme('README.md'),
    long_description_content_type="text/markdown",
    author='Danilchenko Maksim',
    author_email='dmax.dev@gmail.com',
    packages=find_packages(exclude=('test*',)),
    package_dir={'aiohttp_apispec': 'aiohttp_apispec'},
    include_package_data=True,
    install_requires=REQUIRES,
    license='MIT',
    url='https://github.com/maximdanilchenko/aiohttp-apispec',
    zip_safe=False,
    keywords='aiohttp marshmallow apispec swagger',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    test_suite='tests',
)
