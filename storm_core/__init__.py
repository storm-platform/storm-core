# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""SpatioTemporal Open Research Manager."""

from .engine.execution_engine import ExecutionEngine
from .version import __version__

__all__ = ("__version__", "ExecutionEngine")
