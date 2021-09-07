#!/bin/bash
#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

#
# General definitions
#
export BDC_ACCESS_KEY=""

#
# 1. Generate temporal water mask
#
start=0
end=191 # number of scenes

for ((i = $start; i <= $end; i++)); do
    bdcrrm-cli production make python3 analysis/main.py temporal_water_mask $i
done
