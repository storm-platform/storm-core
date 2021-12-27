# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

import os
import uuid

from .base import (
    ReproducibleJob,
    JobResult,
    JobStatus,
)

from ...reprozip import reprozip_execute_script


def _generate_uuid() -> str:
    """Generate a valid UUID4."""
    return str(uuid.uuid4())


class CommandJob(ReproducibleJob):
    def __init__(self, command, output_directory: str = None, execution_id=None):
        self._execution_id = execution_id or _generate_uuid()

        self._command = command
        self._output_directory = output_directory or ""

    @property
    def execution_id(self):
        return self._execution_id

    @property
    def command(self):
        return self._command

    @property
    def output_directory(self):
        return os.path.join(self._output_directory, self._execution_id)

    @output_directory.setter
    def output_directory(self, value):
        self._output_directory = value

    def submit(self, **kwargs) -> JobResult:
        message = "Successfully Finished!"
        job_status = JobStatus.SUCCESSFULLY

        execution_compendium_directory = None

        try:
            execution_compendium_directory = reprozip_execute_script(
                self.output_directory,
                self.command.binary_executor,
                self.command.command,
            )
        except RuntimeError as error:
            error = str(error)

            job_status = JobStatus.ERROR
            message = f"An error occurred when running the job: {error}"

        return JobResult(
            self._execution_id,
            job_status,
            message,
            execution_compendium_directory,
            self._command,
        )
