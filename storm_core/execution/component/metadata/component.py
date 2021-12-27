# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from abc import ABC, abstractmethod

from ....helper.hasher import hash_file
from ....reprozip import reprozip_execution_metadata


class MetadataComponent(ABC):
    """Metadata Builder component class.

    A Metadata Builder provides methods to
    extract metadata from the reproducible bundle
    and the job result.

    Note:
        No files should be modified with this type
        of component.
    """

    @abstractmethod
    def do_metadata(self, job_result=None, states=None, files_config=None, **kwargs):
        """Extract metadata from the Job Execution related objects and files.

        Args:
            job_result (JobResult): JobResult object.

            states (dict): Dict with the execution engine states.

            files_config (ExecutionEngineFilesConfig): Execution engine files definitions.
        """
        pass


class FileChecksumMetadataComponent(MetadataComponent):
    """File checksum component.

    This ``Metadata Builder Component`` class provides methods
    to calculate the checksum of the processed files.
    """

    def do_metadata(self, job_result=None, states=None, files_config=None, **kwargs):
        """Extract metadata from the Job Execution related objects and files."""
        hasher_algorithm = files_config.files_checksum_algorithm
        working_directory = files_config.working_directory
        ignored_data_objects = files_config.ignored_data_objects

        execution_compendium_path = job_result.environment_description_data

        package_metadata = reprozip_execution_metadata(
            execution_compendium_path, working_directory, ignored_data_objects
        )

        result = {"inputs": [], "outputs": []}
        for file_type in result.keys():
            for file in package_metadata[file_type]:
                result[file_type].append(hash_file(file, hasher_algorithm))
        return result
