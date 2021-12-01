#
# This file is part of SpatioTemporal Open Research Manager Core.
# Copyright (C) 2021 INPE.
#
# SpatioTemporal Open Research Manager Core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from .config import MetadataBuilderConfig
from ..component import ComponentExecutor


class MetadataBuilder(ComponentExecutor):

    def __init__(self, config: MetadataBuilderConfig):
        super(MetadataBuilder, self).__init__(config, ["do_metadata"])


__all__ = (
    "MetadataBuilder"
)
