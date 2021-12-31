# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

import os
import shutil
from pathlib import Path

from typing import List, Dict

from .mutator import GraphMutator
from ..execution.plan import ExecutionPlan
from ..index.model import ExecutionCompendium


class ReproducibleOperations:
    def __init__(self, execution_engine, execution_indexer):
        self._execution_engine = execution_engine
        self._execution_indexer = execution_indexer

        self._graph = self._execution_indexer.graph_manager.graph

    def _check_outdated_executions(self):
        # checking if the graph is outdated
        outdated_executions = list(
            self._execution_indexer.search.faceted.get_outdated_compendia()
        )
        if outdated_executions:
            raise RuntimeError(
                "There are pipeline runs that are out of date. Run them again before performing a new run."
            )

    def _remove_unused_execution_files(self):
        """Remove execution files that are not linked to any vertex."""
        # get files from execution directory

        execution_files_stored = os.listdir(
            self._execution_engine.files_config.storage_dir
        )

        # get the registered files
        execution_files_valid_on_graph = self._execution_indexer.graph_manager.to_frame(
            dim="vertex"
        )
        if len(execution_files_valid_on_graph):
            execution_files_valid_on_graph = execution_files_valid_on_graph["name"]

            # get the symmetric difference to define the files to remove
            execution_files_to_remove = set(
                execution_files_stored
            ).symmetric_difference(set(execution_files_valid_on_graph.tolist()))

            # remove the files
            for execution_file in execution_files_to_remove:
                shutil.rmtree(
                    Path(self._execution_engine.files_config.storage_dir)
                    / execution_file
                )

    def run(self, execution_plan: ExecutionPlan):
        self._check_outdated_executions()

        # Searching for previous output files (checksum)
        previous_output_checksum = self._execution_indexer.graph_manager.outputs
        execution_job_results = self._execution_engine.execute(
            execution_plan, states={"previous_outputs": previous_output_checksum}
        )

        # indexing the new done above.
        results = [
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

        # removing outdated/invalid directories
        self._remove_unused_execution_files()

        return results

    def update(self):
        _graph = self._execution_indexer.graph_manager.graph

        # preparing the outdated compendia that will be executed
        outdated_executions = list(
            self._execution_indexer.search.faceted.get_outdated_compendia()
        )
        outdated_compendia = [execution[0] for execution in outdated_executions]

        # mutating graph to execution plan
        execution_plan = (
            GraphMutator.mutate_graph_to_execution_plan_by_outdated_compendia(
                _graph,
                outdated_compendia,
                self._execution_engine.files_config.storage_dir,
            )
        )

        execution_result = []
        if execution_plan:
            previous_output_checksum = self._execution_indexer.graph_manager.outputs

            execution_job_results = self._execution_engine.execute(
                execution_plan, states={"previous_outputs": previous_output_checksum}
            )

            execution_result = [
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

        # removing outdated/invalid directories
        self._remove_unused_execution_files()

        return execution_result

    def rerun(
        self,
        reproducible_storage: str,
        required_data_objects: Dict = None,
        required_environment_variables: List[str] = None,
    ):
        """"""
        self._check_outdated_executions()

        _graph = self._execution_indexer.graph_manager.graph
        execution_compendia = list(
            self._execution_indexer.search.query.query_compendia()
        )

        execution_plan = GraphMutator.mutate_index_graph_to_compendia_job_graph(
            _graph, reproducible_storage, execution_compendia
        )

        # reproducing
        self._execution_engine.reproduce(
            execution_plan,
            required_data_objects or {},
            required_environment_variables or [],
        )
