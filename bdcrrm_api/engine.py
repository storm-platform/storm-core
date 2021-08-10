#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management API is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Management Executor Engine."""

import copy
import os
import shutil
from tempfile import mkdtemp
from typing import Dict, List, Tuple

from .config import EnvironmentConfig, ExecutionEngineConfig
from .graph import ExecutionGraphManager, VertexStatus
from .persistence import FilesPersistencePickle, GraphPersistencePickle
from .reprozip import (filter_reprozip_config_files,
                       reprounzip_add_environment_variables,
                       reprounzip_download_all, reprounzip_run,
                       reprounzip_setup, reprounzip_upload,
                       reprozip_execute_script, reprozip_execution_metadata,
                       reprozip_pack_execution,
                       reprozip_remove_environment_variables)


class ExecutionEngine(object):
    """Execution Engine."""

    def __init__(self, working_dir: str, reprofiles_directory: str,
                 additional_working_directories: List[str] = None, datasources: Dict[str, Dict] = None,
                 secrets: List[str] = None):
        """Initialize execution engine.

        Args:
            working_dir (str): Path of the current working directory.

            reprofiles_directory (str): Path to the reprofiles directory.

            additional_working_directories (List[str]): List of additional working directories.

            datasources (Dict[str, Dict]): Definition of datasource that should be considered when building the
            reprozip package. When not set, all files are saved.

            secrets (List[str]): List of environment variables that should be excluded from the configuration
            file. This removal is useful when you have sensitive environment variables
            (e.g., service keys, database credentials).

        Note:
            The working directories are used in determining which are the input and output files of the experiment being
            performed. By default, only the `working_dir` directory is used. Different directories that must be
            considered are declared through the `additional_working_directories` argument.
        """
        self._reprofiles_directory = reprofiles_directory
        self._metadata_dir = os.path.join(working_dir, EnvironmentConfig.REPROPACK_BASE_PATH)

        self._datasources = datasources
        self._additional_working_directories = (
            [working_dir, *additional_working_directories] if additional_working_directories else [working_dir]
        )

        self._secrets = secrets
        self._graph_manager = self._load_graph_manager()  # what about this ?

    @property
    def graph_manager(self):
        """Return a copy of the ExecutionGraphManager object used by the ExecutionEngine instance."""
        return copy.deepcopy(self._graph_manager)

    def _save_graph_manager(self):
        """Save the Execution Graph Manager linked to the executions."""
        GraphPersistencePickle.save_graph(self._graph_manager.graph, self._metadata_dir)

    def _load_graph_manager(self) -> ExecutionGraphManager:
        """Load the Execution Graph Manager linked to the executions.

        Returns:
            ExecutionGraphManager: Execution graph.
        """
        return ExecutionGraphManager(GraphPersistencePickle.load_graph(self._metadata_dir))

    def _remove_unused_execution_files(self):
        """Remove execution files that are not linked to any vertex."""
        # get files from execution directory
        execution_files_stored_dir = os.path.join(self._metadata_dir, EnvironmentConfig.REPROPACK_EXEC_PATH)
        execution_files_stored = os.listdir(execution_files_stored_dir)

        # get the registered files
        execution_files_valid_on_graph = self._graph_manager.to_frame(dim="vertex")
        execution_files_valid_on_graph = execution_files_valid_on_graph["repropack"]

        # only the basename
        execution_files_stored = list(map(os.path.basename, execution_files_stored))
        execution_files_valid_on_graph = list(map(lambda x: x.split(os.sep)[-2], execution_files_valid_on_graph))

        # get the symmetric difference to define the files to remove
        execution_files_to_remove = set(execution_files_stored).symmetric_difference(
            set(execution_files_valid_on_graph))

        # remove the files
        for execution_file in execution_files_to_remove:
            shutil.rmtree(
                os.path.join(execution_files_stored_dir, execution_file)
            )

    def remake(self):  # what about this name ?
        """Remake the execution graph where vertices is `outdated`."""
        for vertex_index in self._graph_manager.graph.topological_sorting(mode="out"):
            vertex = self._graph_manager.graph.vs[vertex_index]

            if vertex["status"] == VertexStatus.Outdated:
                self.execute(vertex["command"], check_graph_status=False)

    def delete_execution(self, command: str, include_neighbors: bool = True) -> None:
        """Delete a already registered execution.

        Delete a previously registered command from the execution graph. For deletion, two operations modes
        are available:

          1. Deletion of a node from the graph
            > For this case, you must then check which nodes have inconsistencies that need to be fixed.

          2. Deletion of a node and its entire neighborhood
            > Unlike the previous mode, the deletion of the node is done considering its neighborhood, avoiding
              inconsistency problems.

        Args:
            command (str): User Defined Command that will be executed and registered.

            include_neighbors (bool): Flag indicating whether the exclusion of the node's neighborhood should
            be considered. When active, the function represents operation `mode 2`; otherwise, operation
            `mode 1` is assumed.

        Returns:
            None: Updates are made to the execution graph.
        """
        # prepare command and delete the vertex!
        command = command.split()
        self._graph_manager.delete_vertex(command, include_neighbors)

        # save execution graph
        self._save_graph_manager()

        # removing old execution files
        self._remove_unused_execution_files()

    def execute(self, command: Tuple[str], check_graph_status: bool = True) -> None:
        """Execute a User Defined Command with ReproZip Trace System.

        Args:
            command (Tuple): User Defined Command that will be executed and registered.

            check_graph_status (bool): Flag to indicate whether it is necessary to validate the graph before
            execution. A graph is valid when all registered execution nodes have
            `bdcrrm_api.graph.VertexStatus.Updated` status.

        Returns:
            None: The execution information is saved directly in the execution graph.
        """
        if check_graph_status and self._graph_manager.is_outdated:
            raise RuntimeError("There are runs that are outdated. Please check the execution graph and update "
                               "it with the `remake` operation.")

        # prepare commands to execute
        binary_command = command[0]

        # execute script with ReproZip
        repropack_directory = reprozip_execute_script(self._reprofiles_directory, binary_command, command)

        reprozip_remove_environment_variables(repropack_directory, self._secrets)

        # filter reprozip config file
        unpackaged_files = filter_reprozip_config_files(repropack_directory, self._datasources,
                                                        self._graph_manager.outputs)

        # pack!
        reprozip_pack_execution(repropack_directory)

        # store reprozip execution into the execution graph
        execution_metadata = reprozip_execution_metadata(repropack_directory, self._additional_working_directories)
        self._graph_manager.add_vertex(**execution_metadata)

        # save execution graph
        self._save_graph_manager()

        # save unpackaged files
        FilesPersistencePickle.save_files(unpackaged_files, self._metadata_dir)

        # removing old execution files
        self._remove_unused_execution_files()

    def _reproduce_operator(self, vertex, previous_output_files: List[str] = [],
                            missing_inputs_to_upload: Dict = {},
                            missing_environment_variables: List[str] = []) -> List[str]:
        """Execute the operations for experiment reproduction.

        Args:
            vertex (igraph.Vertex): Vertex that should be executed.

            previous_output_files (List[str]): List of the previous output steps files (For each file a relative or full
                                               path is expected.

            missing_inputs_to_upload (Dict): Dictionary with reference to the files that should be considered as input
            for the reproduction.

            missing_environment_variables (List[str]): List of environment variables that should be added on the
            experiment environment before reproduction.

        Returns:
            List: List of generated outputs.
        """
        current_directory = os.getcwd()  # is assumed that the execution will be in the project directory.

        print(f"Reproducing: {vertex['command']}")
        print(f"Checksum: {vertex['command_checksum']}")

        # setup the experiment using the reprounzip
        experiment_reproduction_path = os.path.join(mkdtemp(), "reproduction")
        reprounzip_setup(vertex["repropack"], experiment_reproduction_path)

        # defining the extras environment variables
        if missing_environment_variables:
            reprounzip_add_environment_variables(experiment_reproduction_path, missing_environment_variables)

        # upload missing input files (removed on experiment export with `datasources` options)
        vertex_inputs_to_define_files = []
        if missing_inputs_to_upload:
            vertex_inputs_to_define_files = list(map(os.path.basename, vertex["inputs_to_define"]))
            vertex_inputs_to_define_files = (
                list(map(
                    lambda x: x["target"],
                    filter(
                        lambda x: os.path.basename(x["target"]) in vertex_inputs_to_define_files,
                        missing_inputs_to_upload["files"]
                    )
                ))
            )

            # In case of a difference, the reproduction is not possible,
            # since the files for the experiment are missing
            if vertex["inputs_to_define"].difference(vertex_inputs_to_define_files):
                raise RuntimeError("You cannot run the experiment, there are input files that need to be defined. "
                                   "Check out the input file.")

        # upload previous step generated files as input to currently step
        vertex_input_files = []
        if previous_output_files:
            vertex_input_files = list(map(os.path.basename, vertex["inputs"]))
            vertex_input_files = (
                list(filter(lambda x: os.path.basename(x) in vertex_input_files, previous_output_files))
            )
        else:
            previous_output_files = []

        # upload the required inputs
        vertex_input_files_to_upload = vertex_input_files + vertex_inputs_to_define_files

        for source_input_file in vertex_input_files_to_upload:
            target_input_file = os.path.basename(source_input_file)

            reprounzip_upload(experiment_reproduction_path, source_input_file, target_input_file)

        # execute the experiment
        reprounzip_run(experiment_reproduction_path)

        # download the results
        download_files_path = os.path.join(EnvironmentConfig.REPROPACK_RESULT_PATH, f"step_{vertex.index}")
        os.makedirs(download_files_path, exist_ok=True)

        os.chdir(download_files_path)
        try:
            reprounzip_download_all(experiment_reproduction_path)
        except:
            # The command can return status != 0 when temporary files are
            # used and were not found in the download. For now no treatment will be applied.
            # If the command has problems with different tests, the next step
            # will return errors, stopping execution of the command.
            pass

        # find output files from current directory
        previous_output_files.extend([os.path.join(download_files_path, file) for file in os.listdir()])

        # return to experiment directory
        os.chdir(current_directory)
        shutil.rmtree(experiment_reproduction_path)

        return previous_output_files

    def reproduce(self, missing_inputs_to_upload: Dict = None, missing_environment_variables: List[str] = None,
                  processors: int = 4, processor_mode: str = None) -> None:
        """Reproduce each of the operations of the execution graph in an isolated environment.

        Args:
            missing_inputs_to_upload (Dict): Dictionary with reference to the files that should be considered as input
            for the reproduction. The dictionary must present the `files` and `checksum` keys, were respectively,
            `files` specifies which files should be used as input and `checksum` with the checksum of the originally
            used files. An example input file is shown below:

                {
                    "checksum": {
                        "file_1.png": "1220...",
                        ...
                    },
                    "files": [
                        {
                            "source": "file_1.png",
                            "target": "path/to/file_1.png/on/the/local/machine"
                        }
                    ]
                }

            This parameter should only be specified when the project package does not have them. Alternatively, this
            feature can be used for replication runs.

            missing_environment_variables (List[str]): List of environment variables that should be added on the
            experiment environment before reproduction.

            processors (int): Number of process used to reproduce the experiment. Only define this parameter when
                              `processor_mode` = `multiple`.

            processor_mode (str): Mode of reproduction execution. This method can assume `single` or `multiple`.

        Returns:
            None: The reproduction result will be saved on the current directory.
        """
        (
            ExecutionEngineConfig.DEFAULT_GRAPH_EXECUTOR_CLASS.make(
                self._reproduce_operator,
                self._graph_manager.graph,

                fnc_options=dict(
                    missing_inputs_to_upload=missing_inputs_to_upload,
                    missing_environment_variables=missing_environment_variables
                ),

                processor_options=dict(
                    processors=processors,
                    processor_mode=processor_mode,
                )
            )
        )


__all__ = (
    "ExecutionEngine"
)
