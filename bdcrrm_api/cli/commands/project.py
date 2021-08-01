#
# This file is part of Brazil Data Cube Reproducible Research Management CLI.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Command-Line Interface for Project management."""

from datetime import datetime

import click

from .project_graph import graph
from .project_inputs import inputs
from .utils import load_currently_project, load_currently_execution_engine
from ..graphics.graph import show_ascii_execution_graph
from ...config import EnvironmentConfig

TEMPLATE_REPOSITORY = "https://github.com/M3nin0/bdcrrm-project-cookiecutter"


@click.group(name="project")
def project():
    """Project commands."""


@project.group(name="management")
def project_management():
    """Project management commands."""


@project_management.command(name="init")
def project_init():
    """Initialize a new Brazil Data Cube Reproducible Research project."""
    from cookiecutter.main import cookiecutter

    cookiecutter(TEMPLATE_REPOSITORY, extra_context={
        "timestamp": datetime.utcnow().isoformat()
    })


@project_management.command(name="import")
@click.option("-f", "--project-file", required=True,
              help="BagIt zip file with the project files that will be imported.")
@click.option("-d", "--output-dir", required=True,
              help="Directory where the restored project will be stored.")
@click.option("--checksum-processors", default=1,
              help="Number of processes used to calculate the files checksum during the exporting.")
def project_import(project_file, output_dir, checksum_processors):
    """Import a finalized project to reproduce and explore."""
    from ...persistence import BagItExporter

    click.secho("Importing project files...", bold=True)
    info = BagItExporter.load_bagit(project_file, output_dir, checksum_processors)

    click.secho(f"{info[0]} imported!")
    click.secho(f"The {info[0]} project is available on: {info[1]}")


@project_management.command(name="export")
@click.option("-o", "--output-dir", required=True, help="output directory.")
@click.option("--checksum-processors", default=1,
              help="Number of processes used to calculate the files checksum during the exporting.")
def project_export(output_dir, checksum_processors):
    """Export project to a directory."""
    from ...persistence import BagItExporter

    currently_project = load_currently_project()

    # Export all project elements
    BagItExporter.save_bagit(currently_project.metadata.name, EnvironmentConfig.REPROPACK_BASE_PATH, output_dir,
                             checksum_processors)


@project.command(name="info")
@click.option("--graph", required=False, is_flag=True, default=False,
              help="Flag to indicate that the generated graph with the runs should be displayed.")
def project_show(graph: bool):
    """Show project details."""
    currently_project = load_currently_project()

    click.secho("Project details", bold=True)
    click.secho("----------------", bold=True)

    click.secho("Name:", bold=True)
    click.secho(f"    {currently_project.metadata.name}")

    click.secho("Description:", bold=True)
    click.secho(f"    {currently_project.metadata.description}")

    click.secho("Author:", bold=True)
    click.secho(f"    {currently_project.metadata.author}")

    click.secho("Created:", bold=True)
    click.secho(f"    {currently_project.metadata.creation}")

    if graph:
        execution_manager = load_currently_execution_engine()

        click.secho("Execution Graph:", bold=True)
        show_ascii_execution_graph(execution_manager.graph_manager.graph)


# add graph commands to the project group
project.add_command(graph)

# add inputs commands to the project group
project.add_command(inputs)
