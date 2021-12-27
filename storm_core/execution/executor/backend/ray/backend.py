# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

try:
    import ray
    from ray.remote_function import RemoteFunction
except ImportError:
    raise ModuleNotFoundError(
        "To use the Ray backend, please, install the Ray library: `pip install ray`"
    )

from itertools import chain
from functools import reduce

from typing import Callable, List

from ....job import JobResult
from ..base import GraphExecutor
from ....plan import ExecutionPlan


class RayBackend(GraphExecutor):
    """Ray based Executor graph."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        ray.init(**kwargs)

    def _map_operator(
        self,
        remote_operator: RemoteFunction,
        execution_plan: ExecutionPlan,
        is_reproduction=False,
        **kwargs
    ) -> List[JobResult]:
        """Base map operator to production and reproduction of results.

        Args:
            remote_operator (RemoteFunction): Ray remote function to run.

            execution_plan (ExecutionPlan): Execution Plan to be converted executed.

            is_reproduction (bool): Flag indicating if the map operation is a reproduction.

            kwargs: Extra processing arguments.
        Returns:
            List[JobResult]: List of job results (Produced by te operator).
        """
        reproduction_options = {}
        if is_reproduction:
            reproduction_options = kwargs.get("fnc_options", {})

        # configuring the ray workflow
        ray_job_storage = []

        for job in execution_plan.jobs():

            ray_job_predecessors = []
            for job_predecessor in execution_plan.job_predecessors(job.execution_id):
                # searching for the job on ray storage
                jobs_ray = list(
                    filter(
                        lambda x: x[0] == job_predecessor.execution_id, ray_job_storage
                    )
                )

                if not jobs_ray:
                    jobs_ray = [
                        job_predecessor.execution_id,
                        remote_operator.remote(job_predecessor, reproduction_options),
                    ]

                ray_job_predecessors.extend([x[-1] for x in jobs_ray])
            ray_job_storage.extend(
                [
                    (
                        job.execution_id,
                        remote_operator.remote(
                            job, reproduction_options, *ray_job_predecessors
                        ),
                    )
                ]
            )

        # getting the job results.
        ray_results = [ray.get(ray_job[-1]) for ray_job in ray_job_storage]

        # filtering the results to remove duplicated
        # and hold the original order.
        job_results = []
        for ray_result_list in ray_results:
            for ray_result in ray_result_list:
                if ray_result not in job_results:
                    job_results.append(ray_result)

        return job_results

    def map_execution(
        self, operator: Callable, execution_plan: ExecutionPlan, **kwargs
    ) -> List[JobResult]:
        """Method called by the Execution Engine to produce the experiment results.

        Args:
            operator (Callable): Function to apply the Execution Plan jobs.

            execution_plan (ExecutionPlan): Execution Plan to run.

            kwargs: Extra parameters.

        Returns:
            List[JobResult]: List of job results (Produced by te operator).
        """
        # defining a ray job with the graph dependencies
        # to production operations.
        @ray.remote
        def do_execution_job(job, extra_parameters, *dependencies):
            dependencies = dependencies or []
            return [*[operator(job)], *list(chain(*dependencies))]

        return self._map_operator(do_execution_job, execution_plan, False, **kwargs)

    def map_reproduction(
        self, operator: Callable, execution_plan: ExecutionPlan, **kwargs
    ) -> List[JobResult]:
        """Method called by the Execution Engine to reproduce a experiment results.

        Args:
            operator (Callable): function to apply the Execution Plan jobs.

            execution_plan (ExecutionPlan): Execution Plan to run.

            kwargs: Extra parameters.

        Returns:
            List[JobResult]: List of job results (Produced by te operator).
        """

        @ray.remote
        def do_reproduction_job(job, extra_parameters, *dependencies):
            previous_output_files = []
            dependencies = dependencies or []

            # extracting some information from dependencies result
            if dependencies:
                dependencies = reduce(lambda x, y: x + y, dependencies)
                for dependency in dependencies:
                    previous_output_files.extend(
                        dependency.execution_results.get("previous_output_files", [])
                    )

            # running the operator
            operator_result = operator(
                job,
                **{"previous_output_files": previous_output_files, **extra_parameters},
            )
            return dependencies + [operator_result]

        return self._map_operator(do_reproduction_job, execution_plan, True, **kwargs)
