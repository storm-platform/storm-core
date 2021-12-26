# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from copy import deepcopy
from typing import Dict, List, Callable

from ..helper.hasher import hash_file

from .component.inspector.inspector import Inspector
from .component.metadata.builder import MetadataBuilder

from .component.decorator import pass_component_executor

from .executor.api import ReproducibleJob, ExecutionPlan, JobResult
from ..reprozip import reprozip_pack_execution, reprozip_execution_metadata
from .config import ExecutionEngineFilesConfig, ExecutionEngineServicesConfig


class ExecutionEngine:
    """Execution Engine class.

    The ``Execution Engine`` provides methods to run,
    rerun and reproduce user commands.
    """

    @pass_component_executor("inspector", Inspector)
    @pass_component_executor("builder", MetadataBuilder)
    def __init__(
        self,
        services_config: ExecutionEngineServicesConfig,
        files_config: ExecutionEngineFilesConfig,
        inspector: Inspector = None,
        builder: MetadataBuilder = None,
    ):
        """Initializer.

        Args:
            services_config (ExecutionEngineServicesConfig): Configuration of the services used by the Execution Engine.

            files_config (ExecutionEngineFilesConfig): Files definitions used by the Execution Engine.

            inspector (Inspector): Component executor to handle and modify the data in the reproducible bundle.

            builder (MetadataBuilder): Component executor to build the execution metadata from the Job Results metadata
            and the reproducible bundle files.
        """
        self._files_config = files_config
        self._services_config = services_config

        # Component executors
        self._builder = builder
        self._inspector = inspector

    @property
    def files_config(self):
        """Execution engine files configurations."""
        return deepcopy(self._files_config)  # "read-only"

    @property
    def services_config(self):
        """Execution engine services configurations."""
        return deepcopy(self._services_config)  # "read-only"

    def _operator_run(self, states: Dict, **kwargs) -> Callable:
        """Clojure function to produce a function that executes User-Defined Commands.

        Args:
            states (Dict): Dict with the current execution states (e.g., Previous generated files).

        Note:
            This function produces a closure to store the execution states and makes them available to the
            execution components (Inspector and Metadata Builder) and other functions.

        Returns:
            Callable: Function to execute the User-Defined Command.
        """

        def _wrapper(job, **kwargs) -> JobResult:
            """Function to execute the User-Defined Command."""

            # configuring the job
            job.output_directory = self._files_config.storage_dir

            # executing
            job_result = job.submit()

            # inspecting the files, environment variables
            # and other things from the execution result.
            inspected_files = self._inspector.run_components(
                states=states,
                job_result=job_result,
                files_config=self._files_config,
            )

            # packing the files
            package_file = reprozip_pack_execution(
                job_result.environment_description_data
            )
            package_file = hash_file(
                package_file, self._files_config.files_checksum_algorithm
            )

            # generating the full execution metadata
            metadata = self._builder.run_components(
                states=states,
                job_result=job_result,
                files_config=self._files_config,
            )

            # adding removed files to the metadata
            metadata = {**metadata, "others": inspected_files}

            job_result.execution_results = {
                **job_result.execution_results,
                **{"compendium_package": package_file, "metadata": metadata},
            }

            return job_result

        return _wrapper

    def _operator_rerun(self, job: ReproducibleJob, **kwargs) -> JobResult:
        """Execute the operations for experiment reproduction.

        Args: TODO
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
        return job.submit(**kwargs)

    def execute(self, execution_plan: ExecutionPlan, states=None) -> List[JobResult]:
        """Execute a User Defined Command with ReproZip Trace System.

        Args:
            execution_plan (ExecutionPlan): User Defined Command that will be executed and registered. TODO

            states (Dict): Dict with the current execution states (e.g., Previous generated files).

        Returns:
            None: The execution information is saved directly in the execution graph.  TODO
        """
        return self._services_config.graph_executor.map_execution(
            self._operator_run(states), execution_plan
        )

    def reproduce(
        self,
        execution_plan: ExecutionPlan,
        required_data_objects: Dict = None,
        required_environment_variables: List[str] = None,
    ) -> List[JobResult]:
        """Reproduce each of the operations of the execution graph in an isolated environment.

        Args:
            execution_plan (ExecutionPlan): ToDo

            required_data_objects (Dict): Dictionary with reference to the files that should be considered as input
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

            required_environment_variables (List[str]): List of environment variables that should be added on the
            experiment environment before reproduction.

        Returns:
            None: The reproduction result will be saved on the current directory.
        """
        return self._services_config.graph_executor.map_reproduction(
            self._operator_rerun,
            execution_plan,
            fnc_options=dict(
                required_data_objects=required_data_objects or {},
                required_environment_variables=required_environment_variables or [],
            ),
        )
