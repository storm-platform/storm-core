#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Temporal water mask library `stac functions`."""

from typing import Dict, List, Tuple


def filter_stac_features_by_asset_name(stac_features: List[Dict], assets: Tuple) -> List[Dict]:
    """Filter STAC Features by asset names.

    Args:
        stac_features (List[Dict]): STAC Features to filter.

        assets (Tuple): Asset names to filter by.

    Returns:
        List[Dict]: A `Dict` with filtered STAC Features. The returned dictionary format contains the following keys:
            - `id`: STAC Feature ID.
            - `bands`: A `List` with the URL of the STAC Feature's bands. The bands are based on `assets` names.
    """
    scenes = []

    for feature in stac_features:
        scene_id = feature["id"]

        bands = {}

        # get specific bands
        for asset in assets:
            bands[asset] = feature.assets[asset]["href"]

        # saving bands and scene_id to list of scenes
        scenes.append({
            "id": scene_id,
            "bands": bands
        })
    return scenes
