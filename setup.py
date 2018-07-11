from setuptools import find_packages
from setuptools import setup


def readme(fname):
    """ Return readme file starting after <start_line> until <start_line> """
    start_line = '<p>\n'
    start_flag = False
    result = []
    with open(fname) as fp:
        for line in fp.readlines():
            if line == start_line:
                start_flag = not start_flag
            elif start_flag:
                result.append(line)
    return ''.join(result)


setup(
    name='aiohttp-apispec',
    version='0.5.1',
    description='Build and document REST APIs with aiohttp and apispec',
    long_description=readme('README.md'),
    author='Danilchenko Maksim',
    author_email='dmax.dev@gmail.com',
    packages=find_packages(exclude=('test*',)),
    package_dir={'aiohttp_apispec': 'aiohttp_apispec'},
    include_package_data=True,
    install_requires=['aiohttp', 'apispec<=0.38.0', 'webargs'],
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
    ],
    test_suite='tests',
)
