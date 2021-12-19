# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from copy import deepcopy
from typing import Dict, List

from ..helper.hasher import hash_file

from .inspector.inspector import Inspector
from .inspector.config import InspectorConfig

from .metadata.builder import MetadataBuilder
from .metadata.config import MetadataBuilderConfig
from .metadata.components import IOMetadataComponent

from ..reprozip import reprozip_pack_execution
from .executor.api import ReproducibleJob, ExecutionPlan, JobResult

from .config import ExecutionEngineFilesConfig, ExecutionEngineServicesConfig


class ExecutionEngine:
    """Execution Engine."""

    def __init__(
        self,
        services_config: ExecutionEngineServicesConfig,
        files_config: ExecutionEngineFilesConfig,
    ):
        """Initialize execution engine."""
        self._files_config = files_config
        self._services_config = services_config

        self._states = {"generated_outputs": []}

    @property
    def files_config(self):
        return deepcopy(self._files_config)  # "read-only"

    @property
    def services_config(self):
        return deepcopy(self._services_config)  # "read-only"

    def _operator_execution(self, job, **kwargs) -> JobResult:
        # executing
        job_result = job.submit()

        # inspecting the files, environment variables and other things from the execution result
        inspector = Inspector(InspectorConfig)

        # extracting output files
        io_metadata = IOMetadataComponent().do_metadata(
            ignored_objects=self._files_config.ignored_objects,
            working_directory=self._files_config.working_directory,
            execution_compendium_path=job_result.environment_descriptors_dir,
        )
        self._states["generated_outputs"] = list(
            {*self._states["generated_outputs"], *io_metadata["outputs"]}
        )

        inspected_files = inspector.run_components(
            previous_outputs=self._states["generated_outputs"],
            data_directories=self._files_config.data_storage,
            execution_compendium_path=job_result.environment_descriptors_dir,
            environment_variables_to_remove=self._files_config.environment_variables_to_remove,
        )

        # packing the files
        package_file = reprozip_pack_execution(job_result.environment_descriptors_dir)
        package_file = hash_file(package_file, self._files_config.checksum_algorithm)

        # generating the full execution metadata
        metadata_builder = MetadataBuilder(MetadataBuilderConfig)
        metadata = metadata_builder.run_components(
            ignored_objects=self._files_config.ignored_objects,
            working_directory=self._files_config.working_directory,
            algorithm_checksum_files=self._files_config.checksum_algorithm,
            execution_compendium_path=job_result.environment_descriptors_dir,
        )

        # adding removed files to the metadata
        metadata = {**metadata, "others": inspected_files}

        job_result.execution_results = {
            **job_result.execution_results,
            **{"compendium_package": package_file, "metadata": metadata},
        }

        return job_result

    def _operator_reproduce(self, job: ReproducibleJob, **kwargs) -> JobResult:
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

    def execute(self, execution_plan: ExecutionPlan) -> List[JobResult]:
        """Execute a User Defined Command with ReproZip Trace System.

        Args:
            execution_plan (ExecutionPlan): User Defined Command that will be executed and registered. TODO

        Returns:
            None: The execution information is saved directly in the execution graph.  TODO
        """

        return self._services_config.graph_executor.map_execution(
            self._operator_execution, execution_plan
        )

    def reproduce(
        self,
        execution_plan: ExecutionPlan,
        required_data_objects: Dict = {},
        required_environment_variables: List[str] = [],
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
            self._operator_reproduce,
            execution_plan,
            fnc_options=dict(
                required_data_objects=required_data_objects,
                required_environment_variables=required_environment_variables,
            ),
        )


__all__ = "ExecutionEngine"
