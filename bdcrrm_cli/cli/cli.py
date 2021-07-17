#
# This file is part of Brazil Data Cube Reproducible Research Management CLI.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Command-Line Interface."""

import os

import click
from datetime import datetime

from .operations import load_project
from ..config import EnvironmentConfig


TEMPLATE_REPOSITORY = "https://github.com/M3nin0/bdcrrm-project-cookiecutter"


@click.group()
@click.version_option()
def cli():
    """Brazil Data Cube Reproducible Research Management CLI"""


@cli.command(name = "init")
def init():
    """Initialize a project"""
    from cookiecutter.main import cookiecutter

    cookiecutter(TEMPLATE_REPOSITORY, extra_context={
        "timestamp": datetime.utcnow().isoformat()
    })


@cli.group(name = "project")
@click.pass_context
def project(ctx):
    """Project commands group"""
    
    if ctx.obj is None:
        ctx.obj = dict()

    ctx.obj["actual_project"] = load_project()


@project.command(name = "show")
@click.pass_obj
def project_show(obj):
    """Show project details"""

    project = obj["actual_project"]

    click.secho("Project details", bold = True)
    click.secho("----------------", bold = True)
    
    click.secho("Name:", bold = True)
    click.secho(f"    {project.metadata.name}")

    click.secho("Description:", bold = True)
    click.secho(f"    {project.metadata.description}")

    click.secho("Author:", bold = True)
    click.secho(f"    {project.metadata.author}")

    click.secho("Created:", bold = True)
    click.secho(f"    {project.metadata.creation}")


@project.command(name = "export")
@click.option("-o", "--output-dir", required=True, help="output directory.")
@click.option("--checksum-processors", default=1,
              help="Number of processes used to calculate the files checksum during the exporting.")
def project_export(output_dir, checksum_processors):
    """Export project to a directory"""
    from ..persistence import BagItExporter

    project = load_project()

    # Export all project elements
    BagItExporter.export(project.metadata.name, EnvironmentConfig.REPROPACK_BASE_PATH, output_dir, checksum_processors)

@cli.group(name = "execution")
@click.pass_context
def execution(ctx):
    """Execution commands to produce or reproduce a project analysis."""
    from ..engine import ExecutionEngine

    if ctx.obj is None:
        ctx.obj = dict()

    engine = ExecutionEngine(
        os.getcwd(), EnvironmentConfig.REPROPACK_BASE_PATH
    )

    ctx.obj["execution_engine"] = engine
    ctx.obj["actual_project"] = load_project()


@execution.command(name = "produce")
@click.argument("command", required=False)
@click.pass_obj
def produce(obj, command):
    """Execute scripts in a reproducible way."""

    if not command:
        raise click.BadParameter(
            "To produce a reproducible result you need to specify the command that will be used to " +
            "execute your script. \n\tFor example: `bdcrrm-cli execution produce 'python3 script.py'`"
        )
    
    engine = obj["execution_engine"]
    engine.execute(command)


@execution.command(name = "remake")
@click.pass_obj
def produce(obj):
    """Execute scripts in a reproducible way."""
    
    engine = obj["execution_engine"]
    engine.remake()


@execution.command(name = "reproduce")
@click.pass_obj
def reproduce(obj):
    """Reproduce analysis results commands group"""

    raise NotImplementedError("Operation not implemented yet")


@execution.group(name = "utilities")
def utilities():
    """Execution utilities commands."""


@utilities.command(name = "plot-graph")
@click.option("-f", "--output-file", required=True, 
            help="File where the execution graph should be plotted..")
@click.pass_obj
def plot_graph(obj, output_file):
    """Plot the actual execution graph."""
    from ..graph import plot_execution_graph

    from ..graph import ExecutionGraphManager
    from ..persistence import GraphPersistencePickle

    g = GraphPersistencePickle.load_graph(EnvironmentConfig.REPROPACK_BASE_PATH)
    graph_manager = ExecutionGraphManager(g)

    engine = obj["execution_engine"]

    plot_execution_graph(graph_manager, output_file, status_colors={
        "outdated": "pink",
        "updated": "blue"
    })
