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
export BDC_ACCESS_KEY=""

#
# 1. Extract the time series from the data cube
#
bdcrrm-cli production make Rscript analysis/01_extract_ts.R

#
# 2. Train the classification model
#
bdcrrm-cli production make Rscript analysis/02_training_model.R

#
# 3. Classify the data cube
#
bdcrrm-cli production make Rscript analysis/03_classify.R
