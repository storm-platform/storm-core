#
# This file is part of Brazil Data Cube Reproducible Research Management CLI.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Project definitions."""

import ruamel
from yamlize import Attribute, Object


class ProjectLicenses(Object):
    """Represents a project licenses."""

    code = Attribute(type=str)
    data = Attribute(type=str)
    text = Attribute(type=str)


class ProjectMetadata(Object):
    """Project metadata."""

    name = Attribute(type=str)
    description = Attribute(type=str)
    licenses = Attribute(type=ProjectLicenses)

    author = Attribute(type=str)
    creation = Attribute(type=ruamel.yaml.timestamp.TimeStamp)


class ProjectConfiguration(Object):
    """Project configuration."""

    working_directories = Attribute(type=list)
    datasources = Attribute(type=dict)


class Project(Object):
    """Represents a project."""

    metadata = Attribute(type=ProjectMetadata)
    config = Attribute(type=ProjectConfiguration)


def load_project(project_file: str) -> Project:
    """Load the settings file of a bdcrrm project.

    Args:
        project_file (str): Path to the `YAML` project file to load.

    Returns:
        Project: The loaded project.

    Raises:
        Exception: If the project file cannot be loaded.
    """
    with open(project_file, "r") as stream:
        return Project.load(stream)


def dump_project(project: Project, file: str) -> None:
    """Load the settings file of a bdcrrm project.

    Args:
        project (Project): The project to dump.

        file (str): Path to the `YAML` project file to dump.

    Returns:
        None: The project is dumped to the file.

    Raises:
        Exception: If the project file cannot be dumped.
    """
    with open(file, "w") as stream:
        return Project.dump(project, stream)


__all__ = (
    "Project",
    "ProjectMetadata",
    "ProjectLicenses",
    "ProjectConfiguration",

    "load_project",
    "dump_project",
)
