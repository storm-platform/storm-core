#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Command-Line Interface for Project management."""

import click
import rich
import rich.markdown

from .project_graph import graph
from .project_inputs import inputs
from .project_settings import settings
from .utils import load_currently_project, load_currently_execution_engine
from ..graphics import aesthetic_print
from ..graphics.graph import show_ascii_execution_graph
from ...config import EnvironmentConfig

TEMPLATE_REPOSITORY = "https://github.com/M3nin0/bdcrrm-project-cookiecutter"


@click.group(name="project")
def project():
    """Project management commands."""


@project.command(name="init")
def project_init():
    """Initialize a new Brazil Data Cube Reproducible Research project."""
    from cookiecutter.main import cookiecutter

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Project initialization", 3)

    gretting_message = """
    Welcome to [bold cyan]bdcrrm-api[/bold cyan]. This tool aims to enhance the reproducibility
    of scientific experiments performed with different programming languages and computational
    resources. Created on the shoulder of giants like [bold cyan]ReproZip[/bold cyan],
    this tool seeks to facilitate managing multiple runs and the high variability of computing environments.

    This program is in an [bold red]experimental[/bold red] stage, so if you find any problems,
    please report them and help us to improve this tool. To contact us, you can use the following links:

        - [bold]Github[/bold]: [blue]https://github.com/brazil-data-cube/bdcrrm-api[/blue];
        - [bold]Issues[/bold]: [blue]https://github.com/brazil-data-cube/bdcrrm-api/issues[/blue].

    Now, let's get to creating your project...
    """
    aesthetic_print(gretting_message, 2)
    cookiecutter(TEMPLATE_REPOSITORY)

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Finished!", 0)


@project.group(name="shipment")
def project_shipment():
    """Commands to ship the current project."""


@project_shipment.command(name="import")
@click.option("-f", "--project-file", required=True,
              help="BagIt zip file with the project files that will be imported.")
@click.option("-d", "--output-dir", required=True,
              help="Directory where the restored project will be stored.")
@click.option("--checksum-processors", default=1,
              help="Number of processes used to calculate the files checksum during the exporting.")
def project_import(project_file, output_dir, checksum_processors):
    """Import a finalized project to reproduce and explore it."""
    from ...persistence import BagItExporter

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Project Import", 1)
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Validating the files and importing the project...", 2)

    info = ()
    try:
        info = BagItExporter.load_bagit(project_file, output_dir, checksum_processors)
    except BaseException as e:
        aesthetic_print("[bold red]bdcrrm-cli[/bold red]: There was an import error", 0)
        aesthetic_print(f"[bold red]bdcrrm-cli[/bold red]: {str(e)}", 0)

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: The project was been imported!", 0)
    aesthetic_print(f"[bold cyan]bdcrrm-cli[/bold cyan]: The {info[0].metadata.name} project is "
                    f"available on: {info[1]}", 0)

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Finished!", 0)


@project_shipment.command(name="export")
@click.option("-o", "--output-dir", required=True, help="Directory where the project will be exported.")
@click.option("--checksum-processors", default=1,
              help="Number of processes used to calculate the files checksum during the exporting.")
def project_export(output_dir, checksum_processors):
    """Export a finalized project."""
    from ...persistence import BagItExporter

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Project Export", 1)

    currently_project = load_currently_project()
    execution_manager = load_currently_execution_engine()

    # check if the graph is outdated
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Validating the project...", 1)
    continue_with_outdated = True

    graph_manager = execution_manager.graph_manager
    if graph_manager.is_outdated:
        aesthetic_print("[bold red]bdcrrm-cli[/bold red]: Problems founded")
        aesthetic_print(rich.markdown.Markdown("There are nodes in the execution graph that are `outdated`. This can "
                                               "cause **problems** for the reproducibility of the project. You really "
                                               "want to continue the exporting process ? If needed, you can update the"
                                               "nodes using the `bdcrrm-cli production remake` command."))
        continue_with_outdated = click.confirm("")

    if continue_with_outdated:
        aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Exporting the project!", 2)

        # Export all project elements
        BagItExporter.save_bagit(currently_project.metadata.name, EnvironmentConfig.REPROPACK_BASE_PATH, output_dir,
                                 checksum_processors)

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Finished!", 0)


@project.command(name="info")
@click.option("--graph", required=False, is_flag=True, default=False,
              help="Flag to indicate that the generated graph with the runs should be displayed.")
def project_show(graph: bool):
    """Show general details about the current project."""
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Project details", 1)

    currently_project = load_currently_project()

    aesthetic_print(f"[bold]Name[/bold]:\n\t {currently_project.metadata.name}", 0)
    aesthetic_print(f"[bold]Description[/bold]:\n\t {currently_project.metadata.description}", 0)

    aesthetic_print(
        f"[bold]Author[/bold]:\n\t {currently_project.metadata.author} ({currently_project.metadata.author_email})", 0
    )
    aesthetic_print(f"[bold]Created at[/bold]:\n\t {currently_project.metadata.creation}", 0)

    if graph:
        execution_manager = load_currently_execution_engine()

        aesthetic_print("[bold]Execution Graph[/bold]: ", 0)
        show_ascii_execution_graph(execution_manager.graph_manager.graph)


# add graph commands to the project group
project.add_command(graph)

# add inputs commands to the project group
project.add_command(inputs)

# add settings command to the project group
project.add_command(settings)
