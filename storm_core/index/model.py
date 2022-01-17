# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from copy import deepcopy
from typing import List

from storm_core.execution.command import ExecutableCommand


class ExecutionCompendium:
    def __init__(self, name, command, compendium_package, metadata):
        self._name = name
        self._command = command
        self._metadata = metadata
        self._compendium_package = compendium_package

    @property
    def name(self):
        return self._name

    @property
    def command(self):
        return deepcopy(self._command)

    @property
    def inputs(self) -> List:
        return self._metadata.get("inputs", [])

    @property
    def outputs(self) -> List:
        return self._metadata.get("outputs", [])

    @property
    def metadata(self):
        return deepcopy(self._metadata)

    @property
    def compendium_package(self):
        return self._compendium_package


class ExecutionCompendiumFactory:
    """A simple yet powerful ExecutionCompendium factory class."""

    @staticmethod
    def create_compendium(compendium_vertex) -> ExecutionCompendium:
        """Factory method to create a ExecutionCompendium class based on an
        Indexed Execution Compendium.

        Args:
            compendium_vertex (igraph.Vertex): Indexed execution compendium.

        Returns:
            ExecutionCompendium: ExecutionCompendium object.
        """
        name = compendium_vertex["name"]
        metadata = compendium_vertex["metadata"]
        metadata = {
            **metadata,
            "external_inputs_required": compendium_vertex["external_inputs_required"],
        }

        # compendium definition
        compendium_package = {
            "key": compendium_vertex["environment_package"],
            "checksum": compendium_vertex["environment_package_checksum"],
            "algorithm": compendium_vertex["environment_package_checksum_algorithm"],
        }

        # creating the executable command
        command = compendium_vertex["command"]
        split_fnc = compendium_vertex["command_config"]["split_fnc"]
        checksum_algorithm = compendium_vertex["command_config"]["checksum_algorithm"]

        executable_command = ExecutableCommand(command, split_fnc, checksum_algorithm)

        return ExecutionCompendium(
            name, executable_command, compendium_package, metadata
        )
