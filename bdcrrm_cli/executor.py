#
# This file is part of Brazil Data Cube Reproducible Research Management CLI.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Reprozip Wrapper."""

import os

import uuid
from typing import List

from tempfile import mkdtemp

from reprozip.pack import pack
from reprozip.tracer import trace

from .config import EnvironmentConfig


def _generate_uuid() -> str:
    """Generate a valid UUID4"""

    return str(uuid.uuid4())



def repro_execute_script(binary_command: str, arguments: List[str], verbosity: str = "unset") -> str:
    """Execute a script using ReproZip engine.

    Args:
        binary_command (str): The binary command to execute the script.

        arguments (List[str]): The arguments to pass to the `binary_command`.

        verbosity (str): The verbosity level to use.

    Returns:
        str: The `repropack` directory where ReproZip trace saves the execution files.
    """

    repropack_directory = os.path.join(EnvironmentConfig.REPROPACK_BASE_PATH, _generate_uuid())
    repropack_pack_directory = os.path.join(repropack_directory, "pack")
    
    os.makedirs(repropack_pack_directory)

    # tracing the execution!
    reprozip_status = trace.trace(binary_command, arguments, repropack_directory, False, verbosity)


__all__ = (
    "repro_execute_script"
)
