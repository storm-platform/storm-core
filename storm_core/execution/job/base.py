# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from typing import Dict
from abc import ABC, abstractmethod


class JobStatus:
    ERROR = False
    SUCCESSFULLY = True


class JobResult:
    def __init__(
        self,
        execution_id: str,
        status: bool,
        message: str,
        environment_description_data=None,
        command=None,
        **execution_results,
    ):
        self._status = status
        self._message = message
        self._command = command
        self._execution_id = execution_id
        self._environment_description_data = environment_description_data

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
    def environment_description_data(self):
        return self._environment_description_data  # ToDo: Improve the abstraction

    @property
    def execution_results(self):
        return self._execution_results

    @execution_results.setter
    def execution_results(self, results: Dict):
        self._execution_results = results

    def __hash__(self):
        """hash overwritten.

        Note:
            Implementation based on Python official documentation:
            <https://docs.python.org/3.5/reference/datamodel.html#object.__hash__>
        """
        return hash(
            (
                self._status,
                self._execution_id,
                self._environment_description_data,
            )
        )

    def __eq__(self, other):
        """equal operator."""
        return (
            self._status,
            self._execution_id,
            self._environment_description_data,
        ) == (
            other._status,
            other._execution_id,
            other._environment_description_data,
        )


class ReproducibleJob(ABC):
    @property
    @abstractmethod
    def execution_id(self):
        pass

    @property
    @abstractmethod
    def command(self):
        pass

    @abstractmethod
    def submit(self, **kwargs) -> JobResult:
        pass

    @property
    @abstractmethod
    def output_directory(self):
        pass

    @output_directory.setter
    @abstractmethod
    def output_directory(self, value):
        pass
