#
# This file is part of Brazil Data Cube Reproducible Research Management CLI.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Command-Line Interface Operations."""

import os

import click

from ..project import Project
from ..config import EnvironmentConfig, ProjectConfig


def get_project_file() -> str:
    """Return the project file path.
    
    Returns:
        str: Project file path.
    """

    return os.path.join(
        EnvironmentConfig.REPROPACK_BASE_PATH, ProjectConfig.PROJECT_DEFAULT_FILENAME
    )


def check_if_project_is_valid():
    """Checks that the commands are being executed in a directory of a valid bdcrrm project.
    
    Raises:
        click.FileError: If the project file is not valid.
    """

    # try to find the project definition file
    project_file = get_project_file()

    if not os.path.isfile(project_file):
        raise click.FileError(
            "The project file does not exist. " +
            f"To create one, please use the `bdcrrm-cli project init` command."
        )


def load_project() -> Project:
    """Load Project file.

    Returns:
        Project: Project object.

    Raises:
        click.FileError: If the project file is not valid
    """
    from ..project import load_project

    # raises an exception if the project file is not valid
    check_if_project_is_valid()

    # load the project file
    return load_project(get_project_file())
