#
# This file is part of Brazil Data Cube Reproducible Research Management CLI.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Management Executor Engine."""

import os
from typing import List

from .reprozip import reprozip_execute_script, reprozip_execution_metadata

from .config import EnvironmentConfig
from .graph import ExecutionGraphManager

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

    # bdcrrm `run` `command`
    def execute(self, command: str):
        """Execute a User Defined Command with ReproZip Trace System.
        
        Args:
            command (str): User Defined Command.
        
        Returns:
            None: 
        """

        # prepare commands to execute
        command = command.split()
        binary_command = command[0]

        # execute script with ReproZip (trace and pack)
        repropack_directory = reprozip_execute_script(self._reprofiles_directory, binary_command, command)
        
        # load execution graph
        graph_manager = ExecutionGraphManager(GraphPersistencePickle.load_graph(self._metadata_dir))
        
        # save reprozip execution into the execution graph
        execution_metadata = reprozip_execution_metadata(repropack_directory, self._additional_working_directories)
        graph_manager.add_vertex(**execution_metadata)

        # save execution graph
        GraphPersistencePickle.save_graph(graph_manager.graph, self._metadata_dir)


__all__ = (
    "ExecutionEngine"
)
