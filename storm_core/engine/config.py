# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Execution engine configurations."""

from typing import List
from .executor.backends.base import GraphExecutor


class ExecutionEngineServicesConfig:
    def __init__(self, graph_executor: GraphExecutor):
        self._graph_executor = graph_executor

    @property
    def graph_executor(self):
        return self._graph_executor


class ExecutionEngineFilesConfig:
    def __init__(
        self,
        working_directory,
        data_storage={},
        ignored_objects={},
        environment_variables_to_remove: List[str] = [],
        algorithm_checksum_files: str = "md5",
    ):
        self._working_directory = working_directory

        self._data_storage = data_storage
        self._ignored_objects = ignored_objects

        self._algorithm_checksum_files = algorithm_checksum_files
        self._environment_variables_to_remove = environment_variables_to_remove

    @property
    def data_storage(self):
        return self._data_storage

    @property
    def ignored_objects(self):
        return self._ignored_objects

    @property
    def working_directory(self):
        return self._working_directory

    @property
    def environment_variables_to_remove(self):
        return self._environment_variables_to_remove.copy()

    @property
    def checksum_algorithm(self):
        return self._algorithm_checksum_files


__all__ = (
    "ExecutionEngineFilesConfig",
    "ExecutionEngineServicesConfig",
)
