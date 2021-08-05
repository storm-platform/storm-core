#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Command-Line Interface for Project inputs management."""

import json

import click

from .utils import load_currently_files
from ..graphics import aesthetic_print
from ..graphics.tables import table_simple


@click.group(name="inputs")
@click.pass_context
def inputs(ctx):
    """Manage the project required inputs for reproduction."""
    if ctx.obj is None:
        ctx.obj = dict()
    ctx.obj["files"] = load_currently_files()


@inputs.command(name="list")
@click.option("--with-checksum", required=False, is_flag=True, default=False,
              help="Flag indicating that in the table of required files, the checksum column should be shown. "
                   "This column contains the checksum of the original data used by the researchers in the "
                   "execution of the project's experiments.")
@click.pass_obj
def inputs_list(obj, with_checksum: bool):
    """Lists the inputs that are required to be defined to reproduce this project."""
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Project inputs", 1)

    files_obj = obj.get("files", None)

    if not files_obj:
        aesthetic_print("[bold red]bdcrrm-cli[/bold red]: No required inputs!", 0)
        return

    # defining columns
    columns = ["Filename"]

    if with_checksum:
        columns.append("Checksum")

    # defining rows
    row_fnc = lambda x: (x[0],)
    if with_checksum:
        row_fnc = lambda x: x  # identity

    checksum = files_obj.get("checksum", {})
    rows = list(
        map(
            row_fnc, [
                (file, checksum) for file, checksum in checksum.items()
            ]
        )
    )

    aesthetic_print(
        table_simple(
            title="Project required input files",
            columns=columns,
            rows=rows
        ), 0
    )


@inputs.command(name="template")
@click.option("-f", "--output-file", required=True,
              help="Full path to the file where the JSON template will be saved.")
@click.option("--with-checksum", required=False, is_flag=True, default=False,
              help="Flag indicating whether the generated template should contain the checksum of the original files"
                   " used. This allows the validation of the entries that will be defined.")
@click.pass_obj
def inputs_template(obj, output_file: str, with_checksum: bool):
    """Create a template file to make it easier for the user to specify the inputs needed to reproduce the work.

    When input files need to be defined, in the experiment reproduction, the user must specify where the data files
    are and how they should be used as input.

    This activity can be time-consuming. To facilitate this activity, `bdcrrm-cli` allows creating a JSON file
    with the information needed for reproduction, checksum, and the right fields that must be defined to inform
    where each of the data files is stored.

    The generated JSON template has two main keys:

     - `files`: Reference to the required files

     - `checksum`: Checksum of the original files used by the researchers in the production of the experiments.

       - In the case of reproduction, this information helps determine whether the inputs are the same as
       those used in the original experiment.

    Some observations:

      1. The `checksum` field is only filled in when the `--with-checksum` flag is specified;

      2. In the `files` field, there are objects with the `source` and `target` fields, which represent:

       - `source`: Name of the original file;

       - `target`: Full path to the file that will be used instead of `source` when the experiment is run.
    """
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Project inputs", 1)

    files_obj = obj.get("files", None)

    if not files_obj:
        aesthetic_print("[bold red]bdcrrm-cli[/bold red]: No inputs inputs are required!", 0)
        return

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Generating a template.", 1)
    if not with_checksum:
        files_obj["checksum"] = []

    with open(output_file, "w") as ofile:
        json.dump(files_obj, ofile)

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Finished!", 0)
