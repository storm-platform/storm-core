#
# This file is part of SpatioTemporal Open Research Manager Core.
# Copyright (C) 2021 INPE.
#
# SpatioTemporal Open Research Manager Core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from typing import List
from copy import deepcopy


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


__all__ = (
    "ExecutionCompendium"
)
