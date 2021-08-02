#
# This file is part of Brazil Data Cube Reproducible Research Management CLI.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Command-Line Interface Graphics."""

from time import sleep
from typing import Any

from rich.console import Console


def aesthetic_print(message: Any, wait_time: int = 1, **kwargs):
    """Create aesthetic prints.

    The function takes objects from the rich library and renders them on the terminal with the `rich.console.Console`.
    Args:
        message (Any): Message (with style) that will be presented.

        wait_time (int): Waiting time before unlock the terminal.

        kwargs (dict): rich.console.Console extra parameters.
    Returns:
        None: The messages will show on the terminal.
    """

    console = Console(**kwargs)

    console.print(message)
    sleep(wait_time)
