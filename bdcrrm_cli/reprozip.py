#
# This file is part of Brazil Data Cube Reproducible Research Management CLI.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Reprozip Wrapper."""

from bdcrrm_cli.config import EnvironmentConfig
import os
import yaml

import uuid
from typing import Dict, List

from rpaths import Path

from reprozip.pack import pack
from reprozip.tracer import trace
from reprounzip.common import RPZPack


def _generate_uuid() -> str:
    """Generate a valid UUID4"""

    return str(uuid.uuid4())


def _extract_execution_input_by_working_dir(reprozip_execution_config: Dict, working_directories: List[str]) -> List[Dict]:
    """Extract the execution input by working directory.

    This function filters the input files defined by ReproZip.
    Args:
        reprozip_execution_config (Dict): The ReproZip execution metadata (`config.yml`) dict object.

        working_directories (List[str]): The working directories used to filter the execution input.
    
    Returns:
        List[Dict]: The execution input files filtered by working directory.
    
    Note:
        The filter is done based on `working_directories`. Therefore, all files inside these directories are considered. 
        This heuristic is used to prevent invalid files (e.g., binaries, system libraries) from being used as "input data".
    """
    inputs = []
    for working_directory in working_directories:
        for input_output_file in reprozip_execution_config["inputs_outputs"]:

            if working_directory in input_output_file["path"]:            
                # verify if file is a input (written by nobody - ReproZip heuristic)
                if len(input_output_file["written_by_runs"]) == 0:
                    inputs.append(input_output_file)
    return inputs


def _extract_execution_output(reprozip_execution_config: Dict) -> List[Dict]:
    """Extract the execution output by working directory.

    Args:
        reprozip_execution_config (Dict): The ReproZip execution metadata (`config.yml`) dict object.
    
    Returns:
        List[Dict]: The execution output files.
    """
    outputs = []
    for input_output_file in reprozip_execution_config["inputs_outputs"]:
        if len(input_output_file["written_by_runs"]) != 0:
            outputs.append(input_output_file)
    return outputs


def _extract_command(reprozip_execution_config: Dict) -> List[str]:
    """Extract the execution command.

    Args:
        reprozip_execution_config (Dict): The ReproZip execution metadata (`config.yml`) dict object.
    
    Returns:
        List[str]: The execution command.
    """

    # in bdcrrm, the reprozip execution strategy always generate a unique execution per command
    return reprozip_execution_config["runs"][0]["argv"]


def reprozip_execution_metadata(repropack_directory: str, working_directories: List[str]):
    """Extract the execution metadata from a ReproZip pack.

    Args:
        repropack_directory: The directory where the ReproZip execution files is saved.

        working_directories (List[str]): The working directories used to filter the execution input.
    
    Returns:
        Dict: The execution metadata with the following fields:
            - `repropack`: The path to the ReproZip Pack file;
            - `command`: The execution command;
            - `inputs`: The execution input files;
            - `outputs`: The execution output files;
    """

    # ToDo: Maybe this filter function is temporary. In the future, the complete object will be used.
    def _extract_path(input_output_config: str):
        """Extract only `path` key from input/output ReproZip directory."""

        return list(
            map(
                lambda obj: obj["path"], input_output_config
            )
        )

    pack_path = os.path.join(repropack_directory, "pack.rpz")
    reprozip_execution_config = yaml.load(RPZPack(pack_path).open_config(), Loader=yaml.Loader)
    
    return {
        "repropack": pack_path,
        "command": _extract_command(reprozip_execution_config),
        "inputs": _extract_path(
            _extract_execution_input_by_working_dir(reprozip_execution_config, working_directories)   
        ),
        "outputs": _extract_path(
            _extract_execution_output(reprozip_execution_config)
        )
    }


def reprozip_execute_script(reprofiles_directory: str, binary_command: str, arguments: List[str], verbosity: str = "unset") -> str:
    """Execute a script using ReproZip engine.

    Args:
        reprofiles_directory: The directory where the `bdcrrm` files will be saved.

        binary_command (str): The binary command to execute the script.

        arguments (List[str]): The arguments to pass to the `binary_command`.

        verbosity (str): The verbosity level to use.

    Returns:
        str: The `repropack` directory where ReproZip trace saves the execution files.
    """

    repropack_directory = os.path.join(reprofiles_directory, EnvironmentConfig.REPROPACK_EXEC_PATH, _generate_uuid())
    os.makedirs(repropack_directory)

    # tracing the execution!
    reprozip_status = trace.trace(binary_command, arguments, repropack_directory, False, verbosity)

    # write reprozip configuration file
    trace.write_configuration(Path(repropack_directory), True, True, overwrite=False)

    # pack!
    repropack_pack_directory = os.path.join(repropack_directory, "pack.rpz")
    pack(Path(repropack_pack_directory), Path(repropack_directory), True)

    return repropack_directory


__all__ = (
    "reprozip_execute_script",
    "reprozip_execution_metadata"
)
