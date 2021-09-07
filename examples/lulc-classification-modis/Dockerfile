#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management API is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
FROM brazildatacube/sits-rstudio:0.13.0

USER root

#
# Install python dependencies
#
RUN apt-get update -y \
    && apt-get install -y python3-pip python3.8-venv python3.8-dev git \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip setuptools wheel requests

#
# Install bdcrrm-api
#
WORKDIR /opt/bdcrrm/

COPY . .
RUN pip3 install .[all] \
  && rm -rf *

#
# Copy the example to the base user
#
COPY examples/lulc-classification-modis /home/sits/lulc-classification-modis

RUN chown sits:sits -R /home/sits/lulc-classification-modis
