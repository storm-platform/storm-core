#!/usr/bin/env bash
#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management API is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

pydocstyle bdcrrm_api examples tests setup.py && \
isort bdcrrm_api examples tests setup.py --check-only --diff && \
check-manifest --ignore ".travis.yml,.drone.yml,.readthedocs.yml" && \
sphinx-build -qnW --color -b doctest docs/sphinx/ docs/sphinx/_build/doctest && \
pytest
