import re
import sys
from setuptools import setup, find_packages

with open("LICENSE") as f:
    LICENSE = f.read()

setup(
    name='vaultenv',
    version='0.0.1',
    author='Joakim Uddholm',
    author_email='tethik@gmail.com',
    description='Commandline Interface to load .env from vault',
    url='https://github.com/Tethik/vaultenv',
    py_modules=['vaultenv'],
    entry_points = {
        'console_scripts': ['vaultenv=vaultenv:main'],
    },
    zip_safe=True,
    package_data={'': ['LICENSE', 'README.md']},
    include_package_data=True,
    install_requires=[
        "click",
        "click_default_group",
        "hvac",
        "colorama",
        "python-dotenv==0.7.1",
        "pyyaml"
    ],
    license=LICENSE,
    classifiers=[
        'Development Status :: 3 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT',        
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python',
    ]
)