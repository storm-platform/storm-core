#
# This file is part of SpatioTemporal Open Research Manager Core.
# Copyright (C) 2021 INPE.
#
# SpatioTemporal Open Research Manager Core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from typing import List

from .components import InspectorFileRemoverComponent, InspectorComponent


class InspectorConfig:
    components: List[InspectorComponent] = [
        InspectorFileRemoverComponent
    ]


__all__ = (
    "InspectorGeneralComponent"
)
