#
# This file is part of SpatioTemporal Open Research Manager Core.
# Copyright (C) 2021 INPE.
#
# SpatioTemporal Open Research Manager Core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from typing import Callable, List
from abc import ABC, abstractmethod

from ..api import JobResult
from ...executor.api import ExecutionPlan


class GraphExecutor(ABC):

    @abstractmethod
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def map_execution(self, operator: Callable, execution_plan: ExecutionPlan, **kwargs) -> List[JobResult]:
        pass

    @abstractmethod
    def map_reproduction(self, operator: Callable, execution_plan: ExecutionPlan, **kwargs) -> List[JobResult]:
        pass


__all__ = (
    "GraphExecutor"
)
