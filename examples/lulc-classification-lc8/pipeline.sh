#!/bin/bash

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
