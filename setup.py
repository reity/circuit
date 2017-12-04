from setuptools import setup

setup(
    name             = 'circuit',
    version          = '0.0.0.2',
    packages         = ['circuit',],
    install_requires = [],
    license          = 'MIT',
    url              = 'https://github.com/lapets/circuit',
    author           = 'Andrei Lapets',
    author_email     = 'a@lapets.io',
    description      = 'Minimal pure Python library for building and working with circuit graphs/expressions.',
    long_description = open('README.rst').read(),
    test_suite       = 'nose.collector',
    tests_require    = ['nose'],
)
