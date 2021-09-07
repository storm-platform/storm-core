#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Temporal water mask library `pipeline definion module`."""

import os

from config import PipelineConfiguration as config
from rr_water_mask.parallelly import ndwi_delayed
from rr_water_mask.stac import filter_stac_features_by_asset_name
from stac import STAC


def temporal_water_mask(feature_index: int):
    """Run the Temporal Water Mask.

    :param feature_index: Index of STACFeature that will be processed
    """
    #
    # 1. STAC Service and STAC Collection
    #
    service = STAC(config.stac_url,
                   access_token=config.stac_token)

    collection = service.collection(config.stac_collection)

    #
    # 2. STAC Items
    #
    items = collection.get_items(filter=config.stac_items_filter)
    features = filter_stac_features_by_asset_name(items.features,
                                                  config.stac_assets)

    feature = features[feature_index: feature_index + 1]

    #
    # 3. Temporal Water Mask
    #
    os.makedirs(config.output_directory, exist_ok=True)

    ndwi_delayed(feature,
                 config.output_directory,
                 config.n_jobs,
                 config.band_mapping)
