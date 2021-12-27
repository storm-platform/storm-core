# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from igraph import Graph


class ExecutionPlan:
    def __init__(self, jobs: Graph):
        self._jobs = jobs

    def _index_to_job(self, vertex_index):
        return self.job(self._jobs.vs[vertex_index]["name"])

    def job(self, execution_id):
        selected_job = self._jobs.vs.select(name=execution_id)

        if selected_job:
            return selected_job["job"][-1]
        return None

    def jobs(self):
        for vertex_index in self._jobs.topological_sorting():
            job = self._index_to_job(vertex_index)

            yield job

    def job_predecessors(self, execution_id):
        selected_job = self._jobs.vs.select(name=execution_id)
        if selected_job:
            selected_job = selected_job[-1]

            for job_predecessor_index in self._jobs.predecessors(selected_job):
                yield self._index_to_job(job_predecessor_index)
