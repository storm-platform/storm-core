# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from abc import ABC, abstractmethod

from ....reprozip import (
    reprozip_remove_environment_variables,
    filter_reprozip_config_files,
)


class InspectorComponent(ABC):
    """Inspector component class.

    A Inspector Component provides methods to change
    data formats, environment variables and other data
    elements of the base reproducible bundle.
    """

    @abstractmethod
    def inspect_data_files(
        self, job_result=None, states=None, files_config=None, **kwargs
    ):
        """Inspect and change the compendium data files.

        Args:
            job_result (JobResult): JobResult object.

            states (dict): Dict with the execution engine states.

            files_config (ExecutionEngineFilesConfig): Execution engine files definitions.
        """
        pass

    @abstractmethod
    def inspect_environment_variables(
        self, job_result=None, states=None, files_config=None, **kwargs
    ):
        """Inspect and change the compendium environment variables.

        Args:
            job_result (JobResult): JobResult object.

            states (dict): Dict with the execution engine states.

            files_config (ExecutionEngineFilesConfig): Execution engine files definitions.
        """
        pass


class InspectorFileRemoverComponent(InspectorComponent):
    """File Remover component class.

    This ``Inspector Component`` class provides methods to remove
    files from the reproducible bundle.
    """

    def inspect_data_files(
        self, job_result=None, states=None, files_config=None, **kwargs
    ):
        """Inspect and change the compendium data files."""
        previous_output = states["generated_outputs"]
        data_directories = files_config.data_objects

        execution_compendium_path = job_result.environment_description_data

        files_not_packaged = filter_reprozip_config_files(
            execution_compendium_path, data_directories, previous_output
        )
        return {"unpacked_files": files_not_packaged}

    def inspect_environment_variables(
        self, job_result=None, states=None, files_config=None, **kwargs
    ):
        """Inspect and change the compendium environment variables."""

        execution_compendium_path = job_result.environment_description_data
        ignored_environment_variables = files_config.ignored_environment_variables

        unpacked_env = reprozip_remove_environment_variables(
            execution_compendium_path, ignored_environment_variables
        )
        return {"unpacked_environment_variables": unpacked_env}
