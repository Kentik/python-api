from setuptools import setup, find_packages

setup(
    name='kentikapi',
    version='0.2.0',
    author='Blake Caldwell',
    packages=find_packages(),
    url='https://github.com/kentik/api-client',
    license='LICENSE.txt',
    description='Kentik API Client',
    long_description=open('README.md').read(),
    install_requires=['requests'],
)
