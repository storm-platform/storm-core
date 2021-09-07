#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Temporal water mask library `spectral functions`."""

from typing import Tuple

import numpy as np
import rasterio as rio
import rasterio.windows


def ndwi2(green_file: str, nir_file: str, window: rio.windows.Window) -> Tuple[np.ndarray, rasterio.windows.Window]:
    """Calculate the Normalized Difference Water Index (NDWI2).

    Args:
        green_file (str): The path to the green band file.

        nir_file (str): The path to the nir band file.

        window (rasterio.windows.Window): The window to extract from the raster.

    Returns:
        np.ndarray: NDWI2 raster.

    See:
        - McFeeters, S. K., 1996. The use of the Normalized Difference Water Index (NDWI) in
          the delineation of open water features. International Journal ofRemote Sensing, 17(7), 1425-1432.

        - rasterio.windows module: https://rasterio.readthedocs.io/en/latest/api/rasterio.windows.html
    Note:
        The `rio.windows.Window` is an object that allows you to determine the region of the raster to be processed. The `window` parameter
        accepts this object and allows only a portion of the scene to be processed. This can be used as a base strategy for
        parallelizing the NDWI2 calculation operation.
    """
    nir = rio.open(nir_file).read(window=window)
    green = rio.open(green_file).read(window=window)

    return (green - nir) / (green + nir), window
