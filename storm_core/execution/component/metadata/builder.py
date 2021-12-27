# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from typing import List

from ..base import BaseComponentExecutor
from .component import MetadataComponent, FileChecksumMetadataComponent


class MetadataBuilderConfig:
    """Metadata builder configuration class."""

    components: List[MetadataComponent] = [
        FileChecksumMetadataComponent,
    ]
    """List of inspector components."""


class MetadataBuilder(BaseComponentExecutor):
    """Metadata builder class.

    A Metadata Builder is a ``Component Executor`` that supports
    components to extract metadata information from
    the reproducible bundle files.
    """

    config = MetadataBuilderConfig

    def __init__(self):
        """Initializer."""
        super(MetadataBuilder, self).__init__(["do_metadata"])
