#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Temporal water mask library."""

from setuptools import find_packages, setup

install_requires = [
    'joblib==1.0.1',
    'rasterio==1.2.6',
    'fire==0.4.0',
    'stac.py==0.9.0.post13'
]

packages = find_packages()

version = open('VERSION', 'r').read().strip()

setup(
    name='rr_water_mask',
    version=version,
    description='Package for generate temporal water masks using CBERS-4/AWFI Data Cubes',
    license='MIT',
    author='Felipe Menino Carlos',
    author_email='felipe.carlos@inpe.br',
    packages=packages,
    platforms='any',
    install_requires=install_requires,
    classifiers=[
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
