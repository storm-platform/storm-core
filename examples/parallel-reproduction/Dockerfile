#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management API is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
FROM jupyter/datascience-notebook:python-3.8.8

USER root

#
# Install python dependencies
#
RUN apt-get update -y \
    && apt-get install -y libcairo2-dev git \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install --upgrade pip setuptools wheel \
    && pip3 install rasterio joblib fire stac.py

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
WORKDIR /home/${NB_USER}/
COPY examples/parallel-reproduction /home/${NB_USER}/work/parallel-reproduction

#
# Installing the rr-water-mask library
#
RUN cd /home/${NB_USER}/work/parallel-reproduction \
  && pip install .[all] \
  && chown ${NB_USER} -R /home/${NB_USER}/work/parallel-reproduction
