# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from copy import deepcopy
from typing import Tuple

from .graph import GraphManager
from .accessor import SearchAccessor
from .model import ExecutionCompendium


class ExecutionIndexer:
    def __init__(self, graph_manager: GraphManager = None):
        self._graph_manager = graph_manager

    @property
    def graph_manager(self):
        return deepcopy(self._graph_manager)

    @property
    def search(self):
        return SearchAccessor(self)

    def _extract_package_io(self, execution_compendium):
        inputs_checksum = list(
            map(lambda x: x["checksum"], execution_compendium.metadata.get("inputs"))
        )
        outputs_checksum = list(
            map(lambda x: x["checksum"], execution_compendium.metadata.get("outputs"))
        )

        return inputs_checksum, outputs_checksum

    def _add_execution(
        self, execution_compendium: ExecutionCompendium
    ) -> Tuple[ExecutionCompendium, str]:
        # preparing input and outputs (checksum)
        inputs_checksum, outputs_checksum = self._extract_package_io(
            execution_compendium
        )

        # preparing the command configurations
        command_configurations = {
            "split_fnc": execution_compendium.command.split_function,
            "checksum_algorithm": execution_compendium.command.checksum_algorithm,
        }

        self._graph_manager.add_vertex(
            # General description
            execution_compendium.name,
            execution_compendium.compendium_package["key"],
            execution_compendium.compendium_package["checksum"],
            execution_compendium.compendium_package["algorithm"],
            # Command
            str(execution_compendium.command),
            execution_compendium.command.checksum,
            command_configurations,
            # Files
            inputs_checksum,
            outputs_checksum,
            # Metadata
            execution_compendium.metadata,
        )

        return list(
            self.search.query.query(
                command_checksum=execution_compendium.command.checksum
            )
        )[0][
            0
        ]  # should exists!

    def _edit_indexed_execution(
        self, execution_compendium: ExecutionCompendium
    ) -> Tuple[ExecutionCompendium, str]:
        # preparing input and outputs (checksum)
        inputs_checksum, outputs_checksum = self._extract_package_io(
            execution_compendium
        )

        self._graph_manager.update_vertex(
            # General description
            execution_compendium.name,
            execution_compendium.compendium_package["key"],
            execution_compendium.compendium_package["checksum"],
            execution_compendium.compendium_package["algorithm"],
            # Command
            execution_compendium.command.checksum,
            # Metadata
            execution_compendium.metadata,
            # Files
            inputs_checksum,
            outputs_checksum,
        )

        return list(
            self.search.query.query(
                command_checksum=execution_compendium.command.checksum
            )
        )[0][
            0
        ]  # should exists!

    def index_execution(
        self, execution_compendium: ExecutionCompendium
    ) -> Tuple[ExecutionCompendium, str]:

        res = None
        selected_vertex = list(
            self.search.query.query(
                command_checksum=execution_compendium.command.checksum
            )
        )

        if selected_vertex:
            res = self._edit_indexed_execution(execution_compendium)
        else:
            res = self._add_execution(execution_compendium)
        return res

    def deindex_execution(
        self, execution_compendium_name: str, remove_related_compendia: bool = False
    ):
        self._graph_manager.delete_vertex(
            execution_compendium_name, remove_related_compendia
        )
