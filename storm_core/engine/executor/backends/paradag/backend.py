#
# This file is part of SpatioTemporal Open Research Manager Core.
# Copyright (C) 2021 INPE.
#
# SpatioTemporal Open Research Manager Core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from typing import Callable, List

from ..base import GraphExecutor
from ...api import ExecutionPlan, JobResult

from paradag import DAG, MultiThreadProcessor, SequentialProcessor, dag_run


class CustomizableSelector:
    """Customizable dag_run selector to change the number of process used."""

    def __init__(self, processors: int):
        self._processors = processors

    def select(self, running, idle):
        task_number = max(0, self._processors - len(running))
        return list(idle)[:task_number]


class ReproducibleExecutor:
    """Reproduction executor of an execution graph.

    This class implements all the rules necessary for parallel
    reproduction (multiprocessing) of a execution graph.
    """

    def __init__(self, operator_fnc, reproducible_pipeline: ExecutionPlan, **kwargs):
        """Class initializer.

        Args:
            graph (igraph.Graph): Execution graph with all steps that will be processed.

            kwargs (dict): Extra parameters for the `fnc`.
        """
        self._extra_options = kwargs
        self._operator_fnc = operator_fnc
        self._reproducible_pipeline = reproducible_pipeline

        self._results = []

    @property
    def results(self):
        return self._results.copy()

    def param(self, job_id):
        """Select the vertex that will be processed."""
        return self._reproducible_pipeline.job(job_id)

    def execute(self, job):
        """Execute a vertex."""
        job_result = self._operator_fnc(job)
        self._results.append(job_result)

        return job_result


class ReproductionExecutor:
    """Reproduction executor of an execution graph.

    This class implements all the rules necessary for parallel
    reproduction (multiprocessing) of a execution graph.
    """

    def __init__(self, operator_fnc: Callable, reproducible_pipeline: ExecutionPlan, **kwargs):
        """Class initializer.

        Args:
            operator_fnc (Callable): Function used to process the graph vertices.

            graph (igraph.Graph): Execution graph with all steps that will be processed.

            kwargs (dict): Extra parameters for the `fnc`.
        """
        self._operator_fnc = operator_fnc
        self._extra_options = kwargs
        self._reproducible_pipeline = reproducible_pipeline

        self._level = []
        self._results = []

    @property
    def results(self):
        return self._results.copy()

    def param(self, job_id):
        """Select the vertex that will be processed."""
        return self._reproducible_pipeline.job(job_id)

    def execute(self, job):
        """Execute a vertex."""
        job_result = self._operator_fnc(job, **{"previous_output_files": self._level, **self._extra_options})
        self._results.append(job_result)

        return job_result

    def deliver(self, _, result):
        """Deliver results to descendants vertices."""
        files_dict = [*self._level, *result.execution_results["previous_output_files"]]
        files_dict = [dict(_tuple) for _tuple in {tuple(sorted(_dict.items())) for _dict in files_dict}]

        self._level = files_dict


class ParaDagBackend(GraphExecutor):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        n_process = kwargs.get("n_process", 1)

        # defining who will be execute the graph
        self._processors_number = n_process
        self._processor_class = SequentialProcessor

        if n_process > 1:
            self._processor_class = MultiThreadProcessor

    def _map(self, reproducible_pipeline: ExecutionPlan):

        # creating the execution graph
        dag = DAG()
        dag.add_vertex(*[v.execution_id for v in list(reproducible_pipeline.jobs())])

        # adding the graph edges
        for job in reproducible_pipeline.jobs():
            for job_predecessor in reproducible_pipeline.job_predecessors(job.execution_id):
                dag.add_edge(job_predecessor.execution_id, job.execution_id)

        return dag

    def map_execution(self, operator_fnc: Callable, execution_plan: ExecutionPlan, **kwargs) -> List[JobResult]:
        """Make the execution graph run."""

        # defining the dag and the executor
        dag = self._map(execution_plan)
        executor = ReproducibleExecutor(operator_fnc, execution_plan)

        # run!
        dag_run(dag, processor=self._processor_class(),
                executor=executor,
                selector=CustomizableSelector(self._processors_number))

        # Extracting the results.
        # The results are extracted from the executor, since the return from
        # `dag_run` is just the reference to the processed vertices.
        return executor.results

    def map_reproduction(self, operator_fnc: Callable, execution_plan: ExecutionPlan, **kwargs) -> List[JobResult]:
        """TODO"""

        # extracting extra parameters to reproduction
        reproduction_operator_options = kwargs.get("fnc_options", {})

        # defining the dag and the executor
        dag = self._map(execution_plan)
        executor = ReproductionExecutor(operator_fnc, execution_plan, **reproduction_operator_options)

        dag_run(dag, processor=self._processor_class(),
                executor=executor,
                selector=CustomizableSelector(self._processors_number))

        return executor.results


__all__ = (
    "ParaDagBackend"
)
