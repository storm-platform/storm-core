# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from abc import ABC, abstractmethod
from typing import Callable, List

from ...job import JobResult
from ...plan import ExecutionPlan


class GraphExecutor(ABC):
    """Base class for the graph executor.

    A graph executor is an entity responsible for executing
    and controlling the research pipeline produced by the user.
    Every Graph Executor must have the following properties:

        1. Methods to produce and reproduce results;
        2. Handle the execution plan execution order.
    """

    name = None
    """Graph executor name."""

    @abstractmethod
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def map_execution(
        self, operator: Callable, execution_plan: ExecutionPlan, **kwargs
    ) -> List[JobResult]:
        """Method called by the Execution Engine to produce the experiment results.

        An implementation of this method must handle the following cases:
            1. Empty Execution Plan;
            2. Execution Plan with one job;
            3. Execution Plan with two or more jobs.

        For every job in the Execution Job, this function must call the ``operator`` function. The
        Execution Plan defines the execution order, and the implementation must respect it.

        Args:
            operator (Callable): Function to apply the Execution Plan jobs.

            execution_plan (ExecutionPlan): Execution Plan to run.

            kwargs: Extra parameters.

        Returns:
            List[JobResult]: List of job results (Produced by te operator).
        """
        pass

    @abstractmethod
    def map_reproduction(
        self, operator: Callable, execution_plan: ExecutionPlan, **kwargs
    ) -> List[JobResult]:
        """Method called by the Execution Engine to reproduce a experiment results.

        An implementation of this method must handle the following cases:
            1. Empty Execution Plan;
            2. Execution Plan with one job;
            3. Execution Plan with two or more jobs.

        For every job in the Execution Job, this function must call the ``operator`` function. The
        Execution Plan defines the execution order, and the implementation must respect it.

        Args:
            operator (Callable): function to apply the Execution Plan jobs.

            execution_plan (ExecutionPlan): Execution Plan to run.

            kwargs: Extra parameters.

        Returns:
            List[JobResult]: List of job results (Produced by te operator).
        """
        pass
