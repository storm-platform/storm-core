#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management API is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Command-Line Interface for Reproducible production."""

import click
import rich.markdown

from ..graphics import aesthetic_print
from .utils import (check_if_execution_command_is_valid,
                    load_currently_execution_engine, load_currently_project)


@click.group(name="production")
@click.pass_context
def production(ctx):
    """Reproducible experiment executions."""
    if ctx.obj is None:
        ctx.obj = dict()

    project = load_currently_project()
    engine = load_currently_execution_engine()

    ctx.obj["execution_engine"] = engine
    ctx.obj["actual_project"] = project


@production.command(name="make")
@click.argument("command", required=True, nargs=-1)
@click.option("--no-check-graph", required=False, is_flag=True, help="Flag to indicate that the validation of the "
                                                                     "graph should not be done. A graph is considered "
                                                                     "valid when no execution vertex is outdated.")
@click.pass_obj
def make(obj, command, no_check_graph: bool):
    """Execute an arbitrary command in a reproducible way.

    When the execution is done by the `bdcrrm-api`, all computational components used on the execution will be
    registered transparently. With this, after the execution the experiment can be reproduced without many efforts.

    For example, if you want to run a python script and then play it back, you can use bdcrrm-api to help you.
    To do this, the execution that is normally done like this:

       $ python3 myscript.py

    should look like this:

       $ bdcrrm-api production make "python3 myscript.py"

    The main difference here is that now, the execution is controlled by `bdccrm-api`, which allows you to extract
    information from the execution and save all the elements needed to re-run the project.
    """
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Reproducible execution", 0)

    check_if_execution_command_is_valid(command)
    engine = obj["execution_engine"]

    try:
        engine.execute(list(command), check_graph_status=not no_check_graph)
    except RuntimeError:
        aesthetic_print("[bold red]bdcrrm-cli[/bold red]: Problems founded")
        aesthetic_print(rich.markdown.Markdown("A new command cannot be executed, there are commands in the "
                                               "execution graph that need to be **updated**. You can check the graph "
                                               "status using `bdcrrm-cli graph show --as-table-status`."
                                               "To update the graph you can use the `bdcrrm-cli production remake` "
                                               "command."))


@production.command(name="remake")
@click.pass_obj
def remake(obj):
    """(Re)Execute outdated commands.

    The command `remake` identifies and re-executes all outdated `vertices commands` in the execution graph.
    This option is useful when multiple runs need to be rerun because of changing results from other scripts.

    A vertex command is considered outdated when any of its predecessors have a run performed after its creation.
    For example:

      The execution graph below has three associated commands:

         *(Command 1) -> *(Command 2) -> *(Command 3)

    All are up to date (Imagine). If the vertex `Command 2` is executed again, all its subsequent ones will
    be out of date since they depend on the result generated by this command. Following this rule, in this
    example, the vertex `Command 3` is outdated.

    Using the `remake` command, the out-of-date nodes are automatically identified and re-executed.
    """
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Reproducible (re)execution", 0)

    engine = obj["execution_engine"]
    engine.remake()

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Finished!", 0)
