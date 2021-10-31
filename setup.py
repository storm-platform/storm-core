#
# This file is part of SpatioTemporal Open Research Manager Core.
# Copyright (C) 2021 INPE.
#
# SpatioTemporal Open Research Manager Core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""SpatioTemporal Open Research Manager Core."""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()

history = open('CHANGES.rst').read()

docs_require = [
    'Sphinx>=2.2',
    'sphinx_rtd_theme',
    'sphinx-copybutton',
]

tests_require = [
    'coverage>=4.5',
    'coveralls>=1.8',
    'pytest>=5.2',
    'pytest-cov>=2.8',
    'pytest-pep8>=1.0',
    'pydocstyle>=4.0',
    'isort>4.3',
    'check-manifest>=0.40',
]

examples_require = [
]

cli_require = [
    'asciidag>=0.2.0',
    'cairocffi>=1.2.0',
    'rich>=10.7.0',
    'Click>=7.0',
]

extras_require = {
    'docs': docs_require,
    'examples': examples_require,
    'tests': tests_require,
    'cli': cli_require
}

extras_require['all'] = [req for _, reqs in extras_require.items() for req in reqs]

setup_requires = [
    'pytest-runner>=5.2',
]

processing_dependencies = [
    'paradag>=1.2.0',
]

graph_dependencies = [
    'python-igraph>=0.9.6',
]

environment_dependencies = [
    'reprozip>=1.1',
    'reprounzip>=1.1',
    'reprounzip-docker>=1.1',
]

base_dependencies = [
    'dictdiffer>=0.8.1',
    'py-multihash>=2.0.1',
    'pandas>=1.3.1',
    'docker>=5.0.0',
    'ruamel.yaml>=0.17.10',
    'plumbum>=1.7.0',
    'cookiecutter>=1.7.3',
    'bagit>=1.8.1',
    'rpaths>=1.0.0',
    'yamlize>=0.7.0',
    'base32-lib>=1.0.2'
]

install_requires = [*base_dependencies, *processing_dependencies, *graph_dependencies, *environment_dependencies]

packages = find_packages()

g = {}
with open(os.path.join('storm_core', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='storm_core',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/x-rst',
    keywords=['Time series', 'Earth Observations'],
    license='MIT',
    author='Brazil Data Cube Team',
    author_email='brazildatacube@inpe.br',
    url='https://github.com/brazil-data-cube/bdcrrm-api',
    project_urls={
        'Repository': 'https://github.com/brazil-data-cube/storm-core',
        'Issues': 'https://github.com/brazil-data-cube/storm-core/issues',
        'Documentation': 'https://storm-core.readthedocs.io/en/latest/'
    },
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: GIS',
    ],
)
