# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from itertools import chain
from functools import reduce

from typing import Callable, List

import ray
from ray.remote_function import RemoteFunction

from ..base import GraphExecutor
from ...api import ExecutionPlan, JobResult


class RayBackend(GraphExecutor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        ray.init(**kwargs)

    def _map_operator(
        self,
        remote_operator: RemoteFunction,
        execution_plan: ExecutionPlan,
        is_reproduction=False,
        **kwargs
    ):
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
        return list(chain(*[ray.get(ray_job[-1]) for ray_job in ray_job_storage]))

    def map_execution(
        self, operator: Callable, execution_plan: ExecutionPlan, **kwargs
    ) -> List[JobResult]:
        @ray.remote
        def do_execution_job(job, extra_parameters, *dependencies):
            dependencies = dependencies or []
            return [*[operator(job)], *list(chain(*dependencies))]

        return self._map_operator(do_execution_job, execution_plan, False, **kwargs)

    def map_reproduction(
        self, operator: Callable, execution_plan: ExecutionPlan, **kwargs
    ) -> List[JobResult]:
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
                **{"previous_output_files": previous_output_files, **extra_parameters}
            )
            return dependencies + [operator_result]

        return self._map_operator(do_reproduction_job, execution_plan, True, **kwargs)


__all__ = "RayBackend"
