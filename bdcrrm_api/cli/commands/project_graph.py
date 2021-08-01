#
# This file is part of Brazil Data Cube Reproducible Research Management CLI.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Command-Line Interface for Project graph management."""

import click

from .utils import load_currently_execution_engine, check_if_execution_command_is_valid
from ..graphics.graph import show_ascii_execution_graph


@click.group(name="graph")
@click.pass_context
def graph(ctx):
    """Graph commands."""
    if ctx.obj is None:
        ctx.obj = dict()

    ctx.obj["execution_engine"] = load_currently_execution_engine()


@graph.command(name="show")
@click.pass_obj
def project_graph_show(obj):
    """Show the project execution graph."""
    execution_engine = obj["execution_engine"]
    execution_graph = execution_engine.graph_manager

    if not execution_graph.is_empty:
        click.secho("Execution Graph:", bold=True)
        show_ascii_execution_graph(execution_graph.graph)

    # from .graphics import show_table_execution_graph_status
    # engine: ExecutionEngine = obj["execution_engine"]
    # show_table_execution_graph_status(engine._graph_manager.to_frame())


@graph.command(name="plot")
@click.option("-f", "--output-file", required=True,
              help="File where the execution graph should be plotted..")
@click.pass_obj
def project_graph_plot(obj, output_file):
    """Plot the project execution graph on a file."""
    from ...graph import plot_execution_graph

    execution_engine = obj["execution_engine"]
    execution_graph = execution_engine.graph_manager

    plot_execution_graph(execution_graph, output_file, status_colors={
        "outdated": "pink",
        "updated": "blue",
        "invalid": "red"
    })


@graph.command(name="delete-vertex")
@click.argument("command", required=False)
@click.option("--include-neighbors", required=False, is_flag=True, help="Flag to indicate that the validation of the "
                                                                        "graph should not be done. A graph is "
                                                                        "considered valid when no execution node is "
                                                                        "outdated.")
@click.pass_obj
def project_delete_execution_graph_vertex(obj, command: str, include_neighbors: bool = False):
    """Deletes the vertex from the execution graph that is bound to the specified `COMMAND`.

    Example:
        To remove a graph vertex of the command `python3 myscript.sh`, you can do the following:
            `bdcrrm-cli project graph delete-vertex `python3 myscript.sh`
    """
    check_if_execution_command_is_valid(command)
    engine = obj["execution_engine"]

    engine.delete_execution(command, include_neighbors)
