#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Temporal water mask library `main module`."""

import fire
from pipeline import temporal_water_mask

if __name__ == "__main__":
    fire.Fire({
        "temporal_water_mask": temporal_water_mask
    })
