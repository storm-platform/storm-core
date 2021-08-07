#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management API is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Command-Line Interface for Project graph management."""

import click
import rich.markdown

from ...config import GraphStyleConfig
from ..graphics import aesthetic_print
from ..graphics.graph import show_ascii_execution_graph
from ..graphics.tables import show_table_execution_graph_status
from .utils import (check_if_execution_command_is_valid,
                    load_currently_execution_engine)


@click.group(name="graph")
@click.pass_context
def graph(ctx):
    """Manage the Project Execution Graph."""
    if ctx.obj is None:
        ctx.obj = dict()

    ctx.obj["execution_engine"] = load_currently_execution_engine()


@graph.command(name="show")
@click.option("--as-table-status", required=False, is_flag=True, default=False,
              help="Flag to indicate that the graph should be presented as a table with status of each vertex.")
@click.pass_obj
def project_graph_show(obj, as_table_status):
    """Show the project execution graph."""
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Graph visualization", 1)

    execution_engine = obj["execution_engine"]
    execution_graph = execution_engine.graph_manager

    if not execution_graph.is_empty:
        if as_table_status:
            show_table_execution_graph_status(execution_graph.to_frame())
        else:
            aesthetic_print("[bold]Execution graph[bold]", 0)
            show_ascii_execution_graph(execution_graph.graph)
    else:
        aesthetic_print("Graph empty!", 0)


@graph.command(name="plot")
@click.option("-f", "--output-file", required=True,
              help="File where the execution graph should be plotted..")
@click.pass_obj
def project_graph_plot(obj, output_file):
    """Plot the project execution graph on a file."""
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Graph visualization", 1)

    from ...graph import plot_execution_graph

    execution_engine = obj["execution_engine"]
    execution_graph = execution_engine.graph_manager

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Creating the plot...", 1)
    filename_plot = plot_execution_graph(execution_graph, output_file,
                                         status_colors=GraphStyleConfig.GRAPH_DEFAULT_VERTICES_COLOR)

    if filename_plot:
        aesthetic_print(f"[bold cyan]bdcrrm-cli[/bold cyan]: Plot created on {filename_plot}", 0)
    else:
        aesthetic_print(f"[bold red]bdcrrm-cli[/bold red]: Graph is empty!", 0)

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Finished!", 0)


@graph.command(name="delete-vertex")
@click.argument("command", required=False)
@click.option("--include-neighbors", required=False, is_flag=True, help="By default, the removal only removes the "
                                                                        "vertex with the specified command. When this "
                                                                        "flag is enabled, all neighbors that depended "
                                                                        "on the deleted vertex are also removed.")
@click.pass_obj
def project_delete_execution_graph_vertex(obj, command: str, include_neighbors: bool = False):
    """Delete the vertex from the execution graph that haves the specified `COMMAND`.

    For example, to remove a vertex with the command `python3 myscript.sh` from the graph, you can do the following:
            `bdcrrm-cli project graph delete-vertex `python3 myscript.sh`
    """
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Graph management.", 1)

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Validating the specified command.", 0)
    try:
        check_if_execution_command_is_valid(command)
    except ValueError:
        aesthetic_print("[bold red]bdcrrm-cli[/bold red]: Problems founded.")
        aesthetic_print(rich.markdown.Markdown("Invalid command! You need to specify the command "
                                               "using quotation marks. For example: `'python3 myscript.py'`"))

        return

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Deleting the command vertex.", 0)
    engine = obj["execution_engine"]
    engine.delete_execution(command, include_neighbors)

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Finished!", 0)
