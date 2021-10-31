#
# This file is part of SpatioTemporal Open Research Manager Core.
# Copyright (C) 2021 INPE.
#
# SpatioTemporal Open Research Manager Core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

import os
import shutil
from abc import ABC, abstractmethod
from tempfile import mkdtemp
from typing import List, Dict

import base32_lib as base32

from ....helper.hasher import check_checksum, hash_file
from ....reprozip import (reprozip_execute_script, reprounzip_setup, reprounzip_add_environment_variables,
                          reprounzip_run_docker_container, reprozip_get_output_files,
                          reprounzip_download_file)


class JobStatus:
    ERROR = False
    SUCCESSFULLY = True


class JobResult:
    def __init__(self, execution_id: str, status: bool, message: str,
                 environment_descriptors_dir=None, command=None, **execution_results):
        self._status = status
        self._message = message
        self._command = command
        self._execution_id = execution_id
        self._environment_descriptors_dir = environment_descriptors_dir

        self._execution_results = execution_results

    @property
    def execution_message(self):
        return self._message

    @property
    def command(self):
        return self._command

    @property
    def has_error(self):
        return not self._status

    @property
    def execution_id(self):
        return self._execution_id

    @property
    def environment_descriptors_dir(self):
        return self._environment_descriptors_dir  # ToDo: Improve the abstraction

    @property
    def execution_results(self):
        return self._execution_results

    @execution_results.setter
    def execution_results(self, results: Dict):
        self._execution_results = results


class ReproducibleJob(ABC):

    @property
    @abstractmethod
    def execution_id(self):
        pass

    @property
    @abstractmethod
    def command(self):
        pass

    @property
    @abstractmethod
    def output_directory(self):
        pass

    @abstractmethod
    def submit(self, **kwargs) -> JobResult:
        pass


class CommandJob(ReproducibleJob):

    def __init__(self, command, output_directory: str, execution_id=None):
        self._execution_id = execution_id or base32.generate(length=10, split_every=0, checksum=True)

        self._command = command
        self._output_directory = output_directory

    @property
    def execution_id(self):
        return self._execution_id

    @property
    def command(self):
        return self._command

    @property
    def output_directory(self):
        return os.path.join(self._output_directory, self._execution_id)

    def submit(self, **kwargs) -> JobResult:
        message = "Successfully Finished!"
        job_status = JobStatus.SUCCESSFULLY

        execution_compendium_directory = None

        try:
            execution_compendium_directory = reprozip_execute_script(self.output_directory,
                                                                     self._command.binary_executor,
                                                                     self._command.command)
        except RuntimeError as error:
            error = str(error)

            job_status = JobStatus.ERROR
            message = f"An error occurred when running the job: {error}"

        return JobResult(self._execution_id, job_status, message, execution_compendium_directory, self._command)


class CompendiumJob(ReproducibleJob):

    def __init__(self, compendium, output_directory: str):
        self._compendium = compendium
        self._output_directory = output_directory

    @property
    def execution_id(self):
        return self._compendium.name

    @property
    def command(self):
        return self._compendium.command

    @property
    def output_directory(self):
        return os.path.join(self._output_directory, self.execution_id)

    def submit(self, **kwargs) -> JobResult:
        """Execute the operations for experiment reproduction.

        Args:

            TODo:
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
        message = "Successfully Finished!"
        job_status = JobStatus.SUCCESSFULLY

        # retrieving inputs
        required_data_objects = kwargs.get("required_data_objects", [])
        previous_output_files = kwargs.get("previous_output_files", [])
        required_environment_variables = kwargs.get("required_environment_variables", [])

        # validating the package checksum
        compendium_package = self._compendium.compendium_package
        check_checksum(compendium_package["key"], compendium_package["checksum"], compendium_package["algorithm"])

        # setup the experiment using the reprounzip
        experiment_reproduction_path = os.path.join(mkdtemp(), "reproduction")
        reprounzip_setup(compendium_package["key"], experiment_reproduction_path, "docker")

        # defining the extras environment variables
        if required_environment_variables:
            reprounzip_add_environment_variables(experiment_reproduction_path, required_environment_variables)

        # upload missing input files (removed on experiment export with `datasources` options)
        vertex_inputs_to_define_files = []
        if required_data_objects:
            # extracting checksum and file paths
            required_objects_checksums = required_data_objects["checksum"]
            compendium_external_inputs_required_checksum = self._compendium.metadata.get("external_inputs_required", [])

            required_objects_checksum_list = list(
                map(lambda x: required_objects_checksums[x["source"]], required_data_objects["files"])
            )

            # comparison between user and compendium inputs by checksum
            vertex_inputs_to_define_files = (
                list(map(
                    lambda x: {"key": x["target"], "checksum": required_objects_checksums[x["source"]]},
                    filter(
                        lambda x: required_objects_checksums[
                                      x["source"]] in compendium_external_inputs_required_checksum,
                        required_data_objects["files"]
                    )
                ))
            )

            # In case of a difference, the reproduction is not possible,
            # since the files for the experiment are missing
            if set(compendium_external_inputs_required_checksum).difference(required_objects_checksum_list):
                job_status = JobStatus.ERROR
                message = ("You cannot run the experiment, there are input files that need to be defined. "
                           "Check out the input file.")

        if job_status:
            # select the previous step generated files to use as input to currently step
            vertex_input_files = []
            if previous_output_files:
                vertex_input_files = list(map(lambda file: file["checksum"], self._compendium.inputs))
                vertex_input_files = (
                    list(filter(lambda x: x["checksum"] in vertex_input_files, previous_output_files))
                )
            else:
                previous_output_files = []

            # upload the required inputs
            required_input_objects = vertex_input_files + vertex_inputs_to_define_files

            # creating the docker volume for each required input data defined
            volume_options = []
            for required_input_object in required_input_objects:
                # search for the object checksum into the compendium inputs
                original_input_file = list(filter(
                    lambda x: x["checksum"] in required_input_object["checksum"], self._compendium.inputs
                ))

                if original_input_file:
                    original_input_file = original_input_file[0]

                    volume_options.append(f"{required_input_object['key']}:{original_input_file['key']}:ro")

            # execute the experiment
            reprounzip_run_docker_container(experiment_reproduction_path, volume_options)

            # download the results
            download_files_path = os.path.join(self._output_directory, self._compendium.name)
            os.makedirs(download_files_path, exist_ok=True)

            # downloading experiment result
            experiment_output_files = reprozip_get_output_files(experiment_reproduction_path)

            for experiment_output_file in experiment_output_files:
                try:
                    reprounzip_download_file(experiment_reproduction_path,
                                             experiment_output_file,
                                             download_files_path,
                                             "docker")
                except:
                    # The command can return status != 0 when temporary files are
                    # used and were not found in the download. For now no treatment will be applied.
                    # If the command has problems with different tests, the next step
                    # will return errors, stopping execution of the command.
                    pass

            # find output files from current directory
            generated_files = [os.path.join(download_files_path, file) for file in experiment_output_files]
            generated_files_checksum = [
                hash_file(f, self._compendium.compendium_package["algorithm"]) for f in generated_files
            ]

            previous_output_files.extend(generated_files_checksum)

        # remove temporary reproduction directory
        shutil.rmtree(experiment_reproduction_path)

        return JobResult(self.execution_id, job_status, message,
                         previous_output_files=previous_output_files, compendium=self._compendium)


__all__ = (
    "JobStatus",
    "JobResult",

    "ReproducibleJob",

    "CommandJob",
    "CompendiumJob"
)
