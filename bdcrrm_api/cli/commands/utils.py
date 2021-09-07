#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management API is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Command-Line Interface Operations."""

import os
from typing import Dict, Tuple

from igraph import Graph

from ...config import EnvironmentConfig, ProjectConfig
from ...engine import ExecutionEngine
from ...project import Project, dump_project, load_project


def get_project_file() -> str:
    """Return the project file path.

    Returns:
        str: Project file path.
    """
    return os.path.join(
        EnvironmentConfig.REPROPACK_BASE_PATH, ProjectConfig.PROJECT_DEFAULT_FILENAME
    )


def check_if_project_is_valid():
    """Check that the execution commands are being executed in a valid `bdcrrm` project directory.

    Raises:
        RuntimeError: If the project file is not valid.
    """
    # try to find the project definition file
    project_file = get_project_file()

    if not os.path.isfile(project_file):
        raise RuntimeError(
            "The project definition file does not exist or was not found. " +
            f"If needed, please use the `bdcrrm-cli project init` command to create a new project."
        )


def check_if_execution_command_is_valid(command: Tuple[str]):
    """Check that the execution commands are valid.

    A command that is considered valid is one that has at least one associated binary
    (with or without usage parameters).

    Raises:
        ValueError: If the command is not valid
    """
    if not command or not " ".join(command).strip():
        raise ValueError("Invalid command!")


def load_currently_graph() -> Graph:
    """Load the graph associated with the current project."""
    from ...persistence import GraphPersistencePickle
    return GraphPersistencePickle.load_graph(EnvironmentConfig.REPROPACK_BASE_PATH)


def load_currently_files() -> Dict:
    """Load the files that have been removed from the ReproZip package and are required to reproduce the experiment."""
    from ...persistence import FilesPersistencePickle
    return FilesPersistencePickle.load_files(os.path.join(os.getcwd(), EnvironmentConfig.REPROPACK_BASE_PATH))


def load_currently_project() -> Project:
    """Load Project file.

    Returns:
        Project: Project object.

    Raises:
        click.FileError: If the project file is not valid
    """
    # raises an exception if the project file is not valid
    check_if_project_is_valid()

    # load the project file
    return load_project(get_project_file())


def save_currently_project(project: Project):
    """Save Project file.

    Args:
        project (Project): Project object.
    """
    dump_project(project, get_project_file())


def load_currently_execution_engine() -> ExecutionEngine:
    """Load the ExecutionEngine of the current Project.

    Returns:
        ExecutionEngine: ExecutionEngine object.

    Raises:
        click.FileError: If the project file is not valid
    """
    project = load_currently_project()
    engine = ExecutionEngine(
        os.getcwd(),
        EnvironmentConfig.REPROPACK_BASE_PATH,
        datasources=project.config.datasources,
        additional_working_directories=project.config.working_directories,
        secrets=project.secrets
    )

    return engine


__all__ = (
    "get_project_file",

    "check_if_project_is_valid",
    "check_if_execution_command_is_valid",

    "load_currently_project",
    "load_currently_files",
    "load_currently_execution_engine",

    "save_currently_project"
)
