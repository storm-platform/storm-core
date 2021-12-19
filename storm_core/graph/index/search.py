#
# This file is part of SpatioTemporal Open Research Manager Core.
# Copyright (C) 2021 INPE.
#
# SpatioTemporal Open Research Manager Core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from typing import List, Tuple

from ..manager import VertexStatus
from ...core.compendium import ExecutionCompendium
from ...engine.executor.api import ExecutableCommand


class SearchAccessor:
    def __init__(self, execution_indexer):
        self._execution_indexer = execution_indexer

    @property
    def query(self):
        return QuerySearch(self._execution_indexer)

    @property
    def faceted(self):
        return FacetedIndexSearchAccessor(self._execution_indexer)


class IndexerSearch:
    def __init__(self, execution_indexer):
        self._execution_indexer = execution_indexer


class QuerySearch(IndexerSearch):
    def execution_compendium(self, **kwargs) -> List[Tuple[ExecutionCompendium, str]]:
        # searching for compendium in the graph
        compendia_vertex = self._execution_indexer.graph_manager.search_vertex(**kwargs)

        for compendium_vertex in compendia_vertex:
            # general definitions
            name = compendium_vertex["name"]
            metadata = compendium_vertex["metadata"]
            metadata = {
                **metadata,
                "external_inputs_required": compendium_vertex[
                    "external_inputs_required"
                ],
            }

            # compendium definition
            compendium_package = {
                "key": compendium_vertex["environment_package"],
                "checksum": compendium_vertex["environment_package_checksum"],
                "algorithm": compendium_vertex[
                    "environment_package_checksum_algorithm"
                ],
            }

            # creating the executable command
            command = compendium_vertex["command"]
            split_fnc = compendium_vertex["command_config"]["split_fnc"]
            checksum_algorithm = compendium_vertex["command_config"][
                "checksum_algorithm"
            ]

            executable_command = ExecutableCommand(
                command, split_fnc, checksum_algorithm
            )

            yield (
                ExecutionCompendium(
                    name, executable_command, compendium_package, metadata
                ),
                compendium_vertex["status"],
            )


class FacetedIndexSearchAccessor(IndexerSearch):
    def outdated_execution_compendia(self):
        _graph = self._execution_indexer.graph_manager.graph
        for vertex_index in _graph.topological_sorting(mode="out"):
            vertex = _graph.vs[vertex_index]

            if vertex["status"] == VertexStatus.Outdated:
                selected_vertex = list(
                    self._execution_indexer.search.query.execution_compendium(
                        name=vertex["name"]
                    )
                )
                yield selected_vertex[0]  # should exists!


__all__ = (
    # Accessor
    "SearchAccessor",
    # Search types
    "IndexerSearch",
    "QuerySearch",
    "FacetedIndexSearchAccessor",
)
