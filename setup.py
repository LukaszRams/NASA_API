#!/usr/bin/python
# -*- coding: utf-8 -*-
from setuptools import setup
import py2exe

setup(
    name="NASA_Api",
    version="1.0.0",
    author="Łukasz Rams",
    install_requires=[
        'certifi==2021.10.8',
        'charset-normalizer==2.0.9',
        'idna==3.3',
        'Pillow==8.4.0',
        'requests==2.26.0',
        'urllib3==1.26.7',
    ],
    service=['main'])
