#
# This file is part of Brazil Data Cube Reproducible Research Management CLI.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Command-Line Interface for Project settings."""

import os

import click

from .utils import load_currently_project, save_currently_project
from ..graphics import aesthetic_print
from ..graphics.tables import table_simple
from ..graphics.trees import tree_one_root_with_children


@click.group(name="settings")
@click.pass_context
def settings(ctx):
    """Project Settings."""
    if ctx.obj is None:
        ctx.obj = dict()
    ctx.obj["project"] = load_currently_project()


@settings.command(name="metadata-set")
@click.argument("definition", required=True)
@click.pass_obj
def settings_metadata_set(obj, definition: str):
    """Configure a metadata settings."""
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Metadata settings", 2)
    project = obj.get("project", None)

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Validating input", 1)
    if "=" not in definition:
        aesthetic_print("[bold red]bdcrrm-cli[/bold red]: You need to set attributes of the metadata "
                        "using the command as follows:")
        aesthetic_print("""
            $ bdcrrm-cli project settings metadata-set [bold purple]<PROPERTY_NAME>=<PROPERTY_VALUE>[/bold purple]
        """.strip())

        return

    # get metadata attribute
    attribute, value = definition.replace("'", "").strip().split("=")

    # validating attribute name
    valid_attributes = project.metadata.attributes.by_name.keys()

    if not any(va == attribute.split(".")[0] for va in valid_attributes):
        aesthetic_print("[bold red]bdcrrm-cli[/bold red]: Invalid input! You need to set attributes of the metadata "
                        "using the command as follows:")

        aesthetic_print(tree_one_root_with_children("[bold]Valid Attributes[/bold]", valid_attributes))
        return

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Updating the values")
    # license is a especial, multilevel, case
    if "license" in attribute:
        setattr(project.metadata.license, attribute, value)
    else:
        setattr(project.metadata, attribute, value)

    save_currently_project(project)
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Done!")


@settings.group(name="working-directories")
def settings_working_directories():
    """Project settings for working directories."""


@settings_working_directories.command(name="add")
@click.argument("name", required=True)
@click.pass_obj
def settings_working_directories_add(obj, name: str):
    """Add working directories to the project definition."""
    name = name.strip()

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: working-directories settings", 2)
    project = obj.get("project", None)

    # validating
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Validating input", 1)
    if not os.path.isdir(name) or os.path.isfile(name):
        aesthetic_print("[bold red]bdcrrm-cli[/bold red]: Invalid input! You must use a valid [bold]directory[/bold] "
                        "as input.")
        return

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Updating the values")
    project.config.working_directories = list(set([*project.config.working_directories, name]))

    save_currently_project(project)
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Done!")


@settings_working_directories.command(name="remove")
@click.argument("name", required=True)
@click.pass_obj
def settings_working_directories_remove(obj, name: str):
    """Add working directories to the project definition."""
    name = name.strip()

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: working-directories settings", 2)
    project = obj.get("project", None)

    # search for the selected working directory
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Searching...", 1)
    new_working_directories = [wd for wd in project.config.working_directories if wd != name]

    # checking if a working directory was founded
    if len(new_working_directories) < len(project.config.working_directories):
        aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Found!", 1)
    else:
        aesthetic_print("[bold red]bdcrrm-cli[/bold red]: Not found! Exiting...", 1)
        return

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Updating the values")
    project.config.working_directories = new_working_directories

    save_currently_project(project)
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Done!")


@settings_working_directories.command(name="list")
@click.pass_obj
def settings_working_directories_list(obj):
    """List project working directories."""
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: working-directories settings", 1)
    project = obj.get("project", None)

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Listing working directories", 1)
    aesthetic_print(
        tree_one_root_with_children(f"[bold]{project.metadata.name}[/bold]", project.config.working_directories)
    )


@settings.group(name="datasources")
def settings_datasources():
    """Project settings for datasources."""


@settings_datasources.command(name="add")
@click.argument("name", required=True)
@click.option("--action", required=True)
@click.option("--pattern", required=True)
@click.pass_obj
def settings_datasources_add(obj, name: str, action: str, pattern: str):
    """Add datasources to the project definition."""
    name = name.strip()
    action = action.strip()
    pattern = pattern.strip()

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: datasource settings", 2)
    project = obj.get("project", None)

    # validating
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Validating input", 1)
    if not all([name, action, pattern]):
        aesthetic_print("[bold red]bdcrrm-cli[/bold red]: Invalid input! You should define all values.")
        return

    if action not in {"include", "exclude"}:
        aesthetic_print("[bold red]bdcrrm-cli[/bold red]: Invalid input! You should define a valid action. "
                        "The valid values are:")
        aesthetic_print(
            tree_one_root_with_children(f"[bold]Valid actions [/bold]", [
                " include: To include the data-source", " exclude: To exclude the data-source"
            ])
        )
        return

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Updating the values")
    project.config.datasources[name] = {"pattern": pattern, "action": action}

    save_currently_project(project)
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Done!")


@settings_datasources.command(name="list")
@click.pass_obj
def settings_datasources_list(obj):
    """List project data-sources."""
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: datasource settings", 2)
    project = obj.get("project", None)

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Listing data-sources", 1)
    datasources = project.config.datasources

    aesthetic_print(
        table_simple(
            "[bold]Project data-sources[/bold]",
            ["Name", "Pattern", "Action"],
            list((
                (name, datasources[name]["pattern"], datasources[name]["pattern"]) for name in datasources.keys()
            ))
        )
    )


@settings_datasources.command(name="remove")
@click.argument("name", required=True)
@click.pass_obj
def settings_datasources_remove(obj, name: str):
    """Remove a project datasources."""
    name = name.strip()

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: datasource settings", 2)
    project = obj.get("project", None)

    # validating
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Validating input", 1)
    if not name or name not in project.config.datasources:
        aesthetic_print("[bold red]bdcrrm-cli[/bold red]: Invalid input! You should define a valid name.")
        return

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Updating the values")
    del project.config.datasources[name]

    save_currently_project(project)
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Done!")


@settings.group(name="secrets")
def settings_secrets():
    """Project settings for secrets."""


@settings_secrets.command(name="add")
@click.argument("name", required=True)
@click.pass_obj
def settings_secrets_add(obj, name: str):
    """Add a new secret to the project."""
    name = name.strip()

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: secrets settings", 2)
    project = obj.get("project", None)

    # validating
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Validating input", 1)
    if not name:
        aesthetic_print("[bold red]bdcrrm-cli[/bold red]: Invalid input! You should define a valid secret name.")
        return

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Updating the values")
    project.secrets.append(name)

    save_currently_project(project)
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Done!")


@settings_secrets.command(name="list")
@click.pass_obj
def settings_secrets_list(obj):
    """List project secrets."""
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: secrets settings", 2)
    project = obj.get("project", None)

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Listing secrets", 1)

    aesthetic_print(
        tree_one_root_with_children(f"[bold]Project Secrets[/bold]", project.secrets)
    )


@settings_secrets.command(name="remove")
@click.argument("name", required=True)
@click.pass_obj
def settings_secrets_remove(obj, name: str):
    """Remove a secret to the project."""
    name = name.strip()

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: secrets settings", 2)
    project = obj.get("project", None)

    # validating
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Validating input", 1)
    if not name:
        aesthetic_print("[bold red]bdcrrm-cli[/bold red]: Invalid input! You should define a valid secret name.")
        return

    # search for the selected working directory
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Searching...", 1)
    new_secrets = [s for s in project.secrets if s != name]

    # checking if a working directory was founded
    if len(new_secrets) < len(project.secrets):
        aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Found!", 1)
    else:
        aesthetic_print("[bold red]bdcrrm-cli[/bold red]: Not found! Exiting...", 1)
        return

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Updating the values")
    project.secrets = new_secrets

    save_currently_project(project)
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Done!")
