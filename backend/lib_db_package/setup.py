from setuptools import setup, find_packages

setup(
    name='lib_db',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pymongo', 'requests'
    ],
)
