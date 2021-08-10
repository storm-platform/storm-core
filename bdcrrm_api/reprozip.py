#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management API is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Reprozip Wrapper."""

import fnmatch
import os
import uuid
from typing import Dict, List, Tuple

import plumbum
from reprounzip.common import RPZPack
from reprozip.pack import pack
from reprozip.tracer import trace
from rpaths import Path
from ruamel.yaml import YAML

from .config import EnvironmentConfig


def _generate_uuid() -> str:
    """Generate a valid UUID4."""
    return str(uuid.uuid4())


def _filter_none_values(values: List) -> List:
    """Remove none values from an list of values.

    Args:
        values (List): List of values
    Returns:
        List: Filtered list
    """
    return list(
        filter(
            lambda x: x is not None, values
        )
    )


def _load_reprozip_config_file(repropack_directory: str) -> Dict:
    """Load the Reprozip configuration file.

    Args:
        repropack_directory (str): The directory where the ReproZip execution files is saved.

    Returns:
        Dict: Dictionary object with data loaded from configuration file.
    """
    config_file = os.path.join(repropack_directory, "config.yml")
    return YAML().load(open(config_file))


def _save_reprozip_config_file(repropack_directory: str, config_obj: Dict) -> str:
    """Save a Reprozip configuration file.

    Args:
        repropack_directory (str): The directory where the ReproZip execution files is saved.

        config_obj (Dict): Dictionary object with data that should be added on the configuration file.

    Returns:
        None: The configuration file will be updated in-place.
    """
    config_file = os.path.join(repropack_directory, "config.yml")

    with open(config_file, "w") as f:
        YAML().dump(config_obj, f)
    return config_file


def _exclude_execution_input_files_by_already_generated_files(reprozip_execution_config: Dict,
                                                              already_generated_files: List[str]) -> Tuple[Dict, List]:
    """Remove files/directories from the configuration file based on already generated files.

    In the bdcrrm-api the reprozip is being used as a basis for script execution. The outputs are
    inserted into the graph and used for the connection operations of each of these. To prevent a
    file that is generated in a previous step of the execution from being included in the package,
    this function filters and removes from the configuration file, all entries that are already
    generated in previous steps.

    Args:
        reprozip_execution_config (Dict): The ReproZip execution metadata (`config.yml`) dict object.

        already_generated_files (List[str]): Files that already is generated by previous graph execution steps.

    Returns:
        Dict: The ReproZip execution metadata (`config.yml`) dict object filtered by already generated files.

    Note:
        The filtering is done in the `other_files` section of the ReproZip configuration file. Thus, the reference to
        which input data should be used is still kept in the file.
    """
    excluded_files = []
    for already_generated_file in already_generated_files:
        for idx, other_file in enumerate(reprozip_execution_config["other_files"]):

            # ToDo: Do this verification by a checksum.
            if already_generated_file == other_file:
                excluded_files.append(
                    reprozip_execution_config["other_files"][idx]
                )
                reprozip_execution_config["other_files"][idx] = None

    # remove all "None" values
    reprozip_execution_config["other_files"] = _filter_none_values(reprozip_execution_config["other_files"])
    return reprozip_execution_config, excluded_files


def _exclude_execution_input_files_by_datasources(reprozip_execution_config: Dict,
                                                  datasources: Dict[str, str]) -> Tuple[Dict, List]:
    """Remove files/directories from the configuration file based on `datasources` definitions.

    Using the files in the `other_files` section of the ReproZip configuration file as a basis,
    for all data that is below the directories defined as datasources, the removal is done if
    the user has determined this way.

    Args:
        reprozip_execution_config (Dict): The ReproZip execution metadata (`config.yml`) dict object.

        datasources (List[Dict[str, str]]): The datasources definitions. This definition is a dictionary in
        which each key is the name of a datasource. The content associated with each key is a dictionary
        with `pattern` and `action` fields. These respectively indicate the path to the data pattern
        (Unix Name patterns interpreted by `fnmatch`) and the action to be taken (`exclude` or `include`). If the
        action is `exclude`, the directory is not included in the generated Repropack. An example of `datasource` is:

            {
                "datasource1": {
                    "pattern": "/path/to/datasource1/*.txt",
                    "action": "exclude"
                }
            }

    Returns:
        Dict: The ReproZip execution metadata (`config.yml`) dict object filtered by the `datasources` definitions.

    Note:
        The `other_files` section of the reprozip configuration file (config.yaml) is used because it
        contains the information about files/directories that are not attached to any OS package.
        Thus data files are kept in this section.

    See:
        https://docs.python.org/pt-br/3/library/fnmatch.html
    """
    excluded_files = []
    for datasource_key in datasources.keys():
        datasource = datasources[datasource_key]

        for idx, other_file in enumerate(reprozip_execution_config["other_files"]):
            if fnmatch.fnmatch(other_file, datasource["pattern"]):
                if datasource["action"] == "exclude":
                    excluded_files.append(
                        reprozip_execution_config["other_files"][idx]
                    )
                    reprozip_execution_config["other_files"][idx] = None

    # remove all "None" values
    reprozip_execution_config["other_files"] = _filter_none_values(reprozip_execution_config["other_files"])
    return reprozip_execution_config, excluded_files


def _extract_execution_input_by_working_dir(reprozip_execution_config: Dict,
                                            working_directories: List[str]) -> List[Dict]:
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
    if not reprozip_execution_config["inputs_outputs"]:
        return []

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
    if not reprozip_execution_config["inputs_outputs"]:
        return []

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


def _remove_command_from_input(command: List[str], input_files: List[str]) -> List[str]:
    """Remove the executed script from the variables considered as input.

    Args:
        command (List[str]): The execution command.

        input_files: The execution input files filtered by working directory.

    Returns:
        List[Dict]: The execution input files filtered without command (as soon as possible).
    """
    return [x for x in input_files if all(os.path.basename(x) not in c for c in command)]


def filter_reprozip_config_files(repropack_directory: str, datasources: dict,
                                 already_generated_files: List[str]) -> Dict[str, List]:
    """Delete configuration file contents from the execution performed by ReproZip.

    Checks all identified files and excludes those that fit one or more of the patterns listed below:
        - 1. It is an input file generated by a previous step that is already in the graph. This heuristic uses the
             maxim that for reproducibility, only the code and the input data are sufficient to obtain the
             same results.

        - 2. File is contained in the directory, pattern or file declared as `exclude`.

    Args:
        repropack_directory: The directory where the ReproZip execution files is saved.

        datasources (List[Dict[str, str]]): The datasources definitions. This definition is a dictionary in
        which each key is the name of a datasource. The content associated with each key is a dictionary
        with `pattern` and `action` fields. These respectively indicate the path to the data pattern
        (Unix Name patterns interpreted by `fnmatch`) and the action to be taken (`exclude` or `include`). If the
        action is `exclude`, the directory is not included in the generated Repropack. An example of `datasource` is:

            {
                "datasource1": {
                    "pattern": "/path/to/datasource1/*.txt",
                    "action": "exclude"
                }
            }

        already_generated_files (List[str]): Files that already is generated by previous graph execution steps.

    Returns:
        Dict: A dictionary with the reference of the files is removed, separated by the used filter method. Each key in
        the dictionary represents the method used to remove the file (`graph` or `datasource`). For the graph method,
        the deletion is done when the file of the same name is generated as output from some vertex. In contrast
        to this, it removes files listed in the data sources in the data source method.

    Note:
        The filter modifications is saved in the ReproZip execution metadata (`config.yml`) file.

    See:
        https://docs.python.org/pt-br/3/library/fnmatch.html
    """
    reprozip_execution_config = _load_reprozip_config_file(repropack_directory)

    # exclude files that are already generated into the execution graph.
    excluded_files_from_graph = []
    if already_generated_files:
        reprozip_execution_config, excluded_files_from_graph = (
            _exclude_execution_input_files_by_already_generated_files(
                reprozip_execution_config, already_generated_files
            )
        )

    # exclude files that are defined as datasources.
    excluded_files_from_datasources = []
    if datasources:
        reprozip_execution_config, excluded_files_from_datasources = _exclude_execution_input_files_by_datasources(
            reprozip_execution_config, datasources
        )

    # write the new config file
    _save_reprozip_config_file(repropack_directory, reprozip_execution_config)

    return {
        "graph": excluded_files_from_graph,
        "datasources": excluded_files_from_datasources
    }


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
    def _extract_path(input_output_config: List[Dict]) -> List[str]:
        """Extract only `path` key from input/output ReproZip directory.

        Args:
            input_output_config (List[Dict]): List of dict with the input/output references.

        Returns:
            List[str]: List of str with the content of `path` key of each object into `input_output_config`.
        """
        return list(
            map(
                lambda obj: obj["path"], input_output_config
            )
        )

    pack_path = os.path.join(repropack_directory, "pack.rpz")
    reprozip_execution_config = YAML().load(RPZPack(pack_path).open_config())

    # extract values
    command = _extract_command(reprozip_execution_config)

    # in the case of input, the script is also removed
    inputs = _remove_command_from_input(
        command,
        _extract_path(
            _extract_execution_input_by_working_dir(reprozip_execution_config, working_directories)
        )
    )

    outputs = _extract_path(
        _extract_execution_output(reprozip_execution_config)
    )

    return {
        "repropack": pack_path,
        "command": command,
        "inputs": inputs,
        "outputs": outputs
    }


def reprozip_remove_environment_variables(repropack_directory: str, environment_variables: List[str]):
    """Remove environment variables from a reprozip execution environment.

    Args:
        repropack_directory (str): The directory where the ReproZip execution files is saved.

        environment_variables (List[str]): List of environment variables that should be removed from the
                                           experiment environment.
    Returns:
        None: The environment variables will be removed from the reprozip configuration file in-place.
    """
    reprozip_execution_config = _load_reprozip_config_file(repropack_directory)

    # go through runs
    for idx, run in enumerate(reprozip_execution_config["runs"]):
        for environment_variable in environment_variables:
            if environment_variable in run["environ"]:
                reprozip_execution_config["runs"][idx]["environ"][environment_variable] = None

    _save_reprozip_config_file(repropack_directory, reprozip_execution_config)


def reprozip_execute_script(reprofiles_directory: str, binary_command: str, arguments: Tuple[str],
                            verbosity: str = "unset") -> str:
    """Execute a script using ReproZip engine.

    Args:
        reprofiles_directory (str): The directory where the `bdcrrm` files will be saved.

        binary_command (str): The binary command to execute the script.

        arguments (Tuple[str]): The arguments to pass to the `binary_command`.

        verbosity (str): The verbosity level to use.

    Returns:
        str: The `repropack` directory where ReproZip trace saves the execution files.
    """
    repropack_directory = os.path.join(reprofiles_directory, EnvironmentConfig.REPROPACK_EXEC_PATH, _generate_uuid())
    os.makedirs(repropack_directory)

    # tracing the execution!
    trace.trace(binary_command, arguments, repropack_directory, False, verbosity)

    # write reprozip configuration file
    trace.write_configuration(Path(repropack_directory), True, True, overwrite=False)

    return repropack_directory


def reprozip_pack_execution(repropack_directory: str) -> str:
    """Create a ReproZip package for an experiment.

    Retrieves the execution information stored in `repropack_directory` and generates the package. If needed the files
    can be filtered using the `bdcrrm_cli.repropzip.filter_reprozip_config_files` function.

    Args:
        repropack_directory (str): The directory where the ReproZip execution files is saved.

    Returns:
        str: Directory where the reprozip package is saved.
    """
    repropack_pack_directory = os.path.join(repropack_directory, "pack.rpz")
    pack(Path(repropack_pack_directory), Path(repropack_directory), True)

    return repropack_pack_directory


def reprounzip_add_environment_variables(repropack_directory: str, environment_variables: List[str]):
    """Add environment variables to a reprounzip environment.

    Args:
        repropack_directory (str): The directory where the ReproZip execution files is saved.

        environment_variables (List[str]): List of environment variables that should be added on the
                                           experiment environment before reproduction.

    Returns:
        None: The environment variables will be added to reprozip configuration file in-place.
    """
    reprozip_execution_config = _load_reprozip_config_file(repropack_directory)

    # prepare the environment variables
    reprozip_environment_variables = []
    for environment_variable in environment_variables:
        # it is assumed that the first value on the left is the
        # variable name and the rest of the elements their respective value
        envvar_definition = environment_variable.split("=")

        # validating
        # If not equal to or greater than 2, it is assumed that the string cannot
        # be split, indicating that the environment variable has not been set correctly.
        if len(envvar_definition) < 2:
            raise RuntimeError("Cannot identify the name and value of the defined environment variable! "
                               "Ensure that the environment variable definition follows the pattern NAME=VALUE, "
                               "where the `=` symbol separates name and value.")

        # prepare the variables
        env_name = envvar_definition[0]
        env_value = "".join(envvar_definition[1:]).replace("'", '').strip()

        reprozip_environment_variables.append((env_name, env_value))

    # go through runs
    for idx, run in enumerate(reprozip_execution_config["runs"]):
        for environment_variable in reprozip_environment_variables:
            env_name, env_value = environment_variable

            reprozip_execution_config["runs"][idx]["environ"][env_name] = env_value
    _save_reprozip_config_file(repropack_directory, reprozip_execution_config)


def reprounzip_setup(repropack_path: str, reproduction_path: str, unpacker: str = "docker"):
    """Configure the directories and data needed to run an experiment through Reprounip.

    Args:
        repropack_path (str): Path to the `.rpz` file.

        reproduction_path (str): Path where the data will be extracted.

        unpacker (str): Used Reprounip unpacker.
    See:
        https://docs.reprozip.org/en/1.0.x/unpacking.html
    """
    (
        plumbum.cmd.reprounzip[
            unpacker, "setup", repropack_path, reproduction_path
        ]
    )()


def reprounzip_upload(reproduction_path: str, source_file_path: str, target_file_name: str, unpacker: str = "docker"):
    """Upload a input file to a reprounzip experiment.

    Args:
        reproduction_path (str): Path where the reprounzip experiment is stored.

        source_file_path (str): relative or absolute path to the file that will be uploaded.

        target_file_name (str): name of the file that the `source_file_path` will be replace.

        unpacker (str): Used Reprounip unpacker.
    See:
        https://docs.reprozip.org/en/1.0.x/unpacking.html
    """
    (
        plumbum.cmd.reprounzip[
            unpacker, "upload", reproduction_path, f"{source_file_path}:{target_file_name}"
        ]
    )()


def reprounzip_download_all(reproduction_path: str, unpacker: str = "docker"):
    """Download all reprounzip experiment result on the current directory.

    Args:
        reproduction_path (str): Path where the reprounzip experiment is stored.

        unpacker (str): Used Reprounip unpacker.
    See:
        https://docs.reprozip.org/en/1.0.x/unpacking.html
    """
    (
        plumbum.cmd.reprounzip[
            unpacker, "download", reproduction_path, "--all"
        ]
    )()


def reprounzip_run(reproduction_path: str, unpacker: str = "docker"):
    """Execute a reprounzip experiment.

    Args:
        reproduction_path (str): Path where the reprounzip experiment is stored.

        unpacker (str): Used Reprounip unpacker.
    See:
        https://docs.reprozip.org/en/1.0.x/unpacking.html
    """
    (
        plumbum.cmd.reprounzip[
            unpacker, "run", reproduction_path
        ]
    )()


__all__ = (
    "filter_reprozip_config_files",

    "reprozip_execute_script",
    "reprozip_pack_execution",
    "reprozip_execution_metadata",
    "reprozip_remove_environment_variables",

    "reprounzip_setup",
    "reprounzip_upload",
    "reprounzip_download_all",
    "reprounzip_run",
    "reprounzip_add_environment_variables"
)
