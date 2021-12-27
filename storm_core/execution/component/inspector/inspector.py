# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from typing import List

from ..base import BaseComponentExecutor
from .component import InspectorComponent, InspectorFileRemoverComponent


class InspectorConfig:
    """Inspector configuration class."""

    components: List[InspectorComponent] = [InspectorFileRemoverComponent]
    """List of inspector components."""


class Inspector(BaseComponentExecutor):
    """Inspector class.

    An Inspector is a ``Component Executor`` that supports
    components with methods that change the files structure,
    metadata fields, environment variables, etc.

    You should use this type of component executor and their
    components when you need modifications in the base reproducible
    bundle.
    """

    config = InspectorConfig

    def __init__(self):
        """Initializer."""
        super(Inspector, self).__init__(
            ["inspect_environment_variables", "inspect_data_files"]
        )
