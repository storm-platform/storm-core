#
# This file is part of Brazil Data Cube Reproducible Research Management CLI.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Command-Line Interface."""

import os
from datetime import datetime

import click

from .operations import load_currently_project
from ..config import EnvironmentConfig

TEMPLATE_REPOSITORY = "https://github.com/M3nin0/bdcrrm-project-cookiecutter"


@click.group()
@click.version_option()
def cli():
    """Brazil Data Cube Reproducible Research Management CLI."""


@cli.group(name="project")
def project():
    """Project commands."""


@project.command(name="init")
def project_init():
    """Initialize a project."""
    from cookiecutter.main import cookiecutter

    cookiecutter(TEMPLATE_REPOSITORY, extra_context={
        "timestamp": datetime.utcnow().isoformat()
    })


@project.command(name="import")
@click.option("-f", "--project-file", required=True,
              help="BagIt zip file with the project files that will be imported.")
@click.option("-d", "--output-dir", required=True,
              help="Directory where the restored project will be stored.")
@click.option("--checksum-processors", default=1,
              help="Number of processes used to calculate the files checksum during the exporting.")
def project_import(project_file, output_dir, checksum_processors):
    """Import a finalized project to reproduce and explore."""
    from .operations import import_finalized_project

    click.secho("Importing project files...", bold=True)
    info = import_finalized_project(project_file, output_dir, checksum_processors)

    click.secho(f"{info[0]} imported!")
    click.secho(f"The {info[0]} project is available on: {info[1]}")


@project.command(name="show")
@click.option("--graph", required=False, is_flag=True, default=False,
              help="Flag to indicate that the generated graph with the runs should be displayed.")
def project_show(graph: bool):
    """Show project details."""
    project = load_currently_project()

    click.secho("Project details", bold=True)
    click.secho("----------------", bold=True)

    click.secho("Name:", bold=True)
    click.secho(f"    {project.metadata.name}")

    click.secho("Description:", bold=True)
    click.secho(f"    {project.metadata.description}")

    click.secho("Author:", bold=True)
    click.secho(f"    {project.metadata.author}")

    click.secho("Created:", bold=True)
    click.secho(f"    {project.metadata.creation}")

    if graph:
        click.secho("Execution Graph:", bold=True)

        try:
            from .operations import ascii_dag, load_currently_graph
            ascii_dag(load_currently_graph())
        except ModuleNotFoundError:
            click.secho("To visualize the graph it is necessary to install the `asciidag` "
                        "library. To do so, use:")
            click.secho("\t pip install asciidag", bold=True)


@project.command(name="export")
@click.option("-o", "--output-dir", required=True, help="output directory.")
@click.option("--checksum-processors", default=1,
              help="Number of processes used to calculate the files checksum during the exporting.")
def project_export(output_dir, checksum_processors):
    """Export project to a directory."""
    from ..persistence import BagItExporter

    project = load_currently_project()

    # Export all project elements
    BagItExporter.export(project.metadata.name, EnvironmentConfig.REPROPACK_BASE_PATH, output_dir, checksum_processors)


@cli.group(name="execution")
@click.pass_context
def execution(ctx):
    """Execute a project analysis for produce, reproduce or rerun."""
    from ..engine import ExecutionEngine

    if ctx.obj is None:
        ctx.obj = dict()

    project = load_currently_project()
    engine = ExecutionEngine(
        os.getcwd(),
        EnvironmentConfig.REPROPACK_BASE_PATH,
        datasources=project.config.datasources,
        additional_working_directories=project.config.working_directories
    )

    ctx.obj["execution_engine"] = engine
    ctx.obj["actual_project"] = project


@execution.command(name="produce")
@click.argument("command", required=False)
@click.option("--no-check-graph", required=False, is_flag=True, help="Flag to indicate that the validation of the "
                                                                     "graph should not be done. A graph is considered "
                                                                     "valid when no execution node is outdated.")
@click.pass_obj
def produce(obj, command, no_check_graph: bool):
    """Execute commands in a reproducible way."""
    if not command or not command.strip():
        raise click.BadParameter(
            "To produce a reproducible result you need to specify the command that will be used to " +
            "execute your script. \n\tFor example: `bdcrrm-cli execution produce 'python3 script.py'`"
        )

    engine = obj["execution_engine"]

    try:
        engine.execute(command, check_graph_status=not no_check_graph)
    except RuntimeError:
        click.secho("bdcrrm-cli Validation Fail", bold=True)
        click.echo("A new command cannot be executed, there are commands in the execution graph that need to be "
                   "updated. You can update the graph by using the `bdcrrm-cli experiment remake` option or by "
                   "disabling this check with the `--no-check-graph` flag.")


@execution.command(name="remake")
@click.pass_obj
def remake(obj):
    """Execute scripts in a reproducible way."""
    engine = obj["execution_engine"]
    engine.remake()


@execution.command(name="reproduce")
@click.pass_obj
def reproduce(obj):
    """Reproduce analysis results commands group."""
    engine = obj["execution_engine"]
    engine.reproduce()


@execution.group(name="utilities")
def utilities():
    """Utilities commands."""


@utilities.command(name="plot-graph")
@click.option("-f", "--output-file", required=True,
              help="File where the execution graph should be plotted..")
def plot_graph(output_file):
    """Plot the actual execution graph."""
    from ..graph import ExecutionGraphManager, plot_execution_graph
    from ..persistence import GraphPersistencePickle

    g = GraphPersistencePickle.load_graph(EnvironmentConfig.REPROPACK_BASE_PATH)
    graph_manager = ExecutionGraphManager(g)

    plot_execution_graph(graph_manager, output_file, status_colors={
        "outdated": "pink",
        "updated": "blue"
    })
