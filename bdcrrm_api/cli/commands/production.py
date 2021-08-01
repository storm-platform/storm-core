#
# This file is part of Brazil Data Cube Reproducible Research Management CLI.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Command-Line Interface for Reproducible production."""

import click

from .utils import (load_currently_project, load_currently_execution_engine, check_if_execution_command_is_valid)


@click.group(name="production")
@click.pass_context
def production(ctx):
    """Reproducible experiment execution commands."""
    if ctx.obj is None:
        ctx.obj = dict()

    project = load_currently_project()
    engine = load_currently_execution_engine()

    ctx.obj["execution_engine"] = engine
    ctx.obj["actual_project"] = project


@production.command(name="make")
@click.argument("command", required=False)
@click.option("--no-check-graph", required=False, is_flag=True, help="Flag to indicate that the validation of the "
                                                                     "graph should not be done. A graph is considered "
                                                                     "valid when no execution node is outdated.")
@click.pass_obj
def make(obj, command, no_check_graph: bool):
    """Execute commands in a reproducible way."""
    check_if_execution_command_is_valid(command)
    engine = obj["execution_engine"]

    try:
        engine.execute(command, check_graph_status=not no_check_graph)
    except RuntimeError:
        click.secho("bdcrrm-cli Validation Fail", bold=True)
        click.echo("A new command cannot be executed, there are commands in the execution graph that need to be "
                   "updated. You can update the graph by using the `bdcrrm-cli production remake` option or by "
                   "disabling this check with the `--no-check-graph` flag.")


@production.command(name="remake")
@click.pass_obj
def remake(obj):
    """(Re)Execute registered commands in a reproducible way."""
    engine = obj["execution_engine"]
    engine.remake()
