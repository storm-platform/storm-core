#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management API is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Command-Line Interface."""

import click

from .commands import production, project, reproduction


@click.group()
@click.version_option()
def bdcrrm_cli():
    """Brazil Data Cube Reproducible Research Management CLI."""


bdcrrm_cli.add_command(project)
bdcrrm_cli.add_command(production)
bdcrrm_cli.add_command(reproduction)
