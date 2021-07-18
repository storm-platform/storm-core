#
# This file is part of Brazil Data Cube Reproducible Research Management CLI.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Command-Line Interface Operations."""

import bagit
import os

import click

import shutil
from typing import Tuple
from tempfile import mkdtemp

from ..project import Project, load_project
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


def import_finalized_project(project_file: str, base_directory: str, processes: int = 1) -> Tuple[str, str]:
    """Import already finished `bdcrrm` project.

    Args:
        project_file (str): path to the finalized project zip file.

        base_directory (str): directory where the project will be extracted.

        processes (int): Number of processes used to validate the `bagit` file.

    Returns:
        Tuple[str, str]: Tuple with the project name and the path to the imported files.
    """

    # extract and validate bagit
    tmp_dir = mkdtemp()

    shutil.unpack_archive(project_file, tmp_dir)

    # validate bagit
    bag = bagit.Bag(tmp_dir)
    bag.validate(processes=processes)

    # load the project definition file
    exported_files = os.path.join(tmp_dir, "data")

    project_path = os.path.join(exported_files, ProjectConfig.PROJECT_DEFAULT_FILENAME)
    project_definition = load_project(project_path)

    # move to the new folder
    base_project_path = os.path.join(base_directory, project_definition.metadata.name)
    project_metadata_path = os.path.join(base_project_path, EnvironmentConfig.REPROPACK_BASE_PATH)

    shutil.move(exported_files, project_metadata_path)

    # create a simple reproduction script
    reproduction_script = os.path.join(base_project_path, "reproduce.sh")

    with open(reproduction_script, "w") as ofile:
        ofile.writelines([
            "#!/bin/bash\n",
            f"echo 'reproducing {project_definition.metadata.name}'"
            "\nbdcrrm-cli execution reproduce"
        ])
    os.chmod(reproduction_script, 0o775)

    return project_definition.metadata.name, base_project_path
