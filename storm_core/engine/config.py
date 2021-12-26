# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Execution engine configurations."""

from pathlib import Path
from typing import List, Union, Dict

from .executor.backends.base import GraphExecutor


class ExecutionEngineServicesConfig:
    """Execution engine services configuration.

    To execute the jobs, handle data, and control
    the user's actions, the ``Execution Engine``
    uses other components services. This class
    provides a way to define and configure these
    services.
    """

    def __init__(self, graph_executor: GraphExecutor):
        """Initializer.

        Args:
            graph_executor (GraphExecutor): Graph Executor service object.
        """
        self._graph_executor = graph_executor

    @property
    def graph_executor(self):
        """Execution Engine Graph Executor."""
        return self._graph_executor


class ExecutionEngineFilesConfig:
    """Execution engine files configuration.

    A ``Execution Engine`` handles all data
    (e.g., files, directories, environment
    variables, and others) used in the user's
    experiment. In some cases, it is necessary
    to change the handle data rules to avoid
    problems with Big Data Sharing in a
    compendium or data leak.

    This class provides a way to configure
    the file's definition used in the
    ``Execution Engine``.
    """

    def __init__(
        self,
        working_directory: Union[str, Path],
        storage_dir: Union[str, Path],
        data_objects: Dict[str, Dict] = None,
        ignored_data_objects: Dict[str, str] = None,
        ignored_environment_variables: List[str] = None,
        files_checksum_algorithm: str = "md5",
    ):
        """Initializer.

        Args:
            working_directory (Union[str, Path]): Directory where the execution engine will be executed.

            storage_dir (Union[str, Path]): Directory where the execution engine will be save the executed compendia.

            data_objects (Dict[str, Dict]): Dictionary with the definition of directories and files that should
            be added/removed from/to the compendia. To declare if a file should be added or excluded, use the Python
            ``fnmatch`` expressions. For example, to ``include`` all ``yaml`` files in the ``/data`` directory,
            you can use a ``dict`` in the following format::

                    ```
                        # Template:

                        filter_data_objects = {
                            <filter-name>: {
                                "pattern": "<fnmatch-pattern>,
                                "action": "include/exclude"
                            }
                        }

                        # Usage:

                        filter_data_objects = {
                            "data-add": {
                                "pattern": "/data/*,
                                "action": "include"
                            }
                        }
                    ```

            ignored_data_objects (Dict[str, str]): Dictionary with the definition of directories and files that should
            be excluded from the ``inputs/outputs`` metadata definition. You can use this argument to remove files
            like python modules scripts or cache files loaded (which sometimes is detected as ``input``, for example).

            ignored_environment_variables (List[str]): List with the environment variables that must be removed from the
            reproducible bundle.

            files_checksum_algorithm (str): Checksum algorithm used to identify the files (default md5). This
            implementation is provided by the ``Storm Hasher``.

        Note:
            The ``working_directory`` argument is used to filter system files used by the
            scripts to process the data. For example, when the ``working_directory`` is
            the directory ``/my-workdir``, all files outside this directory will not be
            included in the reproducible bundle.

            You can use the ``data_objects`` argument to work with multiple directories.

        Note:
            ``filter_data_objects`` only filter the data saved in the reproducible bundle.
            This parameter does not change the ``inputs/outputs`` metadata created during the
            execution.

        See:
            ``fnmatch`` official documentation: <https://docs.python.org/3/library/fnmatch.html>

        See:
            ``Storm Hasher official documentation: <https://github.com/storm-platform/storm-hasher>
        """

        self._storage_dir = Path(storage_dir)
        self._working_directory = Path(working_directory)

        self._data_objects = data_objects or {}
        self._ignored_data_objects = ignored_data_objects or {}

        self._files_checksum_algorithm = files_checksum_algorithm
        self._ignored_environment_variables = ignored_environment_variables or []

        # creating the defined directories
        self._storage_dir.mkdir(exist_ok=True, parents=True)
        self._working_directory.mkdir(exist_ok=True, parents=True)

    @property
    def working_directory(self):
        """Execution engine working directory."""
        return str(self._working_directory)

    @property
    def storage_dir(self):
        """Execution engine storage directory."""
        return str(self._storage_dir)

    @property
    def data_objects(self):
        """Data objects added/excluded to/from the compendia."""
        return self._data_objects

    @property
    def files_checksum_algorithm(self):
        """Execution engine checksum algorithm."""
        return self._files_checksum_algorithm

    @property
    def ignored_data_objects(self):
        """Execution engine ignored data objects."""
        return self._ignored_data_objects

    @property
    def ignored_environment_variables(self):
        """Execution engine ignored environment variables."""
        return self._ignored_environment_variables


__all__ = (
    "ExecutionEngineFilesConfig",
    "ExecutionEngineServicesConfig",
)
