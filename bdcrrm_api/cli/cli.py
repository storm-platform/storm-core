#
# This file is part of Brazil Data Cube Reproducible Research Management CLI.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Command-Line Interface."""

import click

from .commands import project, production, reproduction


@click.group()
@click.version_option()
def bdcrrm_cli():
    """Brazil Data Cube Reproducible Research Management CLI."""


bdcrrm_cli.add_command(project)
bdcrrm_cli.add_command(production)
bdcrrm_cli.add_command(reproduction)
