#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Temporal water mask library `parallel functions`."""

import os

import rasterio as rio
from joblib import Parallel, delayed
from rr_water_mask.spectral_index import ndwi2

DEFAULT_BAND_NAME = {
    "green": "BAND14",
    "nir": "BAND16"
}


def ndwi_delayed(stac_features,
                 ouput_directory,
                 n_jobs=3,
                 bands=DEFAULT_BAND_NAME):
    """Process Normalized difference water index (NDWI) in a parallel way using joblib."""
    nir_band_name = DEFAULT_BAND_NAME["nir"]
    green_band_name = DEFAULT_BAND_NAME["green"]

    for feature in stac_features:

        print(feature["id"])

        # Get the raster data for the feature
        reference_band = rio.open(feature["bands"][green_band_name])

        # split image into mini-rasters
        windows = list(
            map(
                lambda x: x[1], list(
                    reference_band.block_windows()
                )
            )
        )

        # processing in a parallel way
        water_mini_rasters = Parallel(n_jobs=n_jobs)(
            delayed(ndwi2)(
                feature["bands"][green_band_name],
                feature["bands"][nir_band_name],
                window
            ) for window in windows
        )

        # save the water mask raster result
        output_profile = reference_band.profile.copy()
        output_profile['count'] = 1
        output_profile['dtype'] = 'float32'
        output_profile['driver'] = 'GTiff'

        output_filename = os.path.join(ouput_directory,
                                       feature["id"] + "_watermask.tif")

        with rio.open(output_filename, "w", **output_profile) as dst:
            for mini_raster_data, window in water_mini_rasters:
                dst.write(mini_raster_data, window=window)
