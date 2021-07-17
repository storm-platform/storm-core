#
# This file is part of Brazil Data Cube Reproducible Research Management CLI.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Management Executor Engine."""

import os

import shutil

from typing import List

from .reprozip import reprozip_execute_script, reprozip_execution_metadata

from .config import EnvironmentConfig
from .graph import ExecutionGraphManager, VertexStatus

from .persistence import GraphPersistencePickle


class ExecutionEngine():
    """Execution Engine."""

    def __init__(self, working_dir: str, reprofiles_directory: str, additional_working_directories: List[str] = None):
        """Initialize execution engine.
        
        Args:
            working_dir (str): Path of the current working directory.

            reprofiles_directory (str): Path to the reprofiles directory.

            additional_working_directories (str): List of additional working directories.

        Note:
            The working directories are used in determining which are the input and output files of the experiment being 
            performed. By default, only the `working_dir` directory is used. Different directories that must be considered are
            declared through the `additional_working_directories` argument.
        """
        self._working_dir = working_dir
        self._reprofiles_directory = reprofiles_directory

        self._metadata_dir = os.path.join(self._working_dir, EnvironmentConfig.REPROPACK_BASE_PATH)

        self._additional_working_directories = (
            [working_dir, *additional_working_directories] if additional_working_directories else [self._working_dir]
        )

        self._graph_manager = self._load_graph_manager()  # what about this ?

    def _remove_unused_execution_files(self):
        """Remove execution files that are not linked to any vertex."""
        
        # get files from execution directory
        execution_files_stored_dir = os.path.join(self._metadata_dir, EnvironmentConfig.REPROPACK_EXEC_PATH)
        execution_files_stored = os.listdir(execution_files_stored_dir)

        # get the registered files
        execution_files_valid_on_graph = self._graph_manager.to_frame(dim = "vertex")
        execution_files_valid_on_graph = execution_files_valid_on_graph["repropack"]

        # only the basename
        execution_files_stored = list(map(os.path.basename, execution_files_stored))
        execution_files_valid_on_graph = list(map(lambda x: x.split(os.sep)[-2], execution_files_valid_on_graph))

        # get the symmetric difference to define the files to remove
        execution_files_to_remove = set(execution_files_stored).symmetric_difference(set(execution_files_valid_on_graph))

        # remove the files
        for execution_file in execution_files_to_remove:
            shutil.rmtree(
                os.path.join(execution_files_stored_dir, execution_file)
            )

    def _load_graph_manager(self) -> ExecutionGraphManager:
        """Load the Execution Graph Manager linked to the executions.
        
        Returns:
            ExecutionGraphManager: Execution graph.
        """
        return ExecutionGraphManager(GraphPersistencePickle.load_graph(self._metadata_dir))

    def _save_graph_manager(self, graph_manager: ExecutionGraphManager):
        """Save the Execution Graph Manager linked to the executions.
        
        Args:
            graph_manager (ExecutionGraphManager): Execution Graph Manager instance.
        """
        GraphPersistencePickle.save_graph(graph_manager.graph, self._metadata_dir)

    # bdcrrm `run` `command`
    def execute(self, command: str, remove_previous_execution_files: bool = True):
        """Execute a User Defined Command with ReproZip Trace System.
        
        Args:
            command (str): User Defined Command.

            remove_previous_execution_files (bool): Flag to indicate whether or not directories from 
            previous runs should be removed from the `REPROPACK_BASE_PATH`.
        
        Returns:
            None: 
        """
        # prepare commands to execute
        command = command.split()
        binary_command = command[0]

        # execute script with ReproZip (trace and pack)
        repropack_directory = reprozip_execute_script(self._reprofiles_directory, binary_command, command)
                
        # save reprozip execution into the execution graph
        execution_metadata = reprozip_execution_metadata(repropack_directory, self._additional_working_directories)
        self._graph_manager.add_vertex(**execution_metadata)

        # save execution graph
        self._save_graph_manager(self._graph_manager)

        if remove_previous_execution_files:
            self._remove_unused_execution_files()

    def remake(self):  # what about this name ?
        """Remake the execution graph where vertices is `outdated`."""

        for vertex_index in self._graph_manager.graph.topological_sorting(mode = "out"):
            vertex = self._graph_manager.graph.vs[vertex_index]

            if vertex["status"] == VertexStatus.Outdated:
                self.execute(vertex["command"])


__all__ = (
    "ExecutionEngine"
)
