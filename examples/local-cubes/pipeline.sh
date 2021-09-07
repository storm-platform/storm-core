#!/bin/bash
#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management API is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

#
# 1. Download the input data
#
./auxiliary/download.sh

mv lc8_scenes/uncompress/L8_Amazon data/raw_data/L8_Amazon

#
# 2. Processing the Landsat-8 data cube using gdalcubes
#
bdcrrm-cli production make papermill analysis/local-cube.ipynb data/derived_data/local-cube-result.ipynb
