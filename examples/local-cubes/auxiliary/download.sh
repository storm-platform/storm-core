#!/bin/bash
#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management API is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

#
# General definitions
#
export DATAFILES_URL="https://uni-muenster.sciebo.de/s/e5yUZmYGX0bo4u9/download"

#
# Preparing the environment for the example
#
mkdir -p lc8_scenes/zip/
mkdir -p lc8_scenes/uncompress/

# 1. Download
wget ${DATAFILES_URL} -O lc8_scenes/zip/L8_Amazon.zip

# 2. Unzip the files
unzip lc8_scenes/zip/L8_Amazon.zip -d lc8_scenes/uncompress/L8_Amazon

# 3. Remove raw file
rm lc8_scenes/zip/L8_Amazon.zip
