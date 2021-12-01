#
# This file is part of SpatioTemporal Open Research Manager Core.
# Copyright (C) 2021 INPE.
#
# SpatioTemporal Open Research Manager Core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from typing import List

from .components import (
    MetadataComponent,
    IOMetadataComponent,
    FileChecksumMetadataComponent
)


class MetadataBuilderConfig:
    components: List[MetadataComponent] = [
        IOMetadataComponent,
        FileChecksumMetadataComponent
    ]


__all__ = (
    "InspectorGeneralComponent"
)
