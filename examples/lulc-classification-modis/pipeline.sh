#!/bin/bash

#
# General definitions
#
export BDC_ACCESS_KEY=""
export SITS_USER_CONFIG_FILE="${PWD}/config/sits_config.yml"

#
# 1. Extract Time Series
#
bdcrrm-cli production make Rscript analysis/01_extract-ts.R

#
# 2. Train the classifier
#
bdcrrm-cli production make Rscript analysis/02_training_model.R

#
# 3. Classify a supercube
#
start=1
end=16 # number of temporal groups

for ((i = $start; i <= $end; i++)); do
    bdcrrm-cli production make Rscript analysis/03_classify.R $i
done
