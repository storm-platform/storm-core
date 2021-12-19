#
# This file is part of SpatioTemporal Open Research Manager Core.
# Copyright (C) 2021 INPE.
#
# SpatioTemporal Open Research Manager Core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from typing import List, Dict

from ..helper.mutator import GraphMutator

from .compendium import ExecutionCompendium
from ..engine.executor.api import ExecutionPlan


class ReproducibleOperations:
    def __init__(self, execution_engine, execution_indexer):
        self._execution_engine = execution_engine
        self._execution_indexer = execution_indexer

        self._graph = self._execution_indexer.graph_manager.graph

    def _check_outdated_executions(self):
        # checking if the graph is outdated
        outdated_executions = list(
            self._execution_indexer.search.faceted.outdated_execution_compendia()
        )
        if outdated_executions:
            raise RuntimeError(
                "There are pipeline runs that are out of date. Run them again before performing a new run."
            )

    def execute(self, execution_plan: ExecutionPlan):
        self._check_outdated_executions()
        execution_job_results = self._execution_engine.execute(execution_plan)

        return [
            self._execution_indexer.index_execution(
                ExecutionCompendium(
                    command=ec.command,
                    name=ec.execution_id,
                    metadata=ec.execution_results["metadata"],
                    compendium_package=ec.execution_results["compendium_package"],
                )
            )
            for ec in execution_job_results
        ]

    def rerun(self, reproducible_storage):
        _graph = self._execution_indexer.graph_manager.graph

        # preparing the outdated compendia that will be executed
        outdated_executions = list(
            self._execution_indexer.search.faceted.outdated_execution_compendia()
        )
        outdated_compendia = [execution[0] for execution in outdated_executions]

        # mutating graph to execution plan
        execution_plan = (
            GraphMutator.mutate_graph_to_execution_plan_by_outdated_compendia(
                _graph, outdated_compendia, reproducible_storage
            )
        )

        execution_result = []
        if execution_plan:
            execution_job_results = self._execution_engine.execute(execution_plan)

            execution_result = [
                self._execution_indexer.edit_indexed_execution(
                    ExecutionCompendium(
                        command=ec.command,
                        name=ec.execution_id,
                        metadata=ec.execution_results["metadata"],
                        compendium_package=ec.execution_results["compendium_package"],
                    )
                )
                for ec in execution_job_results
            ]

        return execution_result

    def reproduce(
        self,
        reproducible_storage: str,
        required_data_objects: Dict = {},
        required_environment_variables: List[str] = [],
    ):
        """"""
        self._check_outdated_executions()

        _graph = self._execution_indexer.graph_manager.graph
        execution_compendia = list(
            self._execution_indexer.search.query.execution_compendium()
        )

        execution_plan = GraphMutator.mutate_index_graph_to_compendia_job_graph(
            _graph, reproducible_storage, execution_compendia
        )

        # reproducing
        self._execution_engine.reproduce(
            execution_plan, required_data_objects, required_environment_variables
        )


__all__ = "ReproducibleOperations"
