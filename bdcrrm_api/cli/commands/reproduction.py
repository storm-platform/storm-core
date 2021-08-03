#
# This file is part of Brazil Data Cube Reproducible Research Management CLI.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Command-Line Interface for Reproducible (re)production."""

import json

import click

from .utils import (load_currently_project, load_currently_execution_engine)


@click.group(name="reproduction")
@click.pass_context
def reproduction(ctx):
    """Experiment reproduction commands."""
    if ctx.obj is None:
        ctx.obj = dict()

    project = load_currently_project()
    engine = load_currently_execution_engine()

    ctx.obj["actual_project"] = project
    ctx.obj["execution_engine"] = engine


@reproduction.command(name="make")
@click.option("-i", "--inputs-file", required=False)
@click.option("-s", "--secrets-file", required=False)
@click.pass_obj
def make(obj, inputs_file: str, secrets_file: str):
    """Reproduce a experiment."""
    engine = obj["execution_engine"]

    if inputs_file:
        with open(inputs_file, "r") as ifile:
            inputs_file = json.load(ifile)

    # check secrets
    if secrets_file:
        with open(secrets_file, "r") as ifile:
            secrets_file = [line.strip() for line in ifile.readlines()]

    engine.reproduce(missing_inputs_to_upload=inputs_file, missing_environment_variables=secrets_file)
