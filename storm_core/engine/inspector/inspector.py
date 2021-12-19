# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from .config import InspectorConfig
from ..component import ComponentExecutor


class Inspector(ComponentExecutor):
    def __init__(self, config: InspectorConfig):
        super(Inspector, self).__init__(
            config, ["inspect_environment_variables", "inspect_data_files"]
        )


__all__ = "Inspector"
