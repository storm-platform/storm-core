#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Temporal water mask library `analysis pipeline configuration`."""

import os


class PipelineConfiguration:
    """Pipeline configuration class."""

    #
    # General definitions
    #
    n_jobs = 4

    output_directory = "data/derived_data"

    #
    # Brazil Data Cube STAC
    #
    stac_token = os.getenv("BDC_ACCESS_KEY")
    stac_url = "https://brazildatacube.dpi.inpe.br/stac/"

    stac_assets = ("BAND14", "BAND16")
    stac_collection = "CB4_64_16D_STK-1"

    stac_items_filter = {
        "bbox": "-63.4570,-17.6021,-51.6797,-9.4924",

        "start_date": "2018-01-01",
        "end_date": "2019-01-01",

        "limit": 192
    }

    #
    # Water Mask function arguments
    #
    band_mapping = {
        "green": "BAND14",
        "nir": "BAND16"
    }
