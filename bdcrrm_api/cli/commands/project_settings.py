#
# This file is part of Brazil Data Cube Reproducible Research Management API.
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
    """Update project metadata.

    This command is used to update the metadata of a project. The changes are made using the following syntax.

       bdcrrm-cli project settings metadata-set <PROPERTY_NAME>=<PROPERTY_VALUE>

    Where <PROPERTY_NAME> is the name of the property that will be updated and <PROPERTY_VALUE> the value.
    Currently, in a project the following metadata attributes are available:

         - Project name: `metadata.name`

         - Project Description: `metadata.description`

         - Project Code License: `metadata.licenses.code`

         - Project Code Data: `metadata.licenses.data`

         - Project Code Text: `metadata.licenses.text`

         - Project Author: `metadata.author`

    Thus, if the `metadata.name` property needs to be updated, the following command could be used:

       bdcrrm-cli project settings metadata-set metadata.name='new project name'
    """
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Metadata settings", 1)
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
    """Project working directories.

    By default, `bdcrrm-api` considers as valid project data only those files within the project directory. This
    encourages researchers to centralize their files in one project, allowing the material generated during
    experiments to be shared as a Research Compendium.

        > This facilitates reproducibility and encourages the use of the knowledge generated in a project.

    This is not always easy to do. So in `bdcrrm-cli` it is possible to define other directories that should
    be considered `working directories`. Once defined, `bdcrrm-api` will interpret the other `working directories`
    as valid.

    Note

        When you use directories other than the project directory to store your input and output data, these
        extra directories must be added to the project. Otherwise, `bdcrrm-api` will not consider them as valid input.
    """


@settings_working_directories.command(name="add")
@click.argument("path", required=True)
@click.pass_obj
def settings_working_directories_add(obj, path: str):
    """Add working directories path to the project settings."""
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Working Directories settings", 1)
    path = path.strip()

    project = obj.get("project", None)

    # validating
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Validating input", 1)
    if not os.path.isdir(path) or os.path.isfile(path):
        aesthetic_print("[bold red]bdcrrm-cli[/bold red]: Invalid input! You must use a valid [bold]directory[/bold] "
                        "as input.")
        return

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Updating the values")
    project.config.working_directories = list({*project.config.working_directories, path})

    save_currently_project(project)
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Finished!", 0)


@settings_working_directories.command(name="remove")
@click.argument("path", required=True)
@click.pass_obj
def settings_working_directories_remove(obj, path: str):
    """Remove a given working directory from the project settings."""
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Working Directories settings", 1)
    path = path.strip()

    project = obj.get("project", None)

    # search for the selected working directory
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Searching...", 1)
    new_working_directories = [wd for wd in project.config.working_directories if wd != path]

    # checking if a working directory was founded
    if len(new_working_directories) < len(project.config.working_directories):
        aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Found!", 1)
    else:
        aesthetic_print("[bold red]bdcrrm-cli[/bold red]: Not found! Exiting...", 1)
        return

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Updating the values")
    project.config.working_directories = new_working_directories

    save_currently_project(project)
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Finished!", 0)


@settings_working_directories.command(name="list")
@click.pass_obj
def settings_working_directories_list(obj):
    """List project working directories."""
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Working Directories settings", 1)
    project = obj.get("project", None)

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Listing working directories", 1)
    aesthetic_print(
        tree_one_root_with_children(f"[bold]{project.metadata.name}[/bold]", project.config.working_directories)
    )


@settings.group(name="datasources")
def settings_datasources():
    """Project settings for datasources.

    As with the `working directories`, `bdcrrm-api`, at the time of creating the reproducibility package,
    determines which data files will be saved based on the project directory.

    Sometimes the data used may be in other directories. In order for these to be included in the package,
    it is necessary to add them as `data sources` for the project.

    Note

        Unlike a `working directory`, which is used to determine the inputs/outputs, the `data sources`
        are used to determine which data will be inserted into the replay package, and do not influence
        the definition of the inputs/outputs of the runtime graph.
    """


@settings_datasources.command(name="add")
@click.argument("name", required=True)
@click.option("-a", "--action", required=True,
              help="Action to be performed with the data source. When set to `include`, "
                   "the data is included in the reproducibility package. Otherwise, when "
                   "set to `exclude`, the data source files will not be included "
                   "in the package. In this second case, the user doing the reproduction "
                   "will be responsible for providing the data.")
@click.option("-p", "--pattern", required=True,
              help="The definition of which files will be considered from a data source is based on `fnmatch` library. "
                   "Use this field to determine, taking a directory as a base, the file pattern that should "
                   "be or not be included in the reproducibility package.")
@click.pass_obj
def settings_datasources_add(obj, name: str, action: str, pattern: str):
    """Add a data sources to the project settings."""
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Data Source settings", 1)

    name = name.strip()
    action = action.strip()
    pattern = pattern.strip()

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
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Finished!", 0)


@settings_datasources.command(name="list")
@click.pass_obj
def settings_datasources_list(obj):
    """List project defined data sources."""
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Data Source settings", 1)
    project = obj.get("project", None)

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Listing data sources", 1)
    datasources = project.config.datasources

    # building the table rows (with custom style)
    trows = list(
        map(
            lambda x: (x[0], x[1], f"[red]{x[2]}[/red]" if x[2] == "exclude" else f"[green]{x[2]}[/green]"),
            (
                (name, datasources[name]["pattern"], datasources[name]['action']) for name in datasources.keys()
            )
        )
    )

    aesthetic_print(
        table_simple(
            "[bold]Project data-sources[/bold]", ["Name", "Pattern", "Action"], trows
        )
    )


@settings_datasources.command(name="remove")
@click.argument("name", required=True)
@click.pass_obj
def settings_datasources_remove(obj, name: str):
    """Remove a given project defined data source by name."""
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Data Source settings", 1)

    name = name.strip()
    project = obj.get("project", None)

    # validating
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Validating input", 1)
    if not name or name not in project.config.datasources:
        aesthetic_print("[bold red]bdcrrm-cli[/bold red]: Invalid input! You should define a valid name.")
        return

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Updating the values")
    del project.config.datasources[name]

    save_currently_project(project)
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Finished!", 0)


@settings.group(name="secrets")
def settings_secrets():
    """Project secrets.

    The processing performed in an experiment can sometimes use external services that require some
    authentication. Since the information for authentication is inside the scripts, by the time
    the reproducibility package is generated, this information will also be saved. This causes
    information leakage and security/privacy flaws.

    To prevent these problems from occurring, users can make use of secrets. In `bdcrrm-api`,
    secrets are environment variables that are not saved in the reproducibility package. Instead,
    once defined in the project, the user can use the environment variable, and at the time of
    creating the reproducibility package, these environment variables are checked and removed.

    This mechanism helps ensure privacy and control of user data.

    Note

        When a secret is set, it is assumed that the user that will be reproducing the experiment
        must set them again. For this purpose, facilities are provided in the
        `bdcrrm-cli project import` command, which saves the user from manually manipulating secret
        values and entering them into complex configuration files.
    """


@settings_secrets.command(name="add")
@click.argument("name", required=True)
@click.pass_obj
def settings_secrets_add(obj, name: str):
    """Add a new secret to the project settings."""
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Secrets settings", 1)

    name = name.strip()
    project = obj.get("project", None)

    # validating
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Validating input", 1)
    if not name:
        aesthetic_print("[bold red]bdcrrm-cli[/bold red]: Invalid input! You should define a valid secret name.")
        return

    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Updating the values")
    project.secrets.append(name)

    save_currently_project(project)
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Finished!", 0)


@settings_secrets.command(name="list")
@click.pass_obj
def settings_secrets_list(obj):
    """List project secrets."""
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Secrets settings", 1)

    project = obj.get("project", None)
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Listing secrets", 1)

    aesthetic_print(
        tree_one_root_with_children(f"[bold]Project Secrets[/bold]", project.secrets)
    )


@settings_secrets.command(name="remove")
@click.argument("name", required=True)
@click.pass_obj
def settings_secrets_remove(obj, name: str):
    """Remove a secret from the project settings."""
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Secrets settings", 1)

    name = name.strip()
    project = obj.get("project", None)

    # validating
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Validating input", 1)
    if not name:
        aesthetic_print("[bold red]bdcrrm-cli[/bold red]: Invalid input! You should define a valid "
                        "[bold]secret[/bold] name.")
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
    aesthetic_print("[bold cyan]bdcrrm-cli[/bold cyan]: Finished!", 0)
