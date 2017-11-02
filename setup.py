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
        "hvac",
        "colorama",
        "python-dotenv",
        "pyyaml"
    ],
    license=LICENSE,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python',
    ]
)