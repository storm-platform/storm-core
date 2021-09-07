#!/bin/bash
#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management API is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

cd ../../
docker build -t "bdcrrm/lulc-classification-lc8:latest" \
  -f examples/lulc-classification-lc8/Dockerfile .
