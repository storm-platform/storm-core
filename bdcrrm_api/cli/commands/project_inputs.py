#
# This file is part of Brazil Data Cube Reproducible Research Management CLI.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Command-Line Interface for Project inputs management."""

import json

import click

from .utils import load_currently_files


@click.group(name="inputs")
@click.pass_context
def inputs(ctx):
    """Check the experiment required inputs."""
    if ctx.obj is None:
        ctx.obj = dict()
    ctx.obj["files"] = load_currently_files()


@inputs.command(name="list")
@click.pass_obj
def inputs_list(obj):
    """Lists the inputs that are required to be supplied for the reproduction project."""
    files = obj.get("files", [])

    for file in files["files"]:
        print(file["source"])


@inputs.command(name="template")
@click.option("-f", "--output-file", required=True, help="File where the template file will be saved.")
@click.option("--with-checksum", required=False, is_flag=True, default=False,
              help="Flag indicating whether the generated template should contain the checksum of the original files"
                   " used. This allows the validation of the entries that will be defined.")
@click.pass_obj
def inputs_template(obj, output_file: str, with_checksum: bool):
    """Lists the inputs that are required to be supplied for the reproduction project."""
    files = obj["files"]

    print("Generating a template")
    if not with_checksum:
        files["checksum"] = []

    with open(output_file, "w") as ofile:
        json.dump(files, ofile)
