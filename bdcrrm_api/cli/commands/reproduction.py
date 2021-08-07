#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management API is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Command-Line Interface for Reproducible (re)production."""

import json

import click
import rich.markdown

from ..graphics import aesthetic_print
from .utils import load_currently_execution_engine, load_currently_project


@click.group(name="reproduction")
@click.pass_context
def reproduction(ctx):
    """Experiment reproduction."""
    if ctx.obj is None:
        ctx.obj = dict()

    project = load_currently_project()
    engine = load_currently_execution_engine()

    ctx.obj["actual_project"] = project
    ctx.obj["execution_engine"] = engine


@reproduction.command(name="make")
@click.option("-i", "--inputs-file", required=False, help="To reproduce a project, it may be necessary to define "
                                                          "the input files used in its various stages. In `bdcrrm-cli`,"
                                                          "all the required inputs are mapped into a JSON file through "
                                                          "the `bdcrrm-cli project inputs template` command. Here the "
                                                          "format of the JSON document expected by the tool is "
                                                          "determined, and the name of each file must be defined "
                                                          "for reproduction. This parameter must specify the full "
                                                          "path to this JSON file populated.")
@click.option("-s", "--secrets-file", required=False, help="If the project requires the definition of secrets, use this"
                                                           " parameter to determine the complete path to the file that "
                                                           "defines the needed secrets' values. A template file (secre"
                                                           "ts) with all required secrets is generated when the project"
                                                           " is imported. Also, if you want to know what secrets are "
                                                           "used in the project, use the "
                                                           "`bdcrrm-cli project settings secrets list` command.")
@click.option("-m", "--processors", required=False, default=1, help="The number of processes used for project "
                                                                    "reproduction. When this parameter is greater"
                                                                    " than 1, operations are parallelized, and "
                                                                    "more than one step of the execution graph is "
                                                                    "executed simultaneously.")
@click.pass_obj
def make(obj, inputs_file: str, secrets_file: str, processors: int):
    """Reproduce a project."""
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Project reproduction.", 1)
    engine = obj["execution_engine"]

    if processors <= 0:
        aesthetic_print("[bold red]bdcrrm-cli[/bold red]: Problems founded.")
        aesthetic_print(rich.markdown.Markdown("Invalid input! The number of `processors` must be "
                                               "greater than or equal to one."))
        return

    if inputs_file:
        aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Loading required input files.", 0)

        with open(inputs_file, "r") as ifile:
            inputs_file = json.load(ifile)

    # check secrets
    if secrets_file:
        aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Loading required secrets.", 0)

        with open(secrets_file, "r") as ifile:
            secrets_file = [line.strip() for line in ifile.readlines()]

    # reproducing
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Reproducing the project.", 0)
    engine.reproduce(
        processors=processors,
        missing_inputs_to_upload=inputs_file,
        missing_environment_variables=secrets_file,
        processor_mode="single" if processors == 1 else "multiple"
    )

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Finished!", 0)
