#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management API is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Management CLI."""

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

visual_require = [
    'asciidag>=0.2.0',
    'cairocffi>=1.2.0',
    'rich>=10.7.0'
]

docker_unpacker = [
    'reprounzip-docker>=1.1',
]

extras_require = {
    'docs': docs_require,
    'examples': examples_require,
    'tests': tests_require,
    'visual': visual_require,
    'docker-unpacker': docker_unpacker
}

extras_require['all'] = [req for _, reqs in extras_require.items() for req in reqs]

setup_requires = [
    'pytest-runner>=5.2',
]

install_requires = [
    'Click>=7.0',
    'dictdiffer>=0.8.1',
    'py-multihash>=2.0.1',
    'python-igraph>=0.9.6',
    'rpaths>=1.0.0',
    'reprozip>=1.1',
    'reprounzip>=1.1',
    'bagit>=1.8.1',
    'yamlize>=0.7.0',
    'cookiecutter>=1.7.3',
    'plumbum>=1.7.0',
    'ruamel.yaml>=0.17.10',
    'docker>=5.0.0',
    'pandas>=1.3.1',
    'paradag>=1.2.0',
]

packages = find_packages()

g = {}
with open(os.path.join('bdcrrm_api', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='bdcrrm_api',
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
        'Repository': 'https://github.com/brazil-data-cube/bdcrrm-api',
        'Issues': 'https://github.com/brazil-data-cube/bdcrrm-api/issues',
        'Documentation': 'https://bdcrrm_api.readthedocs.io/en/latest/'
    },
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'console_scripts': [
            'bdcrrm-cli = bdcrrm_api.cli.cli:bdcrrm_cli'
        ]
    },
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
